import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dates.js'

export default function TransactionRow({ transaction }) {
  const income = transaction.type === 'INCOME'
  return <tr><td><strong>{transaction.title}</strong></td><td><span className="category-pill">{transaction.category}</span></td><td>{formatDate(transaction.date)}</td><td><span className={income ? 'positive' : 'muted'}>{income ? 'Income' : 'Expense'}</span></td><td className={`right ${income ? 'positive' : 'amount'}`}>{income ? '+' : '−'}{formatCurrency(Number(transaction.amount))}</td></tr>
}
