import { useState } from 'react'
import { CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import { formatINR } from '../../utils/currency.js'
import { formatDate } from '../../utils/dates.js'

export default function StatementRow({ transaction }) {
  const [expanded, setExpanded] = useState(false)
  const isNeedsReview = transaction.status === 'needs_review'
  const isIncome = transaction.type === 'INCOME'
  const isExpense = transaction.type === 'EXPENSE'

  const formattedDate = transaction.date
    ? formatDate(transaction.date)
    : transaction.original_date || 'Invalid Date'

  const isLongNarration = transaction.narration && transaction.narration.length > 55

  return (
    <tr
      style={{
        background: isNeedsReview ? 'rgba(255, 179, 71, 0.05)' : undefined,
        borderLeft: isNeedsReview ? '3px solid #ffb347' : '3px solid transparent',
      }}
    >
      <td style={{ verticalAlign: 'top', whiteSpace: 'nowrap' }}>
        <strong>{formattedDate}</strong>
        {transaction.original_date && transaction.original_date !== formattedDate ? (
          <small style={{ display: 'block', color: '#888', fontSize: '10px' }}>
            {transaction.original_date}
          </small>
        ) : null}
      </td>

      <td style={{ verticalAlign: 'top', minWidth: '220px', maxWidth: '360px', whiteSpace: 'normal' }}>
        <div style={{ wordBreak: 'break-word', lineHeight: 1.4 }}>
          {isLongNarration && !expanded ? (
            <>
              {transaction.narration.slice(0, 55)}…{' '}
              <button
                type="button"
                onClick={() => setExpanded(true)}
                style={{
                  background: 'transparent',
                  border: 0,
                  color: 'var(--green)',
                  fontSize: '11px',
                  padding: 0,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '2px',
                }}
              >
                more <ChevronDown size={11} />
              </button>
            </>
          ) : (
            <>
              {transaction.narration}
              {isLongNarration ? (
                <button
                  type="button"
                  onClick={() => setExpanded(false)}
                  style={{
                    marginLeft: '6px',
                    background: 'transparent',
                    border: 0,
                    color: '#999',
                    fontSize: '11px',
                    padding: 0,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '2px',
                  }}
                >
                  less <ChevronUp size={11} />
                </button>
              ) : null}
            </>
          )}
        </div>
      </td>

      <td style={{ verticalAlign: 'top', whiteSpace: 'nowrap' }}>
        {isIncome ? (
          <span
            className="category-pill"
            style={{ color: 'var(--green)', borderColor: '#24472b', background: '#122616' }}
          >
            Income
          </span>
        ) : isExpense ? (
          <span
            className="category-pill"
            style={{ color: '#ff9297', borderColor: '#59282b', background: '#301719' }}
          >
            Expense
          </span>
        ) : (
          <span
            className="category-pill"
            style={{ color: '#ffc875', borderColor: '#6b4e18', background: '#2b2111' }}
          >
            Unknown
          </span>
        )}
      </td>

      <td className="right" style={{ verticalAlign: 'top', whiteSpace: 'nowrap' }}>
        {transaction.withdrawal > 0 ? (
          <span style={{ color: '#ff9297' }}>
            {formatINR(transaction.withdrawal)}
          </span>
        ) : (
          <span className="muted">—</span>
        )}
      </td>

      <td className="right" style={{ verticalAlign: 'top', whiteSpace: 'nowrap' }}>
        {transaction.deposit > 0 ? (
          <span className="positive">
            {formatINR(transaction.deposit)}
          </span>
        ) : (
          <span className="muted">—</span>
        )}
      </td>

      <td className="right" style={{ verticalAlign: 'top', whiteSpace: 'nowrap' }}>
        {transaction.closing_balance !== null && transaction.closing_balance !== undefined ? (
          <strong style={{ color: '#e7e7e7' }}>
            {formatINR(transaction.closing_balance)}
          </strong>
        ) : (
          <span className="muted">—</span>
        )}
      </td>

      <td style={{ verticalAlign: 'top', minWidth: '130px' }}>
        {isNeedsReview ? (
          <div style={{ display: 'grid', gap: '3px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontSize: '11px',
                color: '#ffb347',
                fontWeight: 600,
              }}
            >
              <AlertTriangle size={13} /> Needs Review
            </span>
            {transaction.issues?.map((issue, idx) => (
              <span key={idx} style={{ color: '#ff9297', fontSize: '10px', lineHeight: 1.2 }}>
                • {issue}
              </span>
            ))}
          </div>
        ) : (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '11px',
              color: 'var(--green)',
            }}
          >
            <CheckCircle2 size={13} /> Verified
          </span>
        )}
      </td>
    </tr>
  )
}
