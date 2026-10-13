import { ArrowLeftRight } from 'lucide-react'
import EmptyState from '../ui/EmptyState.jsx'
import TransactionRow from './TransactionRow.jsx'

export default function TransactionTable({ transactions }) {
  return <div className="table-wrap"><table><thead><tr><th>TRANSACTION</th><th>CATEGORY</th><th>DATE</th><th>TYPE</th><th className="right">AMOUNT</th></tr></thead><tbody>
    {transactions.length === 0 ? <tr><td colSpan="5"><EmptyState icon={ArrowLeftRight} title="No transactions yet" message="Add your first transaction to get started." /></td></tr> : transactions.map((transaction) => <TransactionRow key={transaction.id} transaction={transaction} />)}
  </tbody></table></div>
}
