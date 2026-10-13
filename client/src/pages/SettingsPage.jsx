import PageHeader from '../components/layout/PageHeader.jsx'

export default function SettingsPage() {
  return <><PageHeader title="Settings" description="Manage your preferences and personal finance setup." /><div className="settings-grid">
    <article className="panel settings-card"><h2>Appearance</h2><p>Customize the look of Moneta.</p><div className="settings-line"><div><strong>Theme</strong><small>Dark mode is the current default.</small></div><span className="category-pill">Dark</span></div></article>
    <article className="panel settings-card"><h2>Preferences</h2><p>Set up your financial defaults.</p><div className="settings-line"><div><strong>Currency</strong><small>Currency used throughout the app.</small></div><span className="category-pill">INR (₹)</span></div><div className="settings-line"><div><strong>Monthly budget</strong><small>Target spending limit.</small></div><strong>₹50,000</strong></div></article>
    <article className="panel settings-card"><h2>Privacy</h2><p>Your financial data should stay yours.</p><div className="settings-line"><div><strong>SMS import</strong><small>Not enabled in this version.</small></div><span className="muted">Coming later</span></div></article>
  </div></>
}
