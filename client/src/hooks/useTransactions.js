import { useEffect, useState } from 'react'
import { createTransaction, getTransactions } from '../api.js'
import { today } from '../utils/dates.js'

export const initialTransaction = () => ({ title: '', amount: '', type: 'EXPENSE', category: 'Food & Dining', date: today() })

export default function useTransactions() {
  const [transactions, setTransactions] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    async function loadTransactions() {
      try {
        const loadedTransactions = await getTransactions()
        if (active) setTransactions(loadedTransactions)
      } catch (requestError) {
        if (active) setError(requestError.response?.data?.error || (typeof requestError.response?.data?.detail === 'string' ? requestError.response?.data?.detail : null) || 'Could not load transactions. Check that the API and database are running.')
      } finally {
        if (active) setLoading(false)
      }
    }
    loadTransactions()
    return () => { active = false }
  }, [])

  async function addTransaction(form) {
    setSaving(true)
    setError('')
    setSuccess('')
    try {
      const transaction = await createTransaction({ ...form, amount: Number(form.amount) })
      setTransactions((current) => [transaction, ...current])
      setSuccess('Transaction saved to PostgreSQL.')
      return transaction
    } catch (requestError) {
      setError(requestError.response?.data?.error || (typeof requestError.response?.data?.detail === 'string' ? requestError.response?.data?.detail : null) || 'Could not save transaction. Check that the API and database are running.')
      return null
    } finally {
      setSaving(false)
    }
  }

  return { transactions, error, success, loading, saving, addTransaction, clearMessages: () => { setError(''); setSuccess('') } }
}
