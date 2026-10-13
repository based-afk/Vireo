import { useState } from 'react'
import { Plus, Search } from 'lucide-react'
import PageHeader from '../components/layout/PageHeader.jsx'
import TransactionDialog from '../components/transactions/TransactionDialog.jsx'
import TransactionTable from '../components/transactions/TransactionTable.jsx'
import useTransactions from '../hooks/useTransactions.js'

export default function TransactionsPage() {
  const [open, setOpen] = useState(false)
  const { transactions, error, success, loading, saving, addTransaction, clearMessages } = useTransactions()
  const showDialog = () => { clearMessages(); setOpen(true) }
  return <><PageHeader title="Transactions" description="Every transaction, organized in one place." actions={<button className="primary-button" onClick={showDialog}><Plus size={17} /> Add transaction</button>} />
    {success && <div className="notice success">{success}</div>}{error && <div className="notice error">{error}</div>}
    <article className="panel transactions-panel"><div className="panel-heading"><div><h2>All transactions</h2><p>Newly created transactions appear here for this session.</p></div><button className="outline-button"><Search size={16} /> Search</button></div>{loading ? <div className="empty-state"><strong>Loading transactions…</strong></div> : <TransactionTable transactions={transactions} />}</article>
    <TransactionDialog open={open} onClose={() => setOpen(false)} submitTransaction={addTransaction} saving={saving} />
  </>
}
