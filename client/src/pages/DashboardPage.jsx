import { Activity, ArrowDownLeft, CalendarDays, ChevronDown, CreditCard, Plus, Wallet } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import PageHeader from '../components/layout/PageHeader.jsx'
import MetricCard from '../components/ui/MetricCard.jsx'
import ChartCard from '../components/ui/ChartCard.jsx'
import SpendingTrendChart from '../components/analytics/SpendingTrendChart.jsx'
import CategoryBreakdownChart from '../components/analytics/CategoryBreakdownChart.jsx'
import MonthlyComparisonChart from '../components/analytics/MonthlyComparisonChart.jsx'
import TopMerchants from '../components/analytics/TopMerchants.jsx'
import { categories, monthly, trend } from '../data/mockAnalytics.js'

const recent = [['Swiggy', 'Food & Dining', 'Today', '-₹520', 'expense'], ['Monthly stipend', 'Income', 'Yesterday', '+₹12,000', 'income'], ['Namma Metro', 'Transport', 'Oct 11', '-₹120', 'expense'], ['Spotify Premium', 'Entertainment', 'Oct 10', '-₹119', 'expense']]

function RecentTransactions() {
  return <div className="recent-list">{recent.map(([title, category, date, amount, type]) => <div className="recent-row" key={title}><div className="transaction-symbol">{title.slice(0, 1)}</div><div className="recent-description"><strong>{title}</strong><small>{category} · {date}</small></div><strong className={type === 'income' ? 'positive' : 'amount'}>{amount}</strong></div>)}</div>
}

export default function DashboardPage() {
  return <><PageHeader title="Dashboard" description="Here's your financial overview." actions={<><button className="outline-button"><CalendarDays size={16} /> This month <ChevronDown size={15} /></button><NavLink className="primary-button" to="/transactions"><Plus size={17} /> Add transaction</NavLink></>} />
    <section className="metric-grid"><MetricCard icon={Wallet} label="Total Income" value="₹42,000" change="↗ 12% vs last month" bars={[4, 6, 5, 8, 7, 10, 12, 14]} /><MetricCard icon={ArrowDownLeft} label="Total Expenses" value="₹28,450" change="↓ 8% vs last month" tone="red" bars={[12, 10, 13, 8, 9, 6, 5, 4]} /><MetricCard icon={CreditCard} label="Net Savings" value="₹13,550" change="↗ 28% vs last month" bars={[5, 6, 7, 8, 7, 11, 12, 14]} /><MetricCard icon={Activity} label="Savings Rate" value="32%" change="↗ 6% vs last month" bars={[5, 7, 6, 8, 10, 9, 12, 14]} /></section>
    <section className="dashboard-grid"><ChartCard title="Cash Flow" description="Income and expenses at a glance." actions={<button className="outline-button compact">30 days <ChevronDown size={14} /></button>}><SpendingTrendChart data={trend} gradientId="cashFlow" /></ChartCard><ChartCard title="Spending by Category" description="Where your money goes."><CategoryBreakdownChart data={categories} legendData={categories.slice(0, 5)} total={28450} /></ChartCard></section>
    <section className="dashboard-grid bottom-grid"><ChartCard title="Recent Transactions" description="Your latest financial activity." actions={<NavLink to="/transactions" className="text-link">View all →</NavLink>}><RecentTransactions /></ChartCard><ChartCard title="Monthly Comparison" description="Income vs expenses."><MonthlyComparisonChart data={monthly} /></ChartCard></section>
  </>
}
