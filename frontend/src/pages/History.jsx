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
    if (prob > 0.41) return { text: 'AI',       color: 'bg-red-100 text-red-700' }
    if (prob > 0.32) return { text: 'Wątpliwy', color: 'bg-yellow-100 text-yellow-700' }
    return              { text: 'Human',     color: 'bg-primary-100 text-primary-700' }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Historia analiz</h1>
        <Link to="/analyze" className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Nowa analiza
        </Link>
      </div>

      {loading && <p className="text-gray-400 text-center py-12 text-sm">Ładowanie...</p>}
      {error && <p className="text-red-500 text-center py-12 text-sm">{error}</p>}

      {!loading && analyses.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <svg className="mx-auto mb-4 text-gray-300" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.18 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.5a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 21.5 16"/>
          </svg>
          <p className="text-sm">Brak analiz. <Link to="/analyze" className="text-primary-600 hover:underline">Zacznij teraz →</Link></p>
        </div>
      )}

      {!loading && analyses.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">Data</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">Fragment tekstu</th>
                <th className="text-center px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">AI?</th>
                <th className="text-center px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">TTR</th>
                <th className="text-center px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">LIX</th>
                <th className="text-center px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wide">Akcje</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a, i) => {
                const label = aiLabel(a.ai_probability)
                return (
                  <tr key={a.id} className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${i % 2 === 0 ? '' : 'bg-gray-50/40'}`}>
                    <td className="px-4 py-3 text-gray-400 whitespace-nowrap text-xs">
                      {new Date(a.created_at).toLocaleDateString('pl-PL')}
                    </td>
                    <td className="px-4 py-3 text-gray-700 max-w-xs">
                      <span className="line-clamp-1">{a.text_preview}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded-md text-xs font-semibold ${label.color}`}>
                        {label.text} ({(a.ai_probability * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center font-mono text-gray-600">{a.ttr.toFixed(3)}</td>
                    <td className="px-4 py-3 text-center font-mono text-gray-600">{(a.lix_score ?? a.flesch_score)?.toFixed(1)}</td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-3">
                        <Link to={`/results/${a.id}`} className="text-primary-600 hover:text-primary-700 text-xs font-medium">
                          Podgląd
                        </Link>
                        <button
                          onClick={() => handleDelete(a.id)}
                          className="text-gray-300 hover:text-red-500 text-xs transition-colors"
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