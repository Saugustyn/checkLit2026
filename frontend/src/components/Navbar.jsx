import { NavLink } from 'react-router-dom'

const Logo = () => (
  <div className="flex items-center gap-2.5">
    {/* Monogram mark */}
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="8" fill="#2d6a4f"/>
      <path d="M8 10h10M8 16h7M8 22h10" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <path d="M20 14l3 3-3 3" stroke="#86efac" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
    {/* Wordmark */}
    <span className="font-bold text-lg tracking-tight text-gray-900">
      check<span className="text-primary-600">Lit</span>
    </span>
  </div>
)

const navItems = [
  { to: '/',        label: 'Start'     },
  { to: '/analyze', label: 'Analiza'   },
  { to: '/history', label: 'Historia'  },
  { to: '/compare', label: 'Porównaj'  },
  { to: '/about',   label: 'O platformie' },
]

export default function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <NavLink to="/" className="flex-shrink-0">
          <Logo />
        </NavLink>
        <div className="flex items-center gap-1">
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}