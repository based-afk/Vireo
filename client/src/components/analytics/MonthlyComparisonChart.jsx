import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatCurrency } from '../../utils/currency.js'

export default function MonthlyComparisonChart({ data }) {
  return <div className="chart-area short"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} barGap={4}>
    <CartesianGrid stroke="#292929" vertical={false} /><XAxis dataKey="month" tick={{ fill: '#8F8F8F', fontSize: 11 }} tickLine={false} axisLine={false} /><YAxis tick={{ fill: '#8F8F8F', fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} width={42} />
    <Tooltip contentStyle={{ background: '#202020', border: '1px solid #373737', borderRadius: 10, color: '#fff' }} formatter={(value) => formatCurrency(value)} />
    <Bar dataKey="income" fill="#2BE82A" radius={[4, 4, 0, 0]} /><Bar dataKey="expenses" fill="#9BE49B" radius={[4, 4, 0, 0]} />
  </BarChart></ResponsiveContainer></div>
}
