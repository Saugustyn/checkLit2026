import { useEffect, useState } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell
} from 'recharts'
import { getResults } from '../api/axios'

// Komponent karty wynikowej
const Card = ({ title, children }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
    <h3 className="font-bold text-lg text-gray-800 mb-4">{title}</h3>
    {children}
  </div>
)

// Pasek progresu z etykietą
const ProgressBar = ({ label, value, max = 1, color = 'bg-primary-500' }) => {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-mono font-semibold">{typeof value === 'number' ? value.toFixed(4) : value}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function Results() {
  const { id } = useParams()
  const location = useLocation()
  const [data, setData] = useState(location.state?.data || null)
  const [loading, setLoading] = useState(!data)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!data) {
      getResults(id)
        .then(res => setData(res.data))
        .catch(err => setError(err.message))
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) return <div className="text-center py-20 text-gray-500">⏳ Ładowanie wyników...</div>
  if (error)   return <div className="text-center py-20 text-red-500">⚠️ {error}</div>
  if (!data)   return null

  const { ai_detection, stylometry, quality } = data

  // Dane do wykresu radarowego (stylometria)
  const radarData = [
    { metric: 'TTR',        value: stylometry.ttr },
    { metric: 'Gęstość lex.', value: stylometry.lexical_density },
    { metric: 'Entropia',   value: stylometry.entropy / 6 },  // normalizacja
    { metric: 'Bogactwo',   value: stylometry.vocab_richness },
    { metric: 'Czytelność', value: quality.flesch_score / 100 },
  ]

  // Dane do wykresu słupkowego (top n-gramy)
  const ngramData = stylometry.top_ngrams.map(n => ({ name: n.ngram, count: n.count }))

  // Kolor wskaźnika AI
  const aiColor = ai_detection.ai_probability > 0.6 ? 'text-red-600' : 
                  ai_detection.ai_probability > 0.4 ? 'text-yellow-600' : 'text-green-600'

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Wyniki analizy #{data.id}</h1>
          <p className="text-gray-400 text-sm mt-1">
            {new Date(data.created_at).toLocaleString('pl-PL')} · {data.text_length} znaków
          </p>
        </div>
        <Link to="/analyze" className="text-sm text-primary-600 hover:underline">
          ← Nowa analiza
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Karta 1: Detekcja AI */}
        <Card title="🤖 Detekcja AI">
          <div className={`text-5xl font-black text-center mb-3 ${aiColor}`}>
            {(ai_detection.ai_probability * 100).toFixed(1)}%
          </div>
          <p className="text-center font-semibold text-gray-700 mb-4">{ai_detection.label}</p>
          <ProgressBar label="Prawdopodobieństwo AI" value={ai_detection.ai_probability} color={
            ai_detection.ai_probability > 0.6 ? 'bg-red-500' : 
            ai_detection.ai_probability > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
          } />
          <ProgressBar label="Prawdopodobieństwo człowieka" value={ai_detection.human_probability} color="bg-blue-400" />
          <p className="text-xs text-gray-400 mt-2 text-center">Pewność klasyfikacji: {ai_detection.confidence}</p>
        </Card>

        {/* Karta 2: Profil stylometryczny */}
        <Card title="📊 Profil stylometryczny">
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
              <Radar name="Tekst" dataKey="value" fill="#4f6ef7" fillOpacity={0.4} stroke="#4f6ef7" />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        {/* Karta 3: Metryki szczegółowe */}
        <Card title="📈 Metryki szczegółowe">
          <ProgressBar label="TTR (bogactwo leksykalne)" value={stylometry.ttr} />
          <ProgressBar label="Gęstość leksykalna" value={stylometry.lexical_density} />
          <ProgressBar label="Bogactwo słownikowe" value={stylometry.vocab_richness} />
          <div className="grid grid-cols-3 gap-3 mt-4 text-center">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-primary-600">{stylometry.word_count}</div>
              <div className="text-xs text-gray-500">słów</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-primary-600">{stylometry.sentence_count}</div>
              <div className="text-xs text-gray-500">zdań</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-primary-600">{stylometry.unique_words}</div>
              <div className="text-xs text-gray-500">unikatów</div>
            </div>
          </div>
        </Card>

        {/* Karta 4: Jakość językowa */}
        <Card title="✍️ Jakość językowa">
          <div className="text-center mb-4">
            <div className="text-4xl font-black text-primary-600">{quality.flesch_score}</div>
            <div className="text-sm text-gray-500">Flesch Reading Ease – <strong>{quality.flesch_label}</strong></div>
          </div>
          <ProgressBar label="Czytelność (Flesch)" value={quality.flesch_score} max={100} color="bg-green-500" />
          <ProgressBar label="Gęstość interpunkcji" value={quality.punctuation_density} color="bg-yellow-400" />
          <div className="text-sm text-gray-600 mt-2">
            Śr. długość zdania: <strong>{stylometry.avg_sentence_length.toFixed(1)}</strong> słów &nbsp;|&nbsp;
            Śr. długość słowa: <strong>{quality.avg_word_length.toFixed(1)}</strong> znaków
          </div>
        </Card>

        {/* Karta 5: Top n-gramy */}
        {ngramData.length > 0 && (
          <Card title="🔠 Najczęstsze bigramy">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={ngramData} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={100} />
                <Tooltip />
                <Bar dataKey="count" fill="#4f6ef7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        )}

        {/* Karta 6: Unikalność */}
        <Card title="🌀 Unikalność tekstu">
          <div className="text-center mb-4">
            <div className="text-4xl font-black text-purple-600">{stylometry.entropy.toFixed(3)}</div>
            <div className="text-sm text-gray-500">Entropia Shannona</div>
          </div>
          <p className="text-sm text-gray-600 text-center">
            Wyższa entropia oznacza bardziej zróżnicowane, nieprzewidywalne słownictwo.
            {stylometry.entropy > 4
              ? ' Tekst wykazuje wysoką unikalność leksykalną.'
              : ' Tekst wykazuje umiarkowaną unikalność.'}
          </p>
        </Card>
      </div>

      {/* Akcje */}
      <div className="flex gap-4 mt-8 justify-center">
        <Link to="/history" className="px-5 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 text-sm">
          📋 Historia analiz
        </Link>
        <Link to="/compare" className="px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm">
          🔍 Porównaj z innym tekstem
        </Link>
      </div>
    </div>
  )
}
