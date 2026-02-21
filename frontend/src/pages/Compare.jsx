import { useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Legend, Tooltip
} from 'recharts'
import { compareTexts } from '../api/axios'

const MetricRow = ({ label, a, b }) => {
  const diff = Math.abs(a - b)
  const winner = a > b ? 'A' : 'B'
  return (
    <tr className="border-b border-gray-100">
      <td className="py-2 px-3 text-sm text-gray-600">{label}</td>
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

  // Dane do wykresu radarowego porównawczego
  const radarData = result ? [
    { metric: 'TTR',          A: result.text_a.ttr,              B: result.text_b.ttr },
    { metric: 'Gęstość lex.', A: result.text_a.lexical_density,  B: result.text_b.lexical_density },
    { metric: 'Entropia',     A: result.text_a.entropy / 10,     B: result.text_b.entropy / 10 },
    { metric: 'Bogactwo',     A: result.text_a.vocab_richness,   B: result.text_b.vocab_richness },
  ] : []

  const similarityPct = result ? (result.similarity_score * 100).toFixed(1) : 0
  const similarityColor = result?.similarity_score > 0.7 ? 'text-green-600' :
                          result?.similarity_score > 0.4 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Porównaj dwa teksty</h1>
      <p className="text-gray-500 mb-8">Analiza porównawcza profili stylometrycznych dwóch tekstów literackich.</p>

      {/* Dwa pola tekstowe */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-semibold text-blue-700 mb-1">Tekst A</label>
          <textarea
            className="w-full h-48 border border-blue-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            placeholder="Wklej pierwszy tekst..."
            value={textA}
            onChange={e => setTextA(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">{textA.length} znaków</p>
        </div>
        <div>
          <label className="block text-sm font-semibold text-orange-700 mb-1">Tekst B</label>
          <textarea
            className="w-full h-48 border border-orange-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 resize-none"
            placeholder="Wklej drugi tekst..."
            value={textB}
            onChange={e => setTextB(e.target.value)}
          />
          <p className="text-xs text-gray-400 mt-1">{textB.length} znaków</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-3 mb-4 text-sm">
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={handleCompare}
        disabled={loading}
        className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white font-semibold py-3 rounded-xl transition-colors"
      >
        {loading ? '⏳ Porównywanie...' : '🔍 Porównaj teksty'}
      </button>

      {/* Wyniki */}
      {result && (
        <div className="mt-10">
          {/* Similarity score */}
          <div className="text-center bg-white border border-gray-200 rounded-xl p-6 shadow-sm mb-6">
            <p className="text-gray-500 text-sm mb-1">Podobieństwo stylometryczne</p>
            <div className={`text-5xl font-black ${similarityColor}`}>{similarityPct}%</div>
            <p className="text-gray-400 text-xs mt-2">
              {result.similarity_score > 0.7 ? 'Teksty są stylistycznie bardzo podobne'
               : result.similarity_score > 0.4 ? 'Teksty wykazują umiarkowane podobieństwo'
               : 'Teksty różnią się znacząco stylem'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Radar chart */}
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

            {/* Tabela metryk */}
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
                  <MetricRow label="TTR" a={result.text_a.ttr} b={result.text_b.ttr} />
                  <MetricRow label="Gęstość lex." a={result.text_a.lexical_density} b={result.text_b.lexical_density} />
                  <MetricRow label="Entropia" a={result.text_a.entropy} b={result.text_b.entropy} />
                  <MetricRow label="Bogactwo słow." a={result.text_a.vocab_richness} b={result.text_b.vocab_richness} />
                  <MetricRow label="Śr. dł. zdania" a={result.text_a.avg_sentence_length} b={result.text_b.avg_sentence_length} />
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
