const Section = ({ title, children }) => (
  <div className="mb-8">
    <h2 className="text-xl font-bold text-gray-900 mb-3 border-b border-gray-200 pb-2">{title}</h2>
    {children}
  </div>
)

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">O platformie</h1>
      <p className="text-gray-500 mb-10">
        Literary Analyzer to platforma do automatycznej analizy autentyczności i stylu tekstów literackich,
        zrealizowana jako praca inżynierska.
      </p>

      <Section title="🎯 Cel platformy">
        <p className="text-gray-700 leading-relaxed">
          Platforma umożliwia wykrywanie fragmentów tekstów generowanych przez modele AI
          oraz ocenę ich wartości językowej i stylometrycznej. Może być stosowana przez
          wydawnictwa, instytucje naukowe i edukacyjne w celu ochrony treści autorskich.
        </p>
      </Section>

      <Section title="🧮 Algorytmy">
        <div className="space-y-3 text-sm text-gray-700">
          <div className="bg-gray-50 rounded-lg p-4">
            <strong>Detekcja AI</strong> – model <code>roberta-base-openai-detector</code> (HuggingFace Transformers).
            Klasyfikator binarny trenowany na próbkach tekstów ludzkich i AI.
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <strong>Type-Token Ratio (TTR)</strong> – stosunek liczby unikalnych słów do wszystkich słów.
            Miara bogactwa leksykalnego tekstu.
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <strong>Entropia Shannona</strong> – mierzy nieprzewidywalność rozkładu słów.
            Wyższa wartość oznacza bardziej zróżnicowane słownictwo.
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <strong>Flesch Reading Ease</strong> – wskaźnik czytelności oparty na długości zdań i sylab.
            Zakres 0-100; wyższy = łatwiejszy w odbiorze.
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <strong>N-gramy</strong> – analiza najczęściej współwystępujących sekwencji słów (bigramy).
            Ujawnia powtarzające się wzorce stylistyczne.
          </div>
        </div>
      </Section>

      <Section title="🛠️ Stack technologiczny">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-semibold text-gray-700 mb-2">Backend</p>
            <ul className="space-y-1 text-gray-600">
              <li>🐍 Python 3.11</li>
              <li>⚡ FastAPI</li>
              <li>🗄️ SQLite + SQLAlchemy</li>
              <li>🤗 Hugging Face Transformers</li>
              <li>🧪 Pytest</li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-gray-700 mb-2">Frontend</p>
            <ul className="space-y-1 text-gray-600">
              <li>⚛️ React.js 18</li>
              <li>⚡ Vite</li>
              <li>💨 Tailwind CSS</li>
              <li>📊 Recharts</li>
              <li>🔗 Axios</li>
            </ul>
          </div>
        </div>
      </Section>

      <Section title="📡 API Documentation">
        <p className="text-gray-700 text-sm">
          Pełna dokumentacja API dostępna jest pod adresem{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
             className="text-primary-600 hover:underline">
            localhost:8000/docs
          </a>{' '}
          (Swagger UI generowany automatycznie przez FastAPI).
        </p>
      </Section>
    </div>
  )
}
