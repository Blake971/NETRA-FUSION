import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ScanResults from './pages/ScanResults'
import ScanHistory from './pages/ScanHistory'
import GoogleDork from './pages/GoogleDork'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/scan" element={<ScanResults />} />
        <Route path="/history" element={<ScanHistory />} />
        <Route path="/dork" element={<GoogleDork />} />
      </Routes>
    </Router>
  )
}

export default App
