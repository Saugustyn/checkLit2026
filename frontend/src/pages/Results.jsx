import { useEffect, useState } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip
} from 'recharts'
import { getResults, downloadText, exportReportJSON, exportReportPDF } from '../api/axios'

const Card = ({ title, children, className = '' }) => (
  <div className={`bg-white border border-gray-200 rounded-xl p-6 shadow-sm ${className}`}>
    <h3 className="font-bold text-lg text-gray-800 mb-4">{title}</h3>
    {children}
  </div>
)

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

const ScaleBar = ({ segments, currentValue, max }) => {
  const pct = Math.min((currentValue / max) * 100, 100)
  return (
    <div className="mt-3 mb-1">
      <div className="flex rounded-full overflow-hidden h-3">
        {segments.map((seg, i) => (
          <div key={i} style={{ width: `${seg.width}%`, backgroundColor: seg.color }} />
        ))}
      </div>
      <div className="relative h-4">
        <div
          className="absolute top-0 w-2 h-2 rounded-full bg-gray-800 border-2 border-white shadow"
          style={{ left: `calc(${pct}% - 4px)` }}
        />
      </div>
    </div>
  )
}

const AlertBox = ({ type = 'info', children }) => {
  const styles = {
    info:    'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    danger:  'bg-red-50 border-red-200 text-red-800',
    success: 'bg-green-50 border-green-200 text-green-800',
  }
  const icons = { info: 'ℹ️', warning: '⚠️', danger: '🚨', success: '✅' }
  return (
    <div className={`border rounded-lg p-3 text-xs leading-relaxed ${styles[type]}`}>
      <span className="mr-1">{icons[type]}</span>{children}
    </div>
  )
}

