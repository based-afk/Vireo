import { ArrowUpRight, CalendarDays, ChevronDown, CreditCard, Wallet } from 'lucide-react'
import PageHeader from '../components/layout/PageHeader.jsx'
import MetricCard from '../components/ui/MetricCard.jsx'
import ChartCard from '../components/ui/ChartCard.jsx'
import SpendingTrendChart from '../components/analytics/SpendingTrendChart.jsx'
import CategoryBreakdownChart from '../components/analytics/CategoryBreakdownChart.jsx'
import MonthlyComparisonChart from '../components/analytics/MonthlyComparisonChart.jsx'
import TopMerchants from '../components/analytics/TopMerchants.jsx'
import { categories, merchants, monthly, trend } from '../data/mockAnalytics.js'

export default function AnalyticsPage() {
  return <><PageHeader title="Analytics" description="Understand your spending patterns and track your financial progress." actions={<><button className="outline-button"><CalendarDays size={16} /> Oct 1 – Oct 31, 2026 <ChevronDown size={15} /></button><div className="range-switch"><button>7D</button><button className="selected">30D</button><button>3M</button><button>1Y</button><button>All</button></div></>} />
    <section className="metric-grid"><MetricCard icon={Wallet} label="Total Income" value="₹42,000" change="↗ +12% vs last month" bars={[5, 6, 7, 10, 8, 11, 13, 15]} /><MetricCard icon={ArrowUpRight} label="Total Expenses" value="₹28,450" change="↓ -8% vs last month" tone="red" bars={[13, 10, 12, 8, 9, 6, 5, 4]} /><MetricCard icon={CreditCard} label="Net Savings" value="₹13,550" change="↗ +28% vs last month" bars={[5, 7, 6, 9, 8, 12, 11, 15]} /><MetricCard icon={Wallet} label="Savings Rate" value="32%" change="↗ +6% vs last month" bars={[5, 7, 8, 7, 10, 9, 12, 14]} /></section>
    <section className="dashboard-grid analytics-grid"><ChartCard title="Spending Trend" description="Your daily spending over the selected period." actions={<button className="outline-button compact">Expenses <ChevronDown size={14} /></button>}><SpendingTrendChart data={trend} /></ChartCard><ChartCard title="Expenses by Category" description="Breakdown of your spending." actions={<div className="segmented"><button className="selected">Amount</button><button>Percentage</button></div>}><CategoryBreakdownChart data={categories} totalLabel="Total Spent" className="analytics-category" /></ChartCard></section>
    <section className="dashboard-grid bottom-grid"><ChartCard title="Top Merchants" description="Your most frequent spending destinations."><TopMerchants merchants={merchants} /></ChartCard><ChartCard title="Monthly Comparison" description="Income vs Expenses over the last 6 months." actions={<div className="chart-legend"><span><i className="income-dot" />Income</span><span><i className="expense-dot" />Expenses</span></div>}><MonthlyComparisonChart data={monthly} /></ChartCard></section>
  </>
}
