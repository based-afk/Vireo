import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  return <div className="app-shell">
    <button className="mobile-menu" onClick={() => setMobileOpen((open) => !open)} aria-label={mobileOpen ? 'Close navigation' : 'Open navigation'}>
      {mobileOpen ? <X /> : <Menu />}
    </button>
    <div className={mobileOpen ? 'sidebar-wrap open' : 'sidebar-wrap'}><Sidebar onNavigate={() => setMobileOpen(false)} /></div>
    <main className="main-content"><Outlet /></main>
  </div>
}
