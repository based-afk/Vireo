import axios from 'axios'
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api', headers: { 'Content-Type': 'application/json' } })
export async function createTransaction(payload) {
  const { data } = await api.post('/transactions', payload)
  return data.transaction
}
export async function getTransactions() {
  const { data } = await api.get('/transactions')
  return data.transactions
}
export async function previewPdfImport(file, password = '') {
  const formData = new FormData()
  formData.append('file', file)
  if (password && password.trim()) {
    formData.append('password', password.trim())
  }
  const { data } = await api.post('/imports/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

