import { Link, useLocation } from 'react-router-dom'

const navLinks = [
  { path: '/',        label: 'Strona główna' },
  { path: '/analyze', label: 'Analizuj' },
  { path: '/compare', label: 'Porównaj' },
  { path: '/history', label: 'Historia' },
  { path: '/about',   label: 'O platformie' },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="text-xl font-bold text-primary-600">
          📖 Literary Analyzer
        </Link>

        {/* Linki nawigacyjne */}
        <ul className="flex gap-1">
          {navLinks.map(({ path, label }) => (
            <li key={path}>
              <Link
                to={path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  )
}
