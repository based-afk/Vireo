export default function EmptyState({ icon: Icon, title, message }) {
  return <div className="empty-state"><Icon size={25} /><strong>{title}</strong><span>{message}</span></div>
}
