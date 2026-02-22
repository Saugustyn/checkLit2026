import { useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Legend, Tooltip
} from 'recharts'
import { compareTexts } from '../api/axios'
import axios from 'axios'

const ACCEPTED_FORMATS = '.txt,.pdf,.docx'
const MAX_FILE_MB = 10

const InfoTooltip = ({ text }) => {
  const [show, setShow] = useState(false)
  return (
    <span className="relative inline-block ml-1">
      <button
        className="text-gray-400 hover:text-gray-600 text-xs font-bold w-4 h-4 rounded-full border border-gray-300 inline-flex items-center justify-center"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
      >?</button>
      {show && (
        <span className="absolute z-10 bottom-6 left-0 w-64 bg-gray-800 text-white text-xs rounded-lg p-2 leading-relaxed shadow-lg">
          {text}
        </span>
      )}
    </span>
  )
}

const MetricRow = ({ label, a, b, tooltip }) => {
  const diff = Math.abs(a - b)
  const winner = a > b ? 'A' : 'B'
  return (
    <tr className="border-b border-gray-100">
      <td className="py-2 px-3 text-sm text-gray-600">
        {label}
        {tooltip && <InfoTooltip text={tooltip} />}
      </td>
      <td className={`py-2 px-3 text-sm text-center font-mono font-semibold ${winner === 'A' ? 'text-primary-600' : 'text-gray-700'}`}>
        {a.toFixed(4)}
      </td>
      <td className={`py-2 px-3 text-sm text-center font-mono font-semibold ${winner === 'B' ? 'text-amber-600' : 'text-gray-700'}`}>
        {b.toFixed(4)}
      </td>
      <td className="py-2 px-3 text-sm text-center text-gray-400 font-mono">±{diff.toFixed(4)}</td>
    </tr>
  )
}

const similarityInfo = (score) => {
  if (score >= 0.85) return { label: 'Bardzo wysokie', color: 'text-red-600',     bg: 'bg-red-50 border-red-200',
    desc: 'Teksty są niemal identyczne stylistycznie. Możliwe wspólne autorstwo lub że jeden jest przeróbką drugiego.' }
  if (score >= 0.70) return { label: 'Wysokie',        color: 'text-orange-600',  bg: 'bg-orange-50 border-orange-200',
    desc: 'Silne podobieństwo stylometryczne. Teksty mogą pochodzić od tego samego autora lub modelu AI.' }
  if (score >= 0.50) return { label: 'Umiarkowane',    color: 'text-yellow-600',  bg: 'bg-yellow-50 border-yellow-200',
    desc: 'Umiarkowane podobieństwo. Wspólne cechy stylu, ale wyraźne różnice w słownictwie lub strukturze zdań.' }
  if (score >= 0.30) return { label: 'Niskie',         color: 'text-primary-600', bg: 'bg-primary-50 border-primary-200',
    desc: 'Teksty różnią się stylem. Prawdopodobnie różni autorzy lub znacząco różne gatunki.' }
  return               { label: 'Bardzo niskie',   color: 'text-primary-700', bg: 'bg-primary-50 border-primary-200',
    desc: 'Teksty są stylistycznie bardzo odmienne — różni autorzy, różne gatunki lub epoki.' }
}

