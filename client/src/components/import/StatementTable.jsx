import { useState, useMemo } from 'react'
import {
  ArrowDownLeft,
  ArrowUpRight,
  Receipt,
  Scale,
  AlertTriangle,
  Info,
} from 'lucide-react'
import StatementRow from './StatementRow.jsx'
import { formatINR } from '../../utils/currency.js'

export default function StatementTable({ statement, filename }) {
  const [filter, setFilter] = useState('ALL') // 'ALL' | 'VALID' | 'NEEDS_REVIEW'

  const {
    transactions = [],
    summary = {
      total_transactions: 0,
      valid_count: 0,
      needs_review_count: 0,
      total_withdrawals: 0,
      total_deposits: 0,
      net_change: 0,
    },
    format_detected = 'Standard Bank Statement',
    parsing_warnings = [],
  } = statement || {}

  const filteredTransactions = useMemo(() => {
    if (filter === 'VALID') {
      return transactions.filter((t) => t.status === 'valid')
    }
    if (filter === 'NEEDS_REVIEW') {
      return transactions.filter((t) => t.status === 'needs_review')
    }
    return transactions
  }, [transactions, filter])

  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      {/* Financial Summary Metrics Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px',
        }}
      >
        {/* Total Transactions */}
        <div
          style={{
            background: '#141414',
            border: '1px solid #282828',
            borderRadius: '14px',
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#1f1f1f',
              display: 'grid',
              placeItems: 'center',
              color: '#d4d4d4',
            }}
          >
            <Receipt size={20} />
          </div>
          <div>
            <span style={{ fontSize: '11px', color: '#888', display: 'block' }}>
              TOTAL TRANSACTIONS
            </span>
            <strong style={{ fontSize: '20px', color: '#fff' }}>
              {summary.total_transactions}
            </strong>
            <small style={{ display: 'block', color: '#888', fontSize: '10px', marginTop: '2px' }}>
              {summary.valid_count} valid · {summary.needs_review_count} review
            </small>
          </div>
        </div>

        {/* Total Withdrawals (Expenses) */}
        <div
          style={{
            background: '#141414',
            border: '1px solid #282828',
            borderRadius: '14px',
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#301719',
              display: 'grid',
              placeItems: 'center',
              color: '#ff9297',
            }}
          >
            <ArrowDownLeft size={20} />
          </div>
          <div>
            <span style={{ fontSize: '11px', color: '#888', display: 'block' }}>
              TOTAL WITHDRAWALS
            </span>
            <strong style={{ fontSize: '20px', color: '#ff9297' }}>
              {formatINR(summary.total_withdrawals)}
            </strong>
            <small style={{ display: 'block', color: '#888', fontSize: '10px', marginTop: '2px' }}>
              {summary.statement_total_withdrawals !== null && summary.statement_total_withdrawals !== undefined
                ? (summary.statement_total_withdrawals === summary.total_withdrawals
                    ? '✓ matches statement total'
                    : `stmt total: ${formatINR(summary.statement_total_withdrawals)}`)
                : 'from valid rows only'}
            </small>
          </div>
        </div>

        {/* Total Deposits (Income) */}
        <div
          style={{
            background: '#141414',
            border: '1px solid #282828',
            borderRadius: '14px',
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: '#122616',
              display: 'grid',
              placeItems: 'center',
              color: 'var(--green)',
            }}
          >
            <ArrowUpRight size={20} />
          </div>
          <div>
            <span style={{ fontSize: '11px', color: '#888', display: 'block' }}>
              TOTAL DEPOSITS
            </span>
            <strong style={{ fontSize: '20px', color: 'var(--green)' }}>
              {formatINR(summary.total_deposits)}
            </strong>
            <small style={{ display: 'block', color: '#888', fontSize: '10px', marginTop: '2px' }}>
              {summary.statement_total_deposits !== null && summary.statement_total_deposits !== undefined
                ? (summary.statement_total_deposits === summary.total_deposits
                    ? '✓ matches statement total'
                    : `stmt total: ${formatINR(summary.statement_total_deposits)}`)
                : 'from valid rows only'}
            </small>
          </div>
        </div>

        {/* Net Change */}
        <div
          style={{
            background: '#141414',
            border: '1px solid #282828',
            borderRadius: '14px',
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: summary.net_change >= 0 ? '#122616' : '#301719',
              display: 'grid',
              placeItems: 'center',
              color: summary.net_change >= 0 ? 'var(--green)' : '#ff9297',
            }}
          >
            <Scale size={20} />
          </div>
          <div>
            <span style={{ fontSize: '11px', color: '#888', display: 'block' }}>
              NET BALANCE CHANGE
            </span>
            <strong
              style={{
                fontSize: '20px',
                color: summary.net_change >= 0 ? 'var(--green)' : '#ff9297',
              }}
            >
              {summary.net_change >= 0 ? '+' : ''}
              {formatINR(summary.net_change)}
            </strong>
            <small style={{ display: 'block', color: '#888', fontSize: '10px', marginTop: '2px' }}>
              deposits minus withdrawals
            </small>
          </div>
        </div>
      </div>

      {/* Warnings Banner if any */}
      {parsing_warnings.length > 0 || summary.needs_review_count > 0 ? (
        <div
          style={{
            background: '#241a0b',
            border: '1px solid #573a11',
            borderRadius: '12px',
            padding: '12px 16px',
            color: '#ffc875',
            fontSize: '12px',
            display: 'flex',
            gap: '12px',
            alignItems: 'flex-start',
          }}
        >
          <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: '2px', color: '#ffb347' }} />
          <div>
            <strong style={{ display: 'block', marginBottom: '2px' }}>
              Parsing Advisory ({summary.needs_review_count} row{summary.needs_review_count !== 1 ? 's' : ''} require review)
            </strong>
            {parsing_warnings.map((w, idx) => (
              <span key={idx} style={{ display: 'block', lineHeight: 1.4 }}>
                {w}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {/* Preview Notice Disclaimer */}
      <div
        style={{
          background: '#161616',
          border: '1px solid #282828',
          borderRadius: '10px',
          padding: '10px 14px',
          color: '#aaa',
          fontSize: '11px',
          display: 'flex',
          gap: '8px',
          alignItems: 'center',
        }}
      >
        <Info size={15} style={{ flexShrink: 0, color: 'var(--green)' }} />
        <span>
          <strong>Extraction Preview:</strong> Displaying parsed transactions from <code>{filename}</code> ({format_detected}). Data is in-memory only and has not been saved or categorized.
        </span>
      </div>

      {/* Table Panel */}
      <div className="panel transactions-panel">
        <div
          className="panel-heading"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <h2>Extracted Statement Transactions</h2>
            <p>
              Showing {filteredTransactions.length} of {transactions.length} rows
            </p>
          </div>

          {/* Segmented Filter Buttons */}
          <div className="segmented">
            <button
              type="button"
              className={filter === 'ALL' ? 'selected' : ''}
              onClick={() => setFilter('ALL')}
            >
              All ({transactions.length})
            </button>
            <button
              type="button"
              className={filter === 'VALID' ? 'selected' : ''}
              onClick={() => setFilter('VALID')}
            >
              Valid ({summary.valid_count})
            </button>
            {summary.needs_review_count > 0 ? (
              <button
                type="button"
                className={filter === 'NEEDS_REVIEW' ? 'selected' : ''}
                onClick={() => setFilter('NEEDS_REVIEW')}
                style={{
                  color: filter === 'NEEDS_REVIEW' ? '#061806' : '#ffb347',
                  fontWeight: 600,
                }}
              >
                Needs Review ({summary.needs_review_count})
              </button>
            ) : null}
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th style={{ width: '120px' }}>TXN DATE</th>
                <th>NARRATION</th>
                <th style={{ width: '100px' }}>TYPE</th>
                <th className="right" style={{ width: '130px' }}>WITHDRAWAL</th>
                <th className="right" style={{ width: '130px' }}>DEPOSIT</th>
                <th className="right" style={{ width: '140px' }}>CLOSING BALANCE</th>
                <th style={{ width: '140px' }}>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '36px 20px', color: '#888' }}>
                    No transactions match the selected filter.
                  </td>
                </tr>
              ) : (
                filteredTransactions.map((tx) => (
                  <StatementRow key={tx.row_number} transaction={tx} />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
