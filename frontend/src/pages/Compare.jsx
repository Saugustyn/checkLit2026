import { useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Legend, Tooltip
} from 'recharts'
import { compareTexts } from '../api/axios'

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
      <td className={`py-2 px-3 text-sm text-center font-mono font-semibold ${winner === 'A' ? 'text-blue-600' : 'text-gray-700'}`}>
        {a.toFixed(4)}
      </td>
      <td className={`py-2 px-3 text-sm text-center font-mono font-semibold ${winner === 'B' ? 'text-orange-600' : 'text-gray-700'}`}>
        {b.toFixed(4)}
      </td>
      <td className="py-2 px-3 text-sm text-center text-gray-400 font-mono">±{diff.toFixed(4)}</td>
    </tr>
  )
}

const similarityInfo = (score) => {
  if (score >= 0.85) return { label: 'Bardzo wysoke', color: 'text-red-600', bg: 'bg-red-50 border-red-200', icon: '🚨',
    desc: 'Teksty są niemal identyczne stylistycznie. Możliwe wspólne autorstwo lub że jeden jest przeróbką drugiego.' }
  if (score >= 0.70) return { label: 'Wysokie', color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200', icon: '⚠️',
    desc: 'Silne podobieństwo stylometryczne. Teksty mogą pochodzić od tego samego autora lub modelu AI.' }
  if (score >= 0.50) return { label: 'Umiarkowane', color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200', icon: 'ℹ️',
    desc: 'Umiarkowane podobieństwo. Wspólne cechy stylu, ale wyraźne różnice w słownictwie lub strukturze zdań.' }
  if (score >= 0.30) return { label: 'Niskie', color: 'text-green-600', bg: 'bg-green-50 border-green-200', icon: '✅',
    desc: 'Teksty różnią się stylem. Prawdopodobnie różni autorzy lub znacząco różne gatunki.' }
  return { label: 'Bardzo niskie', color: 'text-green-700', bg: 'bg-green-50 border-green-200', icon: '✅',
    desc: 'Teksty są stylistycznie bardzo odmienne — różni autorzy, różne gatunki lub epoki.' }
}

export default function Compare() {
  const [textA, setTextA] = useState('')
  const [textB, setTextB] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCompare = async () => {
    if (textA.length < 50 || textB.length < 50) {
      setError('Oba teksty muszą mieć co najmniej 50 znaków.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await compareTexts(textA, textB)
      setResult(res.data)
    } catch (err) {
      setError(err.message)
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

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Porównaj dwa teksty</h1>
      <p className="text-gray-500 mb-2">Analiza porównawcza profili stylometrycznych — TTR, entropia, gęstość leksykalna, bogactwo słownikowe.</p>
      <p className="text-xs text-gray-400 mb-8 bg-blue-50 border border-blue-100 rounded-lg p-3">
        ℹ️ Porównanie opiera się wyłącznie na cechach stylometrycznych, nie na treści. Wysoki wynik podobieństwa nie jest dowodem tożsamości autorskiej — oznacza zbliżony styl pisania.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-semibold text-blue-700 mb-1">Tekst A</label>
          <textarea
            className="w-full h-48 border border-blue-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            placeholder="Wklej pierwszy tekst (min. 50 znaków)..."
            value={textA}
            onChange={e => setTextA(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">
            {textA.length} znaków
            {textA.length > 0 && textA.length < 200 && <span className="text-yellow-600 ml-2">⚠️ krótki tekst — wyniki mniej wiarygodne</span>}
          </p>
        </div>
        <div>
          <label className="block text-sm font-semibold text-orange-700 mb-1">Tekst B</label>
          <textarea
            className="w-full h-48 border border-orange-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 resize-none"
            placeholder="Wklej drugi tekst (min. 50 znaków)..."
            value={textB}
            onChange={e => setTextB(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">
            {textB.length} znaków
            {textB.length > 0 && textB.length < 200 && <span className="text-yellow-600 ml-2">⚠️ krótki tekst — wyniki mniej wiarygodne</span>}
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-3 mb-4 text-sm">⚠️ {error}</div>
      )}

      <button onClick={handleCompare} disabled={loading}
        className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white font-semibold py-3 rounded-xl transition-colors">
        {loading ? '⏳ Porównywanie...' : '🔍 Porównaj teksty'}
      </button>

      {result && (
        <div className="mt-10">

          {/* Wynik podobieństwa */}
          <div className={`text-center border rounded-xl p-6 shadow-sm mb-6 ${simInfo.bg}`}>
            <p className="text-gray-500 text-sm mb-1">
              Podobieństwo stylometryczne
              <InfoTooltip text="Obliczone jako 1 minus średnia znormalizowana różnica 4 metryk: TTR, gęstość leksykalna, entropia, średnia długość zdania." />
            </p>
            <div className={`text-5xl font-black ${simInfo.color}`}>
              {(result.similarity_score * 100).toFixed(1)}%
            </div>
            <p className={`font-semibold mt-1 ${simInfo.color}`}>{simInfo.label}</p>
            <p className="text-gray-500 text-xs mt-2 max-w-md mx-auto">{simInfo.icon} {simInfo.desc}</p>
          </div>

          {/* Skala referencyjna */}
          <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6 text-xs">
            <p className="font-semibold text-gray-700 mb-2">Skala podobieństwa stylometrycznego</p>
            <div className="space-y-1">
              {[
                { range: '85–100%', label: 'Bardzo wysokie', color: 'bg-red-500',    desc: 'Niemal identyczny styl — możliwe wspólne autorstwo' },
                { range: '70–85%',  label: 'Wysokie',        color: 'bg-orange-400', desc: 'Silne podobieństwo — potencjalnie ten sam autor / model' },
                { range: '50–70%',  label: 'Umiarkowane',    color: 'bg-yellow-400', desc: 'Podobny gatunek lub epoka literacka' },
                { range: '30–50%',  label: 'Niskie',         color: 'bg-green-400',  desc: 'Różne style pisania' },
                { range: '0–30%',   label: 'Bardzo niskie',  color: 'bg-green-600',  desc: 'Znacząco odmienne style / epoki / gatunki' },
              ].map(s => (
                <div key={s.range} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full flex-shrink-0 ${s.color}`} />
                  <span className="w-16 text-gray-500">{s.range}</span>
                  <span className="font-medium w-24">{s.label}</span>
                  <span className="text-gray-400">{s.desc}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-4">📊 Profil porównawczy</h3>
              <ResponsiveContainer width="100%" height={240}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                  <Radar name="Tekst A" dataKey="A" fill="#3b82f6" fillOpacity={0.3} stroke="#3b82f6" />
                  <Radar name="Tekst B" dataKey="B" fill="#f97316" fillOpacity={0.3} stroke="#f97316" />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-4">📋 Zestawienie metryk</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left text-xs text-gray-500 py-1 px-3">Metryka</th>
                    <th className="text-center text-xs text-blue-600 py-1 px-3 font-semibold">Tekst A</th>
                    <th className="text-center text-xs text-orange-600 py-1 px-3 font-semibold">Tekst B</th>
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
            ⚠️ <strong>Ograniczenie:</strong> Wynik podobieństwa oparty jest wyłącznie na 4 metrykach stylometrycznych. Nie uwzględnia treści, tematyki ani podobieństwa frazowego. Nie stanowi dowodu tożsamości autorskiej.
          </div>
        </div>
      )}
    </div>
  )
}