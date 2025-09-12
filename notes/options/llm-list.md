# LLM Options

## 1. Local (e.g., Llama 3, Mistral, Qwen, Phi)
- Cost: Hardware only
- Pros: Privacy, controllable, no usage billing
- Cons: VRAM limits context & model size, maintenance
- Notes: Use quantized GGUF for CPU/GPU flexibility
- Status: ✎

## 2. OpenAI (GPT-4o / mini / Realtime)
- Cost: Usage based
- Pros: Strong reasoning, multimodal, tool calling
- Cons: Cost, rate limits
- Notes: Realtime for low-latency voice loops
- Status: ✎

## 3. Anthropic (Claude 3.x)
- Cost: Usage based
- Pros: Long context, careful responses
- Cons: Higher latency sometimes
- Notes: Good for structured analysis
- Status: ✎

## 4. Google (Gemini)
- Cost: Usage based
- Pros: Multimodal, broad tool ecosystem
- Cons: Model gating
- Notes: Consider for doc + image tasks
- Status: ✎

## 5. Azure OpenAI / Managed Hosting
- Cost: Usage + platform overhead
- Pros: Enterprise controls, region options
- Cons: Provisioning delays
- Notes: Use if needing compliance routing
- Status: ✎

## 6. Hybrid (Local + Cloud Fallback)
- Cost: Mixed
- Pros: Balance latency/cost/quality
- Cons: Routing complexity
- Notes: Policy-based selection (latency, token budget)
- Status: ✎

## Comparison Axes (To Fill)
| Option | Context Length | Multimodal | Tool Calling | Latency (est) | Cost Predictability | Offline |
|--------|----------------|-----------|--------------|---------------|---------------------|---------|
| Local | Varies (4k–128k) | Limited | Via custom code | Very Low (on device) | High | Yes |
| OpenAI | Up to 200k (select) | Yes | Native | Low-Med | Medium | No |
| Anthropic | Up to 200k | Limited vision | Native | Med | Medium | No |
| Google Gemini | Up to 1M (versions) | Yes | Native | Low-Med | Medium | No |
| Azure OpenAI | Matches OpenAI | Yes | Native | Med | Medium | No |
| Hybrid | Policy-based | Depends | Yes | Adaptive | High (tunable) | Partial |

---
