import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatCurrency } from '../../utils/currency.js'

export default function SpendingTrendChart({ data, gradientId = 'spending' }) {
  return <div className="chart-area"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}>
    <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2BE82A" stopOpacity={.28} /><stop offset="100%" stopColor="#2BE82A" stopOpacity={0} /></linearGradient></defs>
    <CartesianGrid stroke="#292929" vertical={false} /><XAxis dataKey="day" tick={{ fill: '#8F8F8F', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(value) => value % 5 === 1 ? `Oct ${value}` : ''} /><YAxis tick={{ fill: '#8F8F8F', fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} width={45} />
    <Tooltip contentStyle={{ background: '#202020', border: '1px solid #373737', borderRadius: 10, color: '#fff' }} formatter={(value) => formatCurrency(value)} />
    <Area type="monotone" dataKey="amount" stroke="#2BE82A" strokeWidth={2.5} fill={`url(#${gradientId})`} />
  </AreaChart></ResponsiveContainer></div>
}
