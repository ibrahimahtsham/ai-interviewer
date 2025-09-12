import { Container } from '@mui/material'
import Navbar from './components/Navbar.jsx'
import STTPage from './pages/STT/index.jsx'
import LLMPage from './pages/LLM/index.jsx'
import MicTestPage from './pages/MicTest/index.jsx'
import { Routes, Route, Navigate } from 'react-router-dom'

function App() {
  return (
    <>
      <Navbar />
      <Container maxWidth="md">
        <Routes>
          <Route path="/" element={<STTPage />} />
          <Route path="/llm" element={<LLMPage />} />
          <Route path="/mic-test" element={<MicTestPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </>
  )
}

export default App