const TextSlot = ({ label, labelColor, borderColor, ringColor, value, onChange, file, onFileChange, onFileClear, mode, onModeChange, inputId }) => {
  const validateAndSetFile = (selected) => {
    if (!selected) return
    if (selected.size / (1024 * 1024) > MAX_FILE_MB) return
    const ext = selected.name.split('.').pop().toLowerCase()
    if (!['txt', 'pdf', 'docx'].includes(ext)) return
    onFileChange(selected)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className={`text-sm font-semibold ${labelColor}`}>{label}</label>
        <div className="flex bg-gray-100 rounded-lg p-0.5 gap-0.5">
          <button
            onClick={() => onModeChange('text')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${mode === 'text' ? 'bg-white shadow-sm text-gray-700' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <span className="flex items-center gap-1">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg>
              Tekst
            </span>
          </button>
          <button
            onClick={() => onModeChange('file')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${mode === 'file' ? 'bg-white shadow-sm text-gray-700' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <span className="flex items-center gap-1">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Plik
            </span>
          </button>
        </div>
      </div>

      {mode === 'text' && (
        <>
          <textarea
            className={`w-full h-44 border ${borderColor} rounded-xl p-3 text-sm focus:outline-none focus:ring-2 ${ringColor} resize-none`}
            placeholder="Wklej tekst (min. 50 znaków)..."
            value={value}
            onChange={e => onChange(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">
            {value.length} znaków
            {value.length > 0 && value.length < 200 && <span className="text-yellow-600 ml-2">krótki tekst — wyniki mniej wiarygodne</span>}
          </p>
        </>
      )}

      {mode === 'file' && (
        <div
          className={`w-full h-44 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors ${
            file ? 'border-primary-300 bg-primary-50' : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-50'
          }`}
          onDrop={e => { e.preventDefault(); validateAndSetFile(e.dataTransfer.files[0]) }}
          onDragOver={e => e.preventDefault()}
          onClick={() => document.getElementById(inputId).click()}
        >
          <input
            id={inputId}
            type="file"
            accept={ACCEPTED_FORMATS}
            className="hidden"
            onChange={e => validateAndSetFile(e.target.files[0])}
          />
          {file ? (
            <>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary-500 mb-2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
              <p className="font-semibold text-primary-700 text-sm">{file.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">{(file.size / 1024).toFixed(0)} KB</p>
              <button
                className="mt-2 text-xs text-gray-400 hover:text-red-500 transition-colors"
                onClick={e => { e.stopPropagation(); onFileClear() }}
              >× Usuń plik</button>
            </>
          ) : (
            <>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <p className="text-gray-500 text-sm font-medium">Przeciągnij plik lub kliknij</p>
              <p className="text-xs text-gray-400 mt-1">.txt, .pdf, .docx — maks. 10MB</p>
            </>
          )}
        </div>
      )}
    </div>
  )
}

const arch_extractTextFromFile = async (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (ext === 'txt') return await file.text()
  const formData = new FormData()
  formData.append('file', file)
  const res = await axios.post('/api/analyze-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data.full_text || ''
}

const extractTextFromFile = async (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (ext === 'txt') return await file.text()

  const formData = new FormData()
  formData.append('file', file)

  const res = await axios.post('/api/analyze-file', formData)

  const resText = await axios.get(`/api/results/${res.data.id}/text`, {
    responseType: 'text',
  })

  return resText.data || ''
}

export default function Compare() {
  const [modeA, setModeA] = useState('text')
  const [modeB, setModeB] = useState('text')
  const [textA, setTextA] = useState('')
  const [textB, setTextB] = useState('')
  const [fileA, setFileA] = useState(null)
  const [fileB, setFileB] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCompare = async () => {
    setError('')
    if (modeA === 'text' && textA.length < 50) { setError('Tekst A musi mieć co najmniej 50 znaków.'); return }
    if (modeB === 'text' && textB.length < 50) { setError('Tekst B musi mieć co najmniej 50 znaków.'); return }
    if (modeA === 'file' && !fileA) { setError('Wybierz plik dla Tekstu A.'); return }
    if (modeB === 'file' && !fileB) { setError('Wybierz plik dla Tekstu B.'); return }

    setLoading(true)
    try {
      const [resolvedA, resolvedB] = await Promise.all([
        modeA === 'text' ? textA : extractTextFromFile(fileA),
        modeB === 'text' ? textB : extractTextFromFile(fileB),
      ])
      const res = await compareTexts(resolvedA, resolvedB)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Błąd podczas porównania.')
    } finally {
      setLoading(false)
    }
  }

  const radarData = result ? [
    { metric: 'TTR',          A: result.text_a.ttr,             B: result.text_b.ttr },
    { metric: 'Gęstość lex.', A: result.text_a.lexical_density, B: result.text_b.lexical_density },
    { metric: 'Entropia',     A: result.text_a.entropy / 10,    B: result.text_b.entropy / 10 },
    { metric: 'Bogactwo',     A: result.text_a.vocab_richness,  B: result.text_b.vocab_richness },
  ] : []

  const simInfo = result ? similarityInfo(result.similarity_score) : null
  const canCompare = (modeA === 'text' ? textA.length >= 50 : !!fileA) && (modeB === 'text' ? textB.length >= 50 : !!fileB)

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Porównaj dwa teksty</h1>
      <p className="text-gray-500 mb-2">Analiza porównawcza profili stylometrycznych — TTR, entropia, gęstość leksykalna, bogactwo słownikowe.</p>
      <p className="text-xs text-gray-500 mb-8 bg-primary-50 border border-primary-100 rounded-lg p-3">
        Porównanie opiera się wyłącznie na cechach stylometrycznych, nie na treści. Wysoki wynik podobieństwa nie jest dowodem tożsamości autorskiej — oznacza zbliżony styl pisania.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-4">
        <TextSlot
          label="Tekst A" labelColor="text-primary-700"
          borderColor="border-primary-200" ringColor="focus:ring-primary-400"
          value={textA} onChange={setTextA}
          file={fileA} onFileChange={setFileA} onFileClear={() => setFileA(null)}
          mode={modeA} onModeChange={setModeA} inputId="file-input-a"
        />
        <TextSlot
          label="Tekst B" labelColor="text-amber-700"
          borderColor="border-amber-200" ringColor="focus:ring-amber-400"
          value={textB} onChange={setTextB}
          file={fileB} onFileChange={setFileB} onFileClear={() => setFileB(null)}
          mode={modeB} onModeChange={setModeB} inputId="file-input-b"
        />
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-3 mb-4 text-sm">{error}</div>
      )}

      <button
        onClick={handleCompare}
        disabled={loading || !canCompare}
        className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
      >
        {loading ? 'Porównywanie...' : 'Porównaj teksty'}
      </button>

      {result && (
        <div className="mt-10">
          <div className={`text-center border rounded-xl p-6 shadow-sm mb-6 ${simInfo.bg}`}>
            <p className="text-gray-500 text-sm mb-1">
              Podobieństwo stylometryczne
              <InfoTooltip text="Obliczone jako 1 minus średnia znormalizowana różnica 4 metryk: TTR, gęstość leksykalna, entropia, średnia długość zdania." />
            </p>
            <div className={`text-5xl font-black ${simInfo.color}`}>{(result.similarity_score * 100).toFixed(1)}%</div>
            <p className={`font-semibold mt-1 ${simInfo.color}`}>{simInfo.label}</p>
            <p className="text-gray-500 text-xs mt-2 max-w-md mx-auto">{simInfo.desc}</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6 text-xs">
            <p className="font-semibold text-gray-700 mb-2 text-xs uppercase tracking-wide">Skala podobieństwa</p>
            <div className="space-y-1.5">
              {[
                { range: '85–100%', label: 'Bardzo wysokie', color: 'bg-red-500',     desc: 'Niemal identyczny styl — możliwe wspólne autorstwo' },
                { range: '70–85%',  label: 'Wysokie',        color: 'bg-orange-400',  desc: 'Silne podobieństwo — potencjalnie ten sam autor / model' },
                { range: '50–70%',  label: 'Umiarkowane',    color: 'bg-yellow-400',  desc: 'Podobny gatunek lub epoka literacka' },
                { range: '30–50%',  label: 'Niskie',         color: 'bg-primary-400', desc: 'Różne style pisania' },
                { range: '0–30%',   label: 'Bardzo niskie',  color: 'bg-primary-600', desc: 'Znacząco odmienne style / epoki / gatunki' },
              ].map(s => (
                <div key={s.range} className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-sm flex-shrink-0 ${s.color}`} />
                  <span className="w-16 text-gray-500">{s.range}</span>
                  <span className="font-medium w-24 text-gray-700">{s.label}</span>
                  <span className="text-gray-400">{s.desc}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-4 text-sm uppercase tracking-wide">Profil porównawczy</h3>
              <ResponsiveContainer width="100%" height={240}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                  <Radar name="Tekst A" dataKey="A" fill="#2d6a4f" fillOpacity={0.3} stroke="#2d6a4f" />
                  <Radar name="Tekst B" dataKey="B" fill="#d97706" fillOpacity={0.3} stroke="#d97706" />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-4 text-sm uppercase tracking-wide">Zestawienie metryk</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left text-xs text-gray-500 py-1 px-3">Metryka</th>
                    <th className="text-center text-xs text-primary-600 py-1 px-3 font-semibold">Tekst A</th>
                    <th className="text-center text-xs text-amber-600 py-1 px-3 font-semibold">Tekst B</th>
                    <th className="text-center text-xs text-gray-400 py-1 px-3">Δ</th>
                  </tr>
                </thead>
                <tbody>
                  <MetricRow label="TTR (MATTR)" a={result.text_a.ttr} b={result.text_b.ttr}
                    tooltip="Moving Average TTR — bogactwo leksykalne, niezależne od długości tekstu." />
                  <MetricRow label="Gęstość lex." a={result.text_a.lexical_density} b={result.text_b.lexical_density}
                    tooltip="Udział słów treściowych (nie-stopwords) wśród wszystkich tokenów." />
                  <MetricRow label="Entropia" a={result.text_a.entropy} b={result.text_b.entropy}
                    tooltip="Entropia Shannona — nieprzewidywalność rozkładu słów. Wyższe = bardziej zróżnicowane." />
                  <MetricRow label="Bogactwo słow." a={result.text_a.vocab_richness} b={result.text_b.vocab_richness}
                    tooltip="Odsetek słów użytych dokładnie raz (hapax legomena)." />
                  <MetricRow label="Śr. dł. zdania" a={result.text_a.avg_sentence_length} b={result.text_b.avg_sentence_length}
                    tooltip="Średnia liczba słów w zdaniu." />
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-500">
            <strong>Ograniczenie:</strong> Wynik podobieństwa oparty jest wyłącznie na 4 metrykach stylometrycznych. Nie uwzględnia treści, tematyki ani podobieństwa frazowego. Nie stanowi dowodu tożsamości autorskiej.
          </div>
        </div>
      )}
    </div>
  )
}