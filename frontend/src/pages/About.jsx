const Section = ({ title, icon, children }) => (
  <div className="mb-8">
    <h2 className="text-lg font-bold text-gray-900 mb-3 border-b border-gray-200 pb-2 flex items-center gap-2">
      <span className="text-primary-600">{icon}</span>
      {title}
    </h2>
    {children}
  </div>
)

const StackIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary-500 flex-shrink-0 mt-0.5">
    <circle cx="12" cy="12" r="3"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
  </svg>
)

const sectionIcons = {
  cel: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  algorytmy: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
    </svg>
  ),
  stack: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
    </svg>
  ),
  api: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
    </svg>
  ),
}

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">O platformie</h1>
      <p className="text-gray-500 mb-10">
        checkLit to platforma do automatycznej analizy autentyczności i stylu tekstów literackich,
        zrealizowana jako praca inżynierska.
      </p>

      <Section title="Cel platformy" icon={sectionIcons.cel}>
        <p className="text-gray-700 leading-relaxed">
          Platforma umożliwia wykrywanie fragmentów tekstów generowanych przez modele AI
          oraz ocenę ich wartości językowej i stylometrycznej. Może być stosowana przez
          wydawnictwa, instytucje naukowe i edukacyjne w celu ochrony treści autorskich.
        </p>
      </Section>

      <Section title="Algorytmy" icon={sectionIcons.algorytmy}>
        <div className="space-y-2 text-sm text-gray-700">
          {[
            {
              label: 'Detekcja AI',
              desc: <>Model <code className="bg-gray-100 px-1 rounded text-xs">roberta-base-openai-detector</code> (HuggingFace Transformers). Klasyfikator binarny z rekalibrowanymi progami na własnym korpusie 80 tekstów (AUC = 0.90): <span className="text-primary-700 font-medium">human &lt; 32</span>, <span className="text-yellow-700 font-medium">strefa szara 32–41</span>, <span className="text-red-700 font-medium">AI &gt; 41</span>.</>,
            },
            {
              label: 'Type-Token Ratio (TTR)',
              desc: 'Stosunek liczby unikalnych słów do wszystkich słów. Miara bogactwa leksykalnego tekstu.',
            },
            {
              label: 'Entropia Shannona',
              desc: 'Mierzy nieprzewidywalność rozkładu słów. Wyższa wartość oznacza bardziej zróżnicowane słownictwo.',
            },
            {
              label: 'LIX (Läsbarhetsindex)',
              desc: 'Neutralny językowo wskaźnik czytelności oparty na długości zdań i odsetku długich słów (>6 znaków). Zastąpił Flesch Reading Ease, który dawał zaniżone wyniki dla polszczyzny.',
            },
            {
              label: 'N-gramy',
              desc: 'Analiza najczęściej współwystępujących sekwencji słów (bigramy). Ujawnia powtarzające się wzorce stylistyczne.',
            },
          ].map(({ label, desc }) => (
            <div key={label} className="bg-gray-50 border border-gray-100 rounded-lg p-4">
              <span className="font-semibold text-gray-900">{label}</span>
              <span className="text-gray-600"> — {desc}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Stack technologiczny" icon={sectionIcons.stack}>
        <div className="grid grid-cols-2 gap-6 text-sm">
          <div>
            <p className="font-semibold text-gray-700 mb-3 text-xs uppercase tracking-wide">Backend</p>
            <ul className="space-y-2 text-gray-600">
              {['Python 3.11', 'FastAPI', 'SQLite + SQLAlchemy', 'Hugging Face Transformers', 'scikit-learn + scipy', 'Pytest'].map(item => (
                <li key={item} className="flex items-center gap-2">
                  <StackIcon />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="font-semibold text-gray-700 mb-3 text-xs uppercase tracking-wide">Frontend</p>
            <ul className="space-y-2 text-gray-600">
              {['React.js 18', 'Vite', 'Tailwind CSS', 'Recharts', 'Axios'].map(item => (
                <li key={item} className="flex items-center gap-2">
                  <StackIcon />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      <Section title="API Documentation" icon={sectionIcons.api}>
        <p className="text-gray-700 text-sm">
          Pełna dokumentacja API dostępna jest pod adresem{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
             className="text-primary-600 hover:underline font-medium">
            localhost:8000/docs
          </a>{' '}
          (Swagger UI generowany automatycznie przez FastAPI).
        </p>
      </Section>
    </div>
  )
}