import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const ACCEPTED_FORMATS = ".txt,.pdf,.docx"
const MAX_FILE_MB = 10

const IconPaste = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
  </svg>
)

const IconUpload = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
)

const IconFile = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary-400">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
)

export default function Analyze() {
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [mode, setMode] = useState('text')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

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

  const handleAnalyze = async () => {
    setError('')
    setLoading(true)
    try {
      let response
      if (mode === 'file' && file) {
        const formData = new FormData()
        formData.append('file', file)
        response = await axios.post('/api/analyze-file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
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

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Analizuj tekst</h1>
      <p className="text-gray-500 mb-6">
        Wklej tekst lub wgraj plik (.txt, .pdf, .docx) do 10MB.
      </p>

      <div className="flex gap-2 mb-5 p-1 bg-gray-100 rounded-lg w-fit">
        <button
          onClick={() => setMode('text')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === 'text'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <IconPaste /> Wklej tekst
        </button>
        <button
          onClick={() => setMode('file')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === 'file'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <IconUpload /> Wgraj plik
        </button>
      </div>

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
              Rekomendowana długość: 500–10 000 znaków (~1–10 stron)
            </span>
            <span className={`text-sm font-mono ${text.length < 50 ? 'text-red-400' : 'text-gray-400'}`}>
              {text.length.toLocaleString()} znaków
            </span>
          </div>
        </>
      )}

      {mode === 'file' && (
        <div
          className={`w-full h-48 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors mb-4 ${
            file
              ? 'border-primary-400 bg-primary-50'
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
              <IconFile />
              <p className="font-semibold text-primary-700 mt-2">{file.name}</p>
              <p className="text-sm text-gray-500 mt-1">{(file.size / 1024).toFixed(0)} KB</p>
              <button
                className="mt-3 text-xs text-gray-400 hover:text-red-500"
                onClick={(e) => { e.stopPropagation(); setFile(null) }}
              >
                Usuń plik
              </button>
            </>
          ) : (
            <>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-3">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <p className="text-gray-600 font-medium">Przeciągnij plik lub kliknij</p>
              <p className="text-sm text-gray-400 mt-1">.txt, .pdf, .docx — maks. 10MB</p>
            </>
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-3 mb-4 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading || (mode === 'text' && text.trim().length < 50) || (mode === 'file' && !file)}
        className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-base"
      >
        {loading ? 'Analizowanie...' : 'Analizuj tekst'}
      </button>

      {loading && (
        <p className="text-center text-sm text-gray-400 mt-3">
          Trwa analiza — przy pierwszym uruchomieniu może potrwać dłużej (ładowanie modelu AI)
        </p>
      )}
    </div>
  )
}