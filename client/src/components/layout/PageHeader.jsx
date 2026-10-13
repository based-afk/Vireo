export default function PageHeader({ title, description, actions }) {
  return <header className="page-header"><div><h1>{title}</h1><p>{description}</p></div><div className="header-actions">{actions}</div></header>
}
