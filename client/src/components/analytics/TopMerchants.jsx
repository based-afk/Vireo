import { formatCurrency } from '../../utils/currency.js'

export default function TopMerchants({ merchants }) {
  return <div className="merchant-list">{merchants.map((merchant, index) => <div className="merchant-row" key={merchant.name}>
    <span className="rank">{index + 1}</span><span className="merchant-mark">{merchant.mark}</span><div className="merchant-name"><strong>{merchant.name}</strong><small>{merchant.count}</small></div>
    <div className="merchant-bar"><i style={{ width: `${merchant.amount / merchants[0].amount * 100}%` }} /></div><strong className="merchant-amount">{formatCurrency(merchant.amount)}</strong>
  </div>)}</div>
}
