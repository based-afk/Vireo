import { NavLink } from 'react-router-dom'
import { ArrowLeftRight, ChartNoAxesCombined, ChevronDown, FileUp, Home, Settings as SettingsIcon } from 'lucide-react'

const navigation = [
  { to: '/', label: 'Dashboard', icon: Home },
  { to: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
  { to: '/import', label: 'Import', icon: FileUp },
  { to: '/analytics', label: 'Analytics', icon: ChartNoAxesCombined },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
]

export default function Sidebar({ onNavigate }) {
  return <aside className="sidebar">
    <NavLink to="/" className="brand" onClick={onNavigate}>
      <span className="brand-name">VIREO <i /></span>
      <span className="brand-subtitle">PERSONAL FINANCE</span>
    </NavLink>
    <nav className="nav-list">{navigation.map(({ to, label, icon: Icon }) => (
      <NavLink key={to} to={to} end={to === '/'} onClick={onNavigate} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
        <Icon size={20} /><span>{label}</span>
      </NavLink>
    ))}</nav>
    <div className="sidebar-bottom">
      <div className="budget-card"><span className="eyebrow">MONTHLY BUDGET</span><div className="budget-ring"><span>68%</span></div><strong>₹34,200 <small>/ ₹50,000</small></strong></div>
      <div className="profile"><div className="avatar">SB</div><div className="profile-copy"><strong>Your account</strong><span>Personal account</span></div><ChevronDown size={16} /></div>
    </div>
  </aside>
}
