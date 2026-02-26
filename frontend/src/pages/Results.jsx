import { useEffect, useState } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip
} from 'recharts'
import { getResults, downloadText, exportReportJSON, exportReportPDF } from '../api/axios'

const Card = ({ title, children, className = '' }) => (
  <div className={`bg-white border border-gray-200 rounded-xl p-6 shadow-sm ${className}`}>
    <h3 className="font-bold text-base text-gray-800 mb-4 flex items-center gap-1.5">{title}</h3>
    {children}
  </div>
)

const BAR_COLORS = {
  'bg-primary-500': '#2d6a4f',
  'bg-primary-400': '#52b788',
  'bg-primary-300': '#95d5b2',
  'bg-red-400':     '#f87171',
  'bg-red-300':     '#fca5a5',
  'bg-yellow-400':  '#fbbf24',
  'bg-amber-400':   '#fbbf24',
  'bg-orange-400':  '#fb923c',
}

const ProgressBar = ({ label, value, max = 1, color = 'bg-primary-500' }) => {
  const pct = Math.min((value / max) * 100, 100)
  const hex = BAR_COLORS[color] ?? '#2d6a4f'
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-mono font-semibold">{typeof value === 'number' ? value.toFixed(4) : value}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div style={{ width: `${pct}%`, height: "8px", borderRadius: "9999px", backgroundColor: hex, transition: "width 0.3s" }} />
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
      <div className="flex rounded-full overflow-hidden h-2.5">
        {segments.map((seg, i) => (
          <div key={i} style={{ width: `${seg.width}%`, backgroundColor: seg.color }} />
        ))}
      </div>
      <div className="relative h-4">
        <div
          className="absolute top-0 w-2 h-2 rounded-full bg-gray-700 border-2 border-white shadow"
          style={{ left: `calc(${pct}% - 4px)` }}
        />
      </div>
    </div>
  )
}

const AlertBox = ({ type = 'info', children }) => {
  const styles = {
    info:    'bg-primary-50 border-primary-200 text-primary-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    danger:  'bg-red-50 border-red-200 text-red-800',
    success: 'bg-primary-50 border-primary-200 text-primary-800',
  }
  const markers = {
    info:    <span className="font-bold mr-1.5">i</span>,
    warning: <span className="font-bold mr-1.5">!</span>,
    danger:  <span className="font-bold mr-1.5">!!</span>,
    success: <span className="font-bold mr-1.5">✓</span>,
  }
  return (
    <div className={`border rounded-lg p-3 text-xs leading-relaxed ${styles[type]}`}>
      {markers[type]}{children}
    </div>
  )
}

