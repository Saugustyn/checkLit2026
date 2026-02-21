import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const ACCEPTED_FORMATS = ".txt,.pdf,.docx"
const MAX_FILE_MB = 10

export default function Analyze() {
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [mode, setMode] = useState('text')   // 'text' | 'file'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  // ─── Upload pliku ───────────────────────────────────────────
  const handleFileSelect = (e) => {
    const selected = e.target.files[0]
    if (!selected) return

    const sizeInMB = selected.size / (1024 * 1024)
    if (sizeInMB > MAX_FILE_MB) {
      setError(`Plik jest zbyt duży (${sizeInMB.toFixed(1)}MB). Maksimum: ${MAX_FILE_MB}MB.`)
      return
    }

    const ext = selected.name.split('.').pop().toLowerCase()
    if (!['txt', 'pdf', 'docx'].includes(ext)) {
      setError('Obsługiwane formaty: .txt, .pdf, .docx')
      return
    }

    setFile(selected)
    setError('')
  }

  const handleFileDrop = (e) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFileSelect({ target: { files: [dropped] } })
  }

  // ─── Analiza ────────────────────────────────────────────────
  const handleAnalyze = async () => {
    setError('')
    setLoading(true)

    try {
      let response

      if (mode === 'file' && file) {
        // Upload pliku — multipart/form-data
        const formData = new FormData()
        formData.append('file', file)
        response = await axios.post('/api/analyze-file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        // Tekst wklejony
        if (text.trim().length < 50) {
          setError('Tekst musi mieć co najmniej 50 znaków.')
          setLoading(false)
          return
        }
        response = await axios.post('/api/analyze', { text })
      }

      navigate(`/results/${response.data.id}`, { state: { data: response.data } })

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Błąd podczas analizy.')
    } finally {
      setLoading(false)
    }
  }

  // ─── Render ─────────────────────────────────────────────────
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Analizuj tekst</h1>
      <p className="text-gray-500 mb-6">
        Wklej tekst lub wgraj plik (.txt, .pdf, .docx) do 10MB. Platforma obsługuje
        teksty do ~10 stron A4.
      </p>

      {/* Przełącznik trybu */}
      <div className="flex gap-2 mb-5">
        <button
          onClick={() => setMode('text')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            mode === 'text'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          ✍️ Wklej tekst
        </button>
        <button
          onClick={() => setMode('file')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            mode === 'file'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          📁 Wgraj plik
        </button>
      </div>

      {/* Tryb: tekst */}
      {mode === 'text' && (
        <>
          <textarea
            className="w-full h-64 border border-gray-300 rounded-xl p-4 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            placeholder="Wklej tutaj tekst literacki (min. 50 znaków)..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="flex justify-between items-center mt-2 mb-4">
            <span className="text-xs text-gray-400">
              Rekomendowana długość: 500 – 10 000 znaków (~1–10 stron)
            </span>
            <span className={`text-sm font-mono ${text.length < 50 ? 'text-red-400' : 'text-gray-400'}`}>
              {text.length.toLocaleString()} znaków
            </span>
          </div>
        </>
      )}

      {/* Tryb: plik */}
      {mode === 'file' && (
        <div
          className={`w-full h-48 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors mb-4 ${
            file
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-50'
          }`}
          onDrop={handleFileDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept={ACCEPTED_FORMATS}
            className="hidden"
            onChange={handleFileSelect}
          />
          {file ? (
            <>
              <div className="text-3xl mb-2">
                {file.name.endsWith('.pdf') ? '📄' : file.name.endsWith('.docx') ? '📝' : '📃'}
              </div>
              <p className="font-semibold text-green-700">{file.name}</p>
              <p className="text-sm text-gray-500 mt-1">
                {(file.size / 1024).toFixed(0)} KB
              </p>
              <button
                className="mt-3 text-xs text-gray-400 hover:text-red-500"
                onClick={(e) => { e.stopPropagation(); setFile(null) }}
              >
                × Usuń plik
              </button>
            </>
          ) : (
            <>
              <div className="text-4xl mb-3">📁</div>
              <p className="text-gray-600 font-medium">Przeciągnij plik lub kliknij</p>
              <p className="text-sm text-gray-400 mt-1">.txt, .pdf, .docx — maks. 10MB</p>
            </>
          )}
        </div>
      )}

      {/* Błąd */}
      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-3 mb-4 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Przycisk analizy */}
      <button
        onClick={handleAnalyze}
        disabled={loading || (mode === 'text' && text.trim().length < 50) || (mode === 'file' && !file)}
        className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-base"
      >
        {loading ? '⏳ Analizowanie...' : '🔍 Analizuj'}
      </button>

      {loading && (
        <p className="text-center text-sm text-gray-400 mt-3">
          Trwa analiza — przy pierwszym uruchomieniu może potrwać dłużej (ładowanie modelu AI)
        </p>
      )}
    </div>
  )
}