const ExportBar = ({ id }) => {
  const [downloading, setDownloading] = useState('')
  const handle = (action, label) => {
    setDownloading(label)
    setTimeout(() => { action(); setDownloading('') }, 300)
  }
  return (
    <div className="flex flex-wrap gap-3 items-center print:hidden">
      <button onClick={() => handle(() => exportReportJSON(id), 'json')} disabled={!!downloading}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-60">
        <span>📥</span><span>{downloading === 'json' ? 'Pobieranie...' : 'Eksport JSON'}</span>
      </button>
      <button onClick={() => handle(exportReportPDF, 'pdf')} disabled={!!downloading}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-60">
        <span>🖨️</span><span>{downloading === 'pdf' ? 'Otwieranie...' : 'Drukuj / PDF'}</span>
      </button>
      <button onClick={() => handle(() => downloadText(id), 'txt')} disabled={!!downloading}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-60">
        <span>📄</span><span>{downloading === 'txt' ? 'Pobieranie...' : 'Pobierz tekst (.txt)'}</span>
      </button>
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
  const aiProb = ai_detection.ai_probability
  const lix = quality.lix_score ?? quality.flesch_score
  const inGrayZone = ai_detection.confidence?.toLowerCase().includes('szara')

  const aiColor = aiProb > 0.6 ? 'text-red-600' : aiProb > 0.4 ? 'text-yellow-600' : 'text-green-600'

  const radarData = [
    { metric: 'TTR',          value: stylometry.ttr },
    { metric: 'Gęstość lex.', value: stylometry.lexical_density },
    { metric: 'Entropia',     value: stylometry.entropy / 6 },
    { metric: 'Bogactwo',     value: stylometry.vocab_richness },
    { metric: 'Czytelność',   value: lix / 100 },
  ]
  const ngramData = stylometry.top_ngrams.map(n => ({ name: n.ngram, count: n.count }))

  return (
    <>
      <style>{`
        @media print {
          nav, footer, .print-hidden { display: none !important; }
          body { background: white; }
          @page { margin: 1.5cm; }
        }
      `}</style>

      <div className="max-w-5xl mx-auto px-4 py-10">

        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Wyniki analizy #{data.id}</h1>
            <p className="text-gray-400 text-sm mt-1">
              {new Date(data.created_at).toLocaleString('pl-PL')} · {data.text_length.toLocaleString()} znaków
            </p>
          </div>
          <Link to="/analyze" className="text-sm text-primary-600 hover:underline print-hidden">← Nowa analiza</Link>
        </div>

        <div className="mb-8 p-4 bg-gray-50 border border-gray-200 rounded-xl print-hidden">
          <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wide">Eksport wyników</p>
          <ExportBar id={data.id} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Karta 1: Detekcja AI */}
          <Card title={
            <span className="flex items-center gap-1">
              🤖 Detekcja AI
              <InfoTooltip text="Metoda perplexity na modelu Polish GPT-2 (sdadas/polish-gpt2-small). Niska perplexity = tekst przewidywalny dla modelu = styl AI. Skalibrowano na 50 tekstach polskiej prozy (AUC = 0.94)." />
            </span>
          }>
            <div className={`text-5xl font-black text-center mb-2 ${aiColor}`}>
              {(aiProb * 100).toFixed(1)}%
            </div>
            <p className="text-center font-semibold text-gray-700 mb-1">{ai_detection.label}</p>
            <p className="text-center text-xs text-gray-400 mb-3">
              Pewność: <strong>{ai_detection.confidence}</strong>
            </p>

            <ScaleBar
              currentValue={aiProb * 100}
              max={100}
              segments={[
                { width: 40, color: '#22c55e' },
                { width: 20, color: '#eab308' },
                { width: 40, color: '#ef4444' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>Ludzki (&lt;40%)</span>
              <span>Niepewny</span>
              <span>AI (&gt;60%)</span>
            </div>

            <ProgressBar label="Prawdopodobieństwo AI" value={aiProb} color={
              aiProb > 0.6 ? 'bg-red-500' : aiProb > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
            } />
            <ProgressBar label="Prawdopodobieństwo człowieka" value={ai_detection.human_probability} color="bg-blue-400" />

            {ai_detection.perplexity && (
              <p className="text-xs text-gray-400 mt-1 mb-3">
                Perplexity GPT-2: <span className="font-mono font-semibold">{ai_detection.perplexity}</span>
                <InfoTooltip text="Strefa szara: 28.9–37.0 pkt perplexity. Poniżej 28.9 → AI z wysoką pewnością. Powyżej 37.0 → tekst ludzki (próg Youdena, ROC)." />
              </p>
            )}

            <div className="space-y-2">
              {inGrayZone && (
                <AlertBox type="warning">
                  <strong>Strefa szara</strong> (perplexity 28.9–37.0). Klasyfikacja niepewna — tekst wykazuje cechy obu stylów. Zalecana ręczna weryfikacja.
                </AlertBox>
              )}
              {!inGrayZone && aiProb > 0.6 && (
                <AlertBox type="danger">
                  Wysoka wartość wskazuje na styl zbliżony do AI. Wynik nie jest dowodem autorstwa — stanowi wskazówkę do weryfikacji.
                </AlertBox>
              )}
              {!inGrayZone && aiProb < 0.3 && (
                <AlertBox type="info">
                  Znane ograniczenie: prosta narracja epicka (krótkie zdania opisowe, XIX-wieczna proza polska) może mieć niską perplexity mimo ludzkiego autorstwa.
                </AlertBox>
              )}
            </div>
          </Card>

          {/* Karta 2: Profil */}
          <Card title="📊 Profil stylometryczny">
            <p className="text-xs text-gray-400 mb-3">
              5 znormalizowanych metryk. Im większa powierzchnia — tym bardziej zróżnicowany profil tekstu.
            </p>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <Radar name="Tekst" dataKey="value" fill="#4f6ef7" fillOpacity={0.4} stroke="#4f6ef7" />
              </RadarChart>
            </ResponsiveContainer>
          </Card>

          {/* Karta 3: Metryki stylometryczne */}
          <Card title="📈 Metryki stylometryczne">

            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600 font-medium flex items-center">
                  MATTR — bogactwo leksykalne
                  <InfoTooltip text="Moving Average TTR (okno 50 tokenów) — stabilna wersja wskaźnika TTR, niezależna od długości tekstu. Covington & McFall, 2010." />
                </span>
                <span className="font-mono font-semibold">{stylometry.ttr.toFixed(4)}</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 mb-1">
                <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${stylometry.ttr * 100}%` }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400">
                <span>0 — ubogi</span>
                <span className={stylometry.ttr < 0.5 ? 'text-yellow-600' : stylometry.ttr > 0.7 ? 'text-green-600' : 'text-gray-500'}>
                  {stylometry.ttr < 0.5 ? '⚠️ poniżej normy' : stylometry.ttr > 0.7 ? '✅ bogate' : '✓ typowe (0.5–0.7)'}
                </span>
                <span>1 — bogaty</span>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600 font-medium flex items-center">
                  Gęstość leksykalna
                  <InfoTooltip text="Udział słów treściowych (nie-stopwords) wśród wszystkich tokenów. Wysoka >0.7 = merytoryczny; niska <0.5 = narracyjny z dużą ilością słów funkcyjnych." />
                </span>
                <span className="font-mono font-semibold">{stylometry.lexical_density.toFixed(4)}</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 mb-1">
                <div className="bg-indigo-400 h-2 rounded-full" style={{ width: `${stylometry.lexical_density * 100}%` }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400">
                <span>0 — same stopwords</span>
                <span>1 — same słowa treściowe</span>
              </div>
            </div>

            <ProgressBar
              label={<span className="flex items-center">Bogactwo słownikowe (hapax) <InfoTooltip text="Odsetek słów użytych dokładnie raz (hapax legomena) wśród unikalnych słów. Wyższy = większe zróżnicowanie." /></span>}
              value={stylometry.vocab_richness} color="bg-purple-400"
            />

            <div className="grid grid-cols-3 gap-3 mt-4 text-center">
              {[
                { val: stylometry.word_count, label: 'słów' },
                { val: stylometry.sentence_count, label: 'zdań' },
                { val: stylometry.unique_words, label: 'unikatów' },
              ].map(({ val, label }) => (
                <div key={label} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xl font-bold text-primary-600">{val.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">{label}</div>
                </div>
              ))}
            </div>

            {stylometry.word_count < 100 && (
              <div className="mt-3">
                <AlertBox type="warning">
                  Tekst jest krótki ({stylometry.word_count} słów). Metryki stylometryczne są mniej wiarygodne poniżej 200 słów.
                </AlertBox>
              </div>
            )}
          </Card>

          {/* Karta 4: LIX */}
          <Card title={
            <span className="flex items-center gap-1">
              ✍️ Jakość językowa
              <InfoTooltip text="LIX (Läsbarhetsindex) — wskaźnik czytelności neutralny językowo. Zastąpił Flesch Reading Ease, który jest kalibrowany pod angielski i dawał zaniżone wyniki dla polszczyzny." />
            </span>
          }>
            <div className="text-center mb-3">
              <div className="text-4xl font-black text-primary-600">{lix.toFixed(1)}</div>
              <div className="text-sm text-gray-600 mt-1">
                LIX — <strong>{quality.lix_label ?? quality.flesch_label}</strong>
              </div>
              {quality.lix_description && (
                <div className="text-xs text-gray-400 mt-1 italic">{quality.lix_description}</div>
              )}
            </div>

            <ScaleBar
              currentValue={Math.min(lix, 70)}
              max={70}
              segments={[
                { width: 20, color: '#86efac' },
                { width: 14, color: '#4ade80' },
                { width: 14, color: '#facc15' },
                { width: 14, color: '#fb923c' },
                { width: 38, color: '#ef4444' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>dziecięcy</span>
              <span>łatwy</span>
              <span>średni</span>
              <span>trudny</span>
              <span>b. trudny</span>
            </div>

            <ProgressBar label="Gęstość interpunkcji" value={quality.punctuation_density} color="bg-yellow-400" />
            {quality.long_word_ratio != null && (
              <ProgressBar label="Odsetek długich słów (>6 zn.)" value={quality.long_word_ratio} color="bg-orange-400" />
            )}

            <div className="text-sm text-gray-600 mt-3 bg-gray-50 rounded-lg p-3 grid grid-cols-2 gap-1">
              <span className="text-gray-500">Śr. zdanie:</span>
              <span className="font-semibold">{stylometry.avg_sentence_length.toFixed(1)} słów</span>
              <span className="text-gray-500">Śr. słowo:</span>
              <span className="font-semibold">{quality.avg_word_length.toFixed(1)} znaków</span>
            </div>
          </Card>

          {/* Karta 5: N-gramy */}
          {ngramData.length > 0 && (
            <Card title={
              <span className="flex items-center gap-1">
                🔠 Najczęstsze bigramy
                <InfoTooltip text="Pary słów pojawiające się ≥2 razy. Powtarzające się bigramy mogą wskazywać na szablonowe frazy charakterystyczne dla stylu AI." />
              </span>
            }>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={ngramData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={100} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#4f6ef7" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
              {ngramData[0]?.count > 5 && (
                <div className="mt-2">
                  <AlertBox type="info">
                    Bigramm „{ngramData[0].name}" pojawia się {ngramData[0].count} razy. Wysoka częstotliwość może wskazywać na powtarzalne frazy typowe dla stylu AI.
                  </AlertBox>
                </div>
              )}
            </Card>
          )}

          {/* Karta 6: Entropia */}
          <Card title={
            <span className="flex items-center gap-1">
              🌀 Unikalność tekstu
              <InfoTooltip text="Entropia Shannona — mierzy nieprzewidywalność rozkładu słów. Im wyższa, tym bardziej zróżnicowane i unikalne słownictwo." />
            </span>
          }>
            <div className="text-center mb-3">
              <div className="text-4xl font-black text-purple-600">{stylometry.entropy.toFixed(3)}</div>
              <div className="text-sm text-gray-500">Entropia Shannona (bitów)</div>
            </div>

            <ScaleBar
              currentValue={Math.min(stylometry.entropy, 8)}
              max={8}
              segments={[
                { width: 37, color: '#fca5a5' },
                { width: 25, color: '#fde68a' },
                { width: 38, color: '#86efac' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>0–3 monotonny</span>
              <span>3–5 typowy</span>
              <span>5+ zróżnicowany</span>
            </div>

            <p className="text-sm text-gray-600 text-center">
              {stylometry.entropy < 3
                ? '⚠️ Bardzo niska entropia — silna powtarzalność słownictwa.'
                : stylometry.entropy < 5
                ? '➡️ Umiarkowana entropia — typowy zakres dla prozy narracyjnej.'
                : '✅ Wysoka entropia — bogate, zróżnicowane słownictwo.'}
            </p>
          </Card>

        </div>

        {/* Sekcja ograniczeń */}
        <div className="mt-8 border border-gray-200 rounded-xl overflow-hidden">
          <div className="bg-gray-50 px-5 py-3 border-b border-gray-200 flex items-center gap-2">
            <span>⚠️</span>
            <h3 className="font-semibold text-gray-700 text-sm">Znane ograniczenia systemu</h3>
          </div>
          <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-gray-600 leading-relaxed">
            <div>
              <p className="font-semibold text-gray-700 mb-2">Detekcja AI</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>Skuteczność: AUC = 0.94, dokładność 90% (n=50 tekstów)</li>
                <li>Prosta narracja epicka z krótkimi zdaniami może być błędnie flagowana jako AI — dotyczy XIX-wiecznej prozy polskiej (Reymont, Potop)</li>
                <li>Teksty AI z nieregularną, emocjonalną składnią mogą być przeoczone</li>
                <li>Model skalibrowany wyłącznie na polskich tekstach literackich — niesprawdzony na innych gatunkach</li>
                <li><strong>Wynik jest wskazówką, nie dowodem autorstwa.</strong></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-gray-700 mb-2">Metryki stylometryczne</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>MATTR wiarygodny dla tekstów ≥ 200 słów; przy krótszych wyniki mniej stabilne</li>
                <li>Gęstość leksykalna opiera się na liście 50 stopwords — niekompletna</li>
                <li>LIX może niedoszacowywać trudności tekstów z archaizmami</li>
                <li>N-gramy wymagają min. 2 wystąpień — krótkie teksty mogą nie zwracać wyników</li>
                <li>Entropia: wartości 3–5 bitów to typowy zakres prozy polskiej</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 mt-8 justify-center print-hidden">
          <Link to="/history" className="px-5 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 text-sm">
            📋 Historia analiz
          </Link>
          <Link to="/compare" className="px-5 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg text-sm">
            🔍 Porównaj z innym tekstem
          </Link>
        </div>

        <div className="hidden mt-8 pt-4 border-t border-gray-300 text-xs text-gray-400 text-center print-show">
          checkLit – Literary Analyzer · Analiza #{data.id} · {new Date(data.created_at).toLocaleString('pl-PL')} · Model AUC: 0.94
        </div>
      </div>
    </>
  )
}