const IconAI = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h.01M15 9h.01M9 15h6"/>
  </svg>
)
const IconRadar = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
  </svg>
)
const IconMetrics = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
  </svg>
)
const IconQuality = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
)
const IconNgram = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
)
const IconEntropy = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
  </svg>
)

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
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <span>{downloading === 'json' ? 'Pobieranie...' : 'Eksport JSON'}</span>
      </button>
      <button onClick={() => handle(exportReportPDF, 'pdf')} disabled={!!downloading}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-60">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
        <span>{downloading === 'pdf' ? 'Otwieranie...' : 'Drukuj / PDF'}</span>
      </button>
      <button onClick={() => handle(() => downloadText(id), 'txt')} disabled={!!downloading}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-60">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        <span>{downloading === 'txt' ? 'Pobieranie...' : 'Pobierz tekst (.txt)'}</span>
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

  if (loading) return <div className="text-center py-20 text-gray-400 text-sm">Ładowanie wyników...</div>
  if (error)   return <div className="text-center py-20 text-red-500 text-sm">{error}</div>
  if (!data)   return null

  const { ai_detection, stylometry, quality } = data
  const aiProb    = ai_detection.ai_probability
  const ppxProb   = ai_detection.ppx_probability   
  const lix       = quality.lix_score ?? quality.flesch_score
  const inGrayZone = ai_detection.confidence?.toLowerCase().includes('szara')

  const isHuman  = ai_detection.label === 'Human-written'
  const dispProb  = isHuman ? ai_detection.human_probability : aiProb
  const dispLabel = isHuman ? 'Tekst ludzki' : 'Tekst AI'
  const aiColor   = aiProb > 0.5 ? 'text-red-600' : aiProb > 0.4 ? 'text-yellow-600' : 'text-primary-600'
  const dispColor = isHuman ? 'text-primary-600' : aiColor


  const radarData = [
    { metric: 'TTR',          value: stylometry.ttr },
    { metric: 'Gęstość lex.', value: stylometry.lexical_density },
    { metric: 'Entropia',     value: stylometry.entropy / 10 },  
    { metric: 'Bogactwo',     value: stylometry.vocab_richness },
    { metric: 'Czytelność',   value: Math.min(lix / 100, 1) },
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
          <p className="text-xs text-gray-400 mb-3 font-medium uppercase tracking-wide">Eksport wyników</p>
          <ExportBar id={data.id} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <Card title={
            <span className="flex items-center gap-1.5">
              <IconAI />
              Detekcja AI
              <InfoTooltip text="Wynik hybrydowy: 70% sygnał perplexity modelu Polish GPT-2 + 30% cechy stylometryczne (MATTR, entropia, hapax). Progi Youdena wyznaczone na korpusie 80 tekstów literackich (AUC = 0.90)." />
            </span>
          }>
            <div className={`text-5xl font-black text-center mb-2 ${dispColor}`}>
              {(dispProb * 100).toFixed(1)}%
            </div>
            <p className="text-center font-semibold text-gray-700 mb-1">{ai_detection.label}</p>
            <p className="text-center text-xs text-gray-400 mb-3">
              Pewność: <strong>{ai_detection.confidence}</strong>
            </p>

            <ScaleBar
              currentValue={aiProb * 100}
              max={100}
              segments={[
                { width: 32, color: '#4ade80' },
                { width: 9,  color: '#fbbf24' },
                { width: 59, color: '#f87171' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>Ludzki (&lt;32%)</span>
              <span>Niepewny</span>
              <span>AI (&gt;41%)</span>
            </div>

            {isHuman ? (
              <>
                <ProgressBar label="Prawdopodobieństwo człowieka" value={ai_detection.human_probability} color="bg-primary-500" />
                <ProgressBar label="Prawdopodobieństwo AI"        value={aiProb}                          color="bg-red-300" />
              </>
            ) : (
              <>
                <ProgressBar label="Prawdopodobieństwo AI"        value={aiProb}                          color={
                  aiProb > 0.5 ? 'bg-red-400' : aiProb > 0.4 ? 'bg-yellow-400' : 'bg-primary-500'
                } />
                <ProgressBar label="Prawdopodobieństwo człowieka" value={ai_detection.human_probability} color="bg-primary-300" />
              </>
            )}

            {ai_detection.perplexity && (
              <div className="mt-1 mb-3 space-y-0.5">
                <p className="text-xs text-gray-400">
                  Perplexity GPT-2: <span className="font-mono font-semibold">{ai_detection.perplexity}</span>
                  <InfoTooltip text="Surowa wartość perplexity modelu Polish GPT-2. Poniżej 32.03 → AI, strefa szara 32–41, powyżej 41.06 → Human (progi Youdena, n=80)." />
                </p>
                {ppxProb != null && (
                  <p className="text-xs text-gray-400">
                    Sygnał perplexity: <span className="font-mono font-semibold">{(ppxProb * 100).toFixed(1)}%</span>
                    <InfoTooltip text="Surowy sygnał detekcji oparty wyłącznie na perplexity, przed blendowaniem ze stylometrią. Wynik końcowy to 70% tego sygnału + 30% cech stylometrycznych." />
                  </p>
                )}
              </div>
            )}

            <div className="space-y-2">
              {inGrayZone && (
                <AlertBox type="warning">
                  <strong>Strefa szara</strong> (32.03–41.06 pkt). Klasyfikacja niepewna — tekst wykazuje cechy obu stylów. Zalecana ręczna weryfikacja.
                </AlertBox>
              )}
              {!inGrayZone && aiProb > 0.5 && (
                <AlertBox type="danger">
                  Wysoka wartość wskazuje na styl zbliżony do AI. Wynik nie jest dowodem autorstwa — stanowi wskazówkę do weryfikacji.
                </AlertBox>
              )}
              {!inGrayZone && aiProb < 0.32 && (
                <AlertBox type="info">
                  Znane ograniczenie: prosta narracja epicka (krótkie zdania opisowe, XIX-wieczna proza polska) może mieć niskie perplexity mimo ludzkiego autorstwa.
                </AlertBox>
              )}
            </div>
          </Card>

          <Card title={<span className="flex items-center gap-1.5"><IconRadar />Profil stylometryczny</span>}>
            <p className="text-xs text-gray-400 mb-3">
              5 znormalizowanych metryk. Im większa powierzchnia — tym bardziej zróżnicowany profil tekstu.
            </p>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
                <Radar name="Tekst" dataKey="value" fill="#2d6a4f" fillOpacity={0.35} stroke="#2d6a4f" />
              </RadarChart>
            </ResponsiveContainer>
          </Card>

          <Card title={<span className="flex items-center gap-1.5"><IconMetrics />Metryki stylometryczne</span>}>

            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600 font-medium flex items-center">
                  MATTR — bogactwo leksykalne
                  <InfoTooltip text="Moving Average TTR (okno 50 tokenów) — stabilna wersja wskaźnika TTR, niezależna od długości tekstu. Covington & McFall, 2010." />
                </span>
                <span className="font-mono font-semibold">{stylometry.ttr.toFixed(4)}</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 mb-1">
                <div style={{ width: `${stylometry.ttr * 100}%`, height: "8px", borderRadius: "9999px", backgroundColor: "#2d6a4f" }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400">
                <span>0 — ubogi</span>
                <span className={stylometry.ttr < 0.5 ? 'text-yellow-600' : stylometry.ttr > 0.7 ? 'text-primary-600' : 'text-gray-500'}>
                  {stylometry.ttr < 0.5 ? 'poniżej normy' : stylometry.ttr > 0.7 ? 'bogate' : 'typowe (0.5–0.7)'}
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
                <div style={{ width: `${stylometry.lexical_density * 100}%`, height: "8px", borderRadius: "9999px", backgroundColor: "#52b788" }} />
              </div>
              <div className="flex justify-between text-xs text-gray-400">
                <span>0 — same stopwords</span>
                <span>1 — same słowa treściowe</span>
              </div>
            </div>

            <ProgressBar
              label={<span className="flex items-center">Bogactwo słownikowe (hapax) <InfoTooltip text="Odsetek słów użytych dokładnie raz (hapax legomena) wśród unikalnych słów. Wyższy = większe zróżnicowanie." /></span>}
              value={stylometry.vocab_richness} color="bg-primary-300"
            />

            <div className="grid grid-cols-3 gap-3 mt-4 text-center">
              {[
                { val: stylometry.word_count,     label: 'słów' },
                { val: stylometry.sentence_count, label: 'zdań' },
                { val: stylometry.unique_words,   label: 'unikatów' },
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

          <Card title={
            <span className="flex items-center gap-1.5">
              <IconQuality />
              Jakość językowa
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
                { width: 14, color: '#fbbf24' },
                { width: 14, color: '#fb923c' },
                { width: 38, color: '#f87171' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>dziecięcy</span>
              <span>łatwy</span>
              <span>średni</span>
              <span>trudny</span>
              <span>b. trudny</span>
            </div>

            <ProgressBar label="Gęstość interpunkcji" value={quality.punctuation_density} color="bg-amber-400" />
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

          {ngramData.length > 0 && (
            <Card title={
              <span className="flex items-center gap-1.5">
                <IconNgram />
                Najczęstsze bigramy
                <InfoTooltip text="Pary słów pojawiające się ≥2 razy. Powtarzające się bigramy mogą wskazywać na szablonowe frazy charakterystyczne dla stylu AI." />
              </span>
            }>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={ngramData} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={100} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2d6a4f" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
              {ngramData[0]?.count > 5 && (
                <div className="mt-2">
                  <AlertBox type="info">
                    Bigram „{ngramData[0].name}" pojawia się {ngramData[0].count} razy. Wysoka częstotliwość może wskazywać na powtarzalne frazy typowe dla stylu AI.
                  </AlertBox>
                </div>
              )}
            </Card>
          )}

          <Card title={
            <span className="flex items-center gap-1.5">
              <IconEntropy />
              Unikalność tekstu
              <InfoTooltip text="Entropia Shannona — mierzy nieprzewidywalność rozkładu słów. Typowy zakres dla polskiej prozy: 6–9 bitów. Im wyższa, tym bardziej zróżnicowane słownictwo." />
            </span>
          }>
            <div className="text-center mb-3">
              <div className="text-4xl font-black text-primary-600">{stylometry.entropy.toFixed(3)}</div>
              <div className="text-sm text-gray-500">Entropia Shannona (bitów)</div>
            </div>

            <ScaleBar
              currentValue={Math.min(stylometry.entropy, 10)}
              max={10}
              segments={[
                { width: 30, color: '#fca5a5' },
                { width: 20, color: '#fde68a' },
                { width: 50, color: '#86efac' },
              ]}
            />
            <div className="flex justify-between text-xs text-gray-400 mb-4">
              <span>0–3 monotonny</span>
              <span>3–5 typowy</span>
              <span>5+ zróżnicowany</span>
            </div>

            <p className="text-sm text-gray-600 text-center">
              {stylometry.entropy < 3
                ? 'Bardzo niska entropia — silna powtarzalność słownictwa.'
                : stylometry.entropy < 5
                ? 'Umiarkowana entropia — typowy zakres dla prozy narracyjnej.'
                : 'Wysoka entropia — bogate, zróżnicowane słownictwo.'}
            </p>
          </Card>

        </div>

        <div className="mt-8 border border-gray-200 rounded-xl overflow-hidden">
          <div className="bg-gray-50 px-5 py-3 border-b border-gray-200 flex items-center gap-2">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-500">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <h3 className="font-semibold text-gray-700 text-sm">Znane ograniczenia systemu</h3>
          </div>
          <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-gray-600 leading-relaxed">
            <div>
              <p className="font-semibold text-gray-700 mb-2 text-xs uppercase tracking-wide">Detekcja AI</p>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>Skuteczność: AUC = 0.90, n=80 tekstów (rekalibracja v3)</li>
                <li>Wynik hybrydowy: 70% perplexity GPT-2 + 30% stylometria</li>
                <li>Prosta narracja epicka z krótkimi zdaniami może być błędnie flagowana jako AI — dotyczy XIX-wiecznej prozy polskiej</li>
                <li>Teksty AI z nieregularną, emocjonalną składnią mogą być przeoczone</li>
                <li>Model skalibrowany wyłącznie na polskich tekstach literackich</li>
                <li><strong>Wynik jest wskazówką, nie dowodem autorstwa.</strong></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-gray-700 mb-2 text-xs uppercase tracking-wide">Metryki stylometryczne</p>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>MATTR wiarygodny dla tekstów ≥ 200 słów; przy krótszych wyniki mniej stabilne</li>
                <li>Gęstość leksykalna opiera się na liście 50 stopwords — niekompletna</li>
                <li>LIX może niedoszacowywać trudności tekstów z archaizmami</li>
                <li>N-gramy wymagają min. 2 wystąpień — krótkie teksty mogą nie zwracać wyników</li>
                <li>Entropia: wartości 6–9 bitów to typowy zakres polskiej prozy literackiej</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 mt-8 justify-center print-hidden">
          <Link to="/history" className="flex items-center gap-2 px-5 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 text-sm transition-colors">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>
            Historia analiz
          </Link>
        </div>

        <div className="hidden mt-8 pt-4 border-t border-gray-300 text-xs text-gray-400 text-center print-show">
          checkLit – Analiza #{data.id} · {new Date(data.created_at).toLocaleString('pl-PL')} · Model AUC: 0.90
        </div>
      </div>
    </>
  )
}