"""Minimal LLM integration.

Exposes a simple interface:
    - LLM.generate_reply(system_prompt: str, user_text: str) -> str

Backends:
    - DummyLLM: returns a canned interviewer-style response
    - OllamaLLM: calls local Ollama HTTP API (ollama serve)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import subprocess
import shutil
import time
import platform
import stat
import json
import os

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional import at runtime
    requests = None  # type: ignore


class LLM:
    def generate_reply(self, system_prompt: str, user_text: str) -> str:  # pragma: no cover - interface only
        raise NotImplementedError


@dataclass
class DummyLLM(LLM):
    model: str = "dummy"

    def generate_reply(self, system_prompt: str, user_text: str) -> str:
        return (
            "Thanks for your response. Let's begin. Could you briefly walk me through "
            "a recent project relevant to this role and highlight your specific contributions?"
        )


@dataclass
class OllamaLLM(LLM):
    model: str = "llama3"
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    req_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "600"))  # seconds

    def _generate(self, payload: Dict[str, Any]) -> str:
        if requests is None:
            raise RuntimeError("'requests' package not installed; required for Ollama backend")
        url = f"{self.host.rstrip('/')}/api/generate"
        # Prefer streaming to avoid long read timeouts during initial load
        if payload.get("stream", True):
            r = requests.post(url, json=payload, stream=True, timeout=self.req_timeout)
            r.raise_for_status()
            parts: list[str] = []
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except Exception:
                    continue
                if "response" in j and isinstance(j["response"], str):
                    parts.append(j["response"])
            return "".join(parts)
        else:
            r = requests.post(url, json=payload, timeout=self.req_timeout)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and "response" in data:
                return data.get("response", "")
            if isinstance(data, list):
                return "".join(chunk.get("response", "") for chunk in data)
            return ""

    def generate_reply(self, system_prompt: str, user_text: str) -> str:
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_text,
            "stream": True,
            "options": {
                "temperature": 0.7,
            },
        }
        try:
            return self._generate(payload)
        except Exception as e:
            return f"[LLM error: {e}]"


def create_llm(backend: str, model: str, host: Optional[str] = None, timeout_s: Optional[int] = None) -> LLM:
    backend = (backend or "").lower()
    if backend == "ollama":
        return OllamaLLM(
            model=model,
            host=(host or os.getenv("OLLAMA_HOST", "http://localhost:11434")),
            req_timeout=int(timeout_s or os.getenv("OLLAMA_TIMEOUT", "600")),
        )
    return DummyLLM(model="dummy")


# --- Ollama utilities ---

def ollama_is_running(host: Optional[str] = None) -> Tuple[bool, str]:
    """Check if Ollama server is reachable.
    Returns (ok, message).
    """
    h = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    if requests is None:
        return False, "requests not installed"
    try:
        r = requests.get(f"{h}/api/tags", timeout=3)
        r.raise_for_status()
        return True, "Ollama is running"
    except Exception as e:
        return False, str(e)


def ollama_list_models(host: Optional[str] = None) -> List[str]:
    """List installed Ollama models by name (e.g., 'llama3', 'llama3:8b')."""
    h = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    if requests is None:
        return []
    try:
        r = requests.get(f"{h}/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json()
        models = []
        for m in data.get("models", []):
            name = m.get("name")
            if name:
                models.append(name)
        return sorted(models)
    except Exception:
        return []


def ollama_quick_test(model: str, host: Optional[str] = None) -> Tuple[bool, str]:
    """Do a quick non-stream generate to verify model usability."""
    h = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    if requests is None:
        return False, "requests not installed"
    try:
        payload = {
            "model": model,
            "prompt": "Say 'ready'.",
            "stream": False,
        }
        r = requests.post(f"{h}/api/generate", json=payload, timeout=30)
        r.raise_for_status()
        j = r.json()
        ok = isinstance(j, dict) and bool(j.get("response"))
        return ok, (j.get("response", "") or "no response")
    except Exception as e:
        return False, str(e)


def has_ollama_cli(cmd: Optional[str] = None) -> bool:
    """Check if 'ollama' CLI (or provided command path) is on PATH."""
    candidate = (cmd or "ollama").strip()
    if os.path.isabs(candidate) and os.path.exists(candidate):
        return os.access(candidate, os.X_OK)
    return shutil.which(candidate) is not None


def start_ollama_server(cmd: Optional[str] = None) -> Tuple[bool, str, Optional[subprocess.Popen]]:
    """Start 'ollama serve' in the background. Returns (ok, message, process)."""
    ollama_cmd = (cmd or "ollama").strip()
    if not has_ollama_cli(ollama_cmd):
        return False, f"'{ollama_cmd}' CLI not found or not executable", None
    try:
        proc = subprocess.Popen(
            [ollama_cmd, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            start_new_session=True,  # detach process group on POSIX
        )
        # Give it a moment to boot
        time.sleep(0.5)
        return True, "Ollama server starting", proc
    except Exception as e:
        return False, f"Failed to start ollama serve: {e}", None


def pull_ollama_model(model: str, cmd: Optional[str] = None):
    """Generator that yields output lines while pulling a model."""
    ollama_cmd = (cmd or "ollama").strip()
    if not has_ollama_cli(ollama_cmd):
        yield f"'{ollama_cmd}' CLI not found or not executable"
        return
    try:
        proc = subprocess.Popen(
            [ollama_cmd, "pull", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            yield line.rstrip()
        proc.wait()
        if proc.returncode == 0:
            yield f"Model '{model}' pulled successfully."
        else:
            yield f"ollama pull exited with code {proc.returncode}"
    except FileNotFoundError:
        yield "'ollama' CLI not found in PATH"
    except Exception as e:
        yield f"Error pulling model: {e}"


def pull_ollama_model_http(model: str, host: Optional[str] = None):
    """Generator that yields output lines while pulling a model via Ollama HTTP API.
    Useful when CLI isn't available but server is running.
    """
    h = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
    if requests is None:
        yield "'requests' not installed; cannot pull via HTTP"
        return
    url = f"{h}/api/pull"
    try:
        with requests.post(url, json={"name": model, "stream": True}, stream=True, timeout=600) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    j = json.loads(line)
                    # Ollama sends fields like status, digest, total, completed
                    status = j.get("status")
                    if status:
                        yield status
                except Exception:
                    yield str(line)
        yield f"Model '{model}' pull complete (HTTP)."
    except Exception as e:
        yield f"HTTP pull error: {e}"


def _detect_linux_arch() -> Optional[str]:
    mach = platform.machine().lower()
    if mach in ("x86_64", "amd64"):
        return "amd64"
    if mach in ("aarch64", "arm64"):
        return "arm64"
    return None


def install_ollama_user_local(target_dir: Optional[str] = None):
    """Generator that installs the Ollama binary into a user dir (no sudo).
    Downloads from GitHub releases and writes to ~/.local/bin/ollama by default.
    Yields progress lines. Returns the final path at the end.
    """
    if requests is None:
        yield "'requests' not installed; cannot download Ollama binary"
        return
    arch = _detect_linux_arch()
    if arch is None:
        yield "Unsupported architecture for prebuilt Ollama binary"
        return
    # Try multiple possible asset names (GitHub releases sometimes package as .tgz)
    candidate_names = [
        f"ollama-linux-{arch}",
        f"ollama-linux-{arch}.tgz",
    ]
    base = "https://github.com/ollama/ollama/releases/latest/download"
    home = os.path.expanduser("~")
    bin_dir = target_dir or os.path.join(home, ".local", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    out_path = os.path.join(bin_dir, "ollama")
    try:
        import tarfile
        import tempfile

        last_err: Optional[str] = None
        for name in candidate_names:
            url = f"{base}/{name}"
            yield f"Trying {url}"
            try:
                with requests.get(url, stream=True, timeout=600) as r:
                    r.raise_for_status()
                    # Decide handling based on extension
                    if name.endswith(".tgz"):
                        # Download to temp then extract
                        with tempfile.NamedTemporaryFile(suffix=".tgz", delete=False) as tmp:
                            total = int(r.headers.get("content-length", 0))
                            written = 0
                            for chunk in r.iter_content(chunk_size=1024 * 256):
                                if not chunk:
                                    continue
                                tmp.write(chunk)
                                written += len(chunk)
                                if total:
                                    pct = int(written * 100 / total)
                                    if pct % 10 == 0:
                                        yield f"Downloaded {pct}%"
                            tmp.flush()
                            tmp_path = tmp.name
                        yield "Extracting archive..."
                        with tarfile.open(tmp_path, "r:gz") as tar:
                            member = next((m for m in tar.getmembers() if m.isfile() and m.name.endswith("/ollama") or m.name == "ollama"), None)
                            if not member:
                                # extract all and try to locate
                                tar.extractall(path=bin_dir)
                                cand = os.path.join(bin_dir, "ollama")
                                if os.path.exists(cand):
                                    shutil.move(cand, out_path)
                                else:
                                    raise RuntimeError("'ollama' binary not found in archive")
                            else:
                                with tar.extractfile(member) as fsrc, open(out_path, "wb") as fdst:
                                    shutil.copyfileobj(fsrc, fdst)
                    else:
                        # Direct binary
                        total = int(r.headers.get("content-length", 0))
                        written = 0
                        with open(out_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=1024 * 256):
                                if not chunk:
                                    continue
                                f.write(chunk)
                                written += len(chunk)
                                if total:
                                    pct = int(written * 100 / total)
                                    if pct % 10 == 0:
                                        yield f"Downloaded {pct}%"
                    # Mark executable
                    st_mode = os.stat(out_path).st_mode
                    os.chmod(out_path, st_mode | stat.S_IXUSR)
                    yield f"Installed Ollama binary at {out_path}"
                    yield "Ensure ~/.local/bin is on your PATH (e.g., add 'export PATH=\"$HOME/.local/bin:$PATH\"' to your shell profile)."
                    yield out_path
                    return
            except Exception as e:  # try next candidate
                last_err = str(e)
                yield f"Attempt failed for {name}: {last_err}"
                continue
        # If all candidates failed
        raise RuntimeError(last_err or "Failed to download Ollama binary")
    except Exception as e:
        yield f"Install error: {e}"
