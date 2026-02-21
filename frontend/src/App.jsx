import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Analyze from './pages/Analyze'
import Results from './pages/Results'
import History from './pages/History'
import Compare from './pages/Compare'
import About from './pages/About'

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/"           element={<Home />} />
            <Route path="/analyze"    element={<Analyze />} />
            <Route path="/results/:id" element={<Results />} />
            <Route path="/history"    element={<History />} />
            <Route path="/compare"    element={<Compare />} />
            <Route path="/about"      element={<About />} />
          </Routes>
        </main>
        <footer className="text-center text-sm text-gray-400 py-4">
          Literary Analyzer © 2024 — Praca inżynierska
        </footer>
      </div>
    </Router>
  )
}

export default App
