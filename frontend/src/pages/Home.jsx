import { Link } from 'react-router-dom'

const features = [
  {
    icon: '🤖',
    title: 'Detekcja AI',
    desc: 'Wykrywa fragmenty generowane przez modele językowe AI z określeniem prawdopodobieństwa.',
  },
  {
    icon: '📊',
    title: 'Stylometria',
    desc: 'Analizuje TTR, n-gramy, długość zdań, entropię i bogactwo słownikowe.',
  },
  {
    icon: '✍️',
    title: 'Jakość językowa',
    desc: 'Ocenia czytelność (Flesch), gęstość leksykalną i strukturę tekstu.',
  },
  {
    icon: '🔍',
    title: 'Porównanie',
    desc: 'Zestawia dwa teksty stylometrycznie, generując raport podobieństwa.',
  },
]

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-14">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          Literary Analyzer
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          Platforma do automatycznej analizy autentyczności i stylu tekstów literackich.
          Łączy algorytmy NLP, stylometrię i modele AI.
        </p>
        <Link
          to="/analyze"
          className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors text-lg"
        >
          Analizuj tekst →
        </Link>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-14">
        {features.map((f) => (
          <div key={f.title} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">{f.icon}</div>
            <h3 className="font-bold text-lg text-gray-900 mb-2">{f.title}</h3>
            <p className="text-gray-600 text-sm">{f.desc}</p>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Jak działa platforma?</h2>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          {['Wklej tekst', 'Analiza NLP + AI', 'Raport z wynikami'].map((step, i) => (
            <div key={step} className="flex items-center gap-4">
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-primary-500 text-white flex items-center justify-center font-bold">
                  {i + 1}
                </div>
                <span className="text-sm text-gray-600 mt-2 text-center w-24">{step}</span>
              </div>
              {i < 2 && <div className="hidden md:block text-gray-300 text-2xl">→</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
