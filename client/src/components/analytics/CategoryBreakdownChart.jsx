import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { formatCurrency } from '../../utils/currency.js'

export default function CategoryBreakdownChart({ data, legendData = data, total, totalLabel = 'Total spent', className = '' }) {
  const displayedTotal = total ?? data.reduce((sum, category) => sum + category.value, 0)
  return <div className={`category-chart ${className}`}><div className="donut"><ResponsiveContainer width="100%" height="100%"><PieChart>
    <Pie data={data} dataKey="value" nameKey="name" innerRadius="64%" outerRadius="96%" paddingAngle={1} stroke="none">{data.map((category) => <Cell key={category.name} fill={category.color} />)}</Pie>
    <Tooltip contentStyle={{ background: '#202020', border: '1px solid #373737', borderRadius: 10, color: '#fff' }} formatter={(value) => formatCurrency(value)} />
  </PieChart></ResponsiveContainer><div className="donut-center"><strong>{formatCurrency(displayedTotal)}</strong><span>{totalLabel}</span></div></div>
    <div className="category-legend">{legendData.map((category) => <div key={category.name} className="legend-row"><i style={{ background: category.color }} /><span>{category.name}</span><strong>{formatCurrency(category.value)}</strong></div>)}</div>
  </div>
}
