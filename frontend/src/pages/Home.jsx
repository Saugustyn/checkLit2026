import { Link } from 'react-router-dom'

const icons = {
  detect: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      <path d="M11 8v6M8 11h6"/>
    </svg>
  ),
  style: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3h18M3 9h12M3 15h8M3 21h5"/>
    </svg>
  ),
  quality: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
  ),
  compare: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="18"/><rect x="14" y="3" width="7" height="18"/>
    </svg>
  ),
}

const features = [
  {
    icon: icons.detect,
    title: 'Detekcja AI',
    desc: 'Wykrywa fragmenty generowane przez modele językowe AI z określeniem prawdopodobieństwa.',
  },
  {
    icon: icons.style,
    title: 'Stylometria',
    desc: 'Analizuje TTR, n-gramy, długość zdań, entropię i bogactwo słownikowe.',
  },
  {
    icon: icons.quality,
    title: 'Jakość językowa',
    desc: 'Ocenia czytelność (LIX), gęstość leksykalną i strukturę tekstu.',
  },
  {
    icon: icons.compare,
    title: 'Porównanie',
    desc: 'Zestawia dwa teksty stylometrycznie, generując raport podobieństwa.',
  },
]

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-12">

      <div className="text-center mb-14">
        <div className="inline-block bg-primary-50 text-primary-700 text-xs font-semibold px-3 py-1 rounded-full mb-4 tracking-wide uppercase">
          Analiza tekstu literackiego
        </div>
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
          checkLit
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-8 leading-relaxed">
          Platforma do automatycznej analizy autentyczności i stylu tekstów literackich.
          Łączy algorytmy NLP, stylometrię i modele AI.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 bg-primary-500 hover:bg-primary-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors text-base"
        >
          Analizuj tekst
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-14">
        {features.map((f) => (
          <div key={f.title} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-primary-200 transition-all group">
            <div className="w-10 h-10 rounded-lg bg-primary-50 text-primary-600 flex items-center justify-center mb-4 group-hover:bg-primary-100 transition-colors">
              {f.icon}
            </div>
            <h3 className="font-semibold text-base text-gray-900 mb-1.5">{f.title}</h3>
            <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-8 text-center">Jak działa platforma?</h2>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          {[
            { label: 'Załącz tekst',       sub: 'wklej lub wgraj plik' },
            { label: 'Analiza NLP + AI',    sub: 'model + stylometria' },
            { label: 'Raport z wynikami',   sub: 'eksport JSON / PDF' },
          ].map((step, i) => (
            <div key={step.label} className="flex items-center gap-4">
              <div className="flex flex-col items-center text-center w-28">
                <div className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center font-bold text-sm mb-2">
                  {i + 1}
                </div>
                <span className="text-sm font-medium text-gray-800">{step.label}</span>
                <span className="text-xs text-gray-400 mt-0.5">{step.sub}</span>
              </div>
              {i < 2 && (
                <svg className="hidden md:block text-gray-300 flex-shrink-0" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}