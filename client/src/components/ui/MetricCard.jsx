export default function MetricCard({ icon: Icon, label, value, change, tone = 'green', bars = [5, 8, 6, 10, 9, 12, 14, 11] }) {
  return <article className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={21} /></div><div className="metric-copy"><span>{label}</span><strong>{value}</strong><small className={tone === 'red' ? 'negative' : 'positive'}>{change}</small></div><div className="mini-bars">{bars.map((height, index) => <i key={index} style={{ height: `${height * 3}px` }} />)}</div></article>
}
