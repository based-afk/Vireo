export default function ChartCard({ title, description, actions, children, className = '' }) {
  return <article className={`panel ${className}`}><div className="panel-heading"><div><h2>{title}</h2><p>{description}</p></div>{actions}</div>{children}</article>
}
