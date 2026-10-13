import { useState } from 'react'
import { X } from 'lucide-react'
import { initialTransaction } from '../../hooks/useTransactions.js'

const categories = ['Food & Dining', 'Shopping', 'Transport', 'Bills & Utilities', 'Entertainment', 'Healthcare', 'Groceries', 'Education', 'Transfers', 'Income', 'Others']

export default function TransactionDialog({ open, onClose, submitTransaction, saving }) {
  const [form, setForm] = useState(initialTransaction)
  if (!open) return null
  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  async function submit(event) {
    event.preventDefault()
    const transaction = await submitTransaction(form)
    if (transaction) { setForm(initialTransaction()); onClose() }
  }
  return <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><form className="modal" onSubmit={submit}>
    <div className="modal-header"><div><h2>Add transaction</h2><p>Save a transaction to your finance tracker.</p></div><button type="button" className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={19} /></button></div>
    <label>Title<input name="title" value={form.title} onChange={update} placeholder="e.g. Lunch at Swiggy" required maxLength="120" /></label>
    <div className="form-grid"><label>Amount (INR)<input name="amount" type="number" min="0.01" step="0.01" value={form.amount} onChange={update} placeholder="250.00" required /></label><label>Type<select name="type" value={form.type} onChange={update}><option value="EXPENSE">Expense</option><option value="INCOME">Income</option></select></label></div>
    <div className="form-grid"><label>Category<select name="category" value={form.category} onChange={update}>{categories.map((category) => <option key={category}>{category}</option>)}</select></label><label>Date<input name="date" type="date" value={form.date} onChange={update} required /></label></div>
    <div className="modal-actions"><button type="button" className="outline-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save transaction'}</button></div>
  </form></div>
}
