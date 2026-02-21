import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHistory, deleteAnalysis } from '../api/axios'

export default function History() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchHistory = () => {
    setLoading(true)
    getHistory()
      .then(res => setAnalyses(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchHistory() }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Usunąć tę analizę?')) return
    await deleteAnalysis(id)
    setAnalyses(prev => prev.filter(a => a.id !== id))
  }

  const aiLabel = (prob) => {
    if (prob > 0.6) return { text: 'AI', color: 'bg-red-100 text-red-700' }
    if (prob > 0.4) return { text: 'Wątpliwy', color: 'bg-yellow-100 text-yellow-700' }
    return { text: 'Human', color: 'bg-green-100 text-green-700' }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Historia analiz</h1>
        <Link to="/analyze" className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm">
          + Nowa analiza
        </Link>
      </div>

      {loading && <p className="text-gray-500 text-center py-12">⏳ Ładowanie...</p>}
      {error && <p className="text-red-500 text-center py-12">⚠️ {error}</p>}

      {!loading && analyses.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-5xl mb-4">📭</p>
          <p>Brak analiz. <Link to="/analyze" className="text-primary-600 hover:underline">Zacznij teraz →</Link></p>
        </div>
      )}

      {!loading && analyses.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-gray-600 font-semibold">Data</th>
                <th className="text-left px-4 py-3 text-gray-600 font-semibold">Fragment tekstu</th>
                <th className="text-center px-4 py-3 text-gray-600 font-semibold">AI?</th>
                <th className="text-center px-4 py-3 text-gray-600 font-semibold">TTR</th>
                <th className="text-center px-4 py-3 text-gray-600 font-semibold">Flesch</th>
                <th className="text-center px-4 py-3 text-gray-600 font-semibold">Akcje</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a, i) => {
                const label = aiLabel(a.ai_probability)
                return (
                  <tr key={a.id} className={`border-b border-gray-100 hover:bg-gray-50 ${i % 2 === 0 ? '' : 'bg-gray-50/50'}`}>
                    <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                      {new Date(a.created_at).toLocaleDateString('pl-PL')}
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-xs">
                      <span className="line-clamp-1">{a.text_preview}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${label.color}`}>
                        {label.text} ({(a.ai_probability * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center font-mono">{a.ttr.toFixed(3)}</td>
                    <td className="px-4 py-3 text-center font-mono">{a.flesch_score.toFixed(1)}</td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <Link to={`/results/${a.id}`} className="text-primary-600 hover:underline text-xs">
                          Podgląd
                        </Link>
                        <button
                          onClick={() => handleDelete(a.id)}
                          className="text-red-400 hover:text-red-600 text-xs"
                        >
                          Usuń
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
