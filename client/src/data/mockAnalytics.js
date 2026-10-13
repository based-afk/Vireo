// Illustrative analytics remain mock data until read-only analytics endpoints exist.
export const categories = [
  { name: 'Food & Dining', value: 8420, color: '#2BE82A' },
  { name: 'Shopping', value: 5680, color: '#75D875' },
  { name: 'Transport', value: 4230, color: '#9BE49B' },
  { name: 'Bills & Utilities', value: 3920, color: '#FFFFFF' },
  { name: 'Entertainment', value: 2450, color: '#A6A6A6' },
  { name: 'Healthcare', value: 1750, color: '#707070' },
  { name: 'Others', value: 2000, color: '#454545' },
]

export const trend = Array.from({ length: 31 }, (_, index) => ({
  day: index + 1,
  amount: [850, 1200, 1350, 1750, 1750, 1250, 800, 1300, 1500, 1500, 2050, 2050, 2100, 2900, 3300, 2850, 2550, 2700, 2450, 3100, 3400, 2950, 2550, 2250, 2000, 2400, 3100, 3420, 3250, 3750, 4200][index],
}))

export const monthly = [
  { month: 'May', income: 42000, expenses: 28000 },
  { month: 'Jun', income: 46000, expenses: 31000 },
  { month: 'Jul', income: 47000, expenses: 28000 },
  { month: 'Aug', income: 46000, expenses: 33000 },
  { month: 'Sep', income: 54000, expenses: 39000 },
  { month: 'Oct', income: 68000, expenses: 48000 },
]

export const merchants = [
  { name: 'Swiggy', count: '18 transactions', amount: 5240, mark: 'S' },
  { name: 'Amazon', count: '12 transactions', amount: 4380, mark: 'a' },
  { name: 'Spotify', count: '6 transactions', amount: 2450, mark: '♫' },
  { name: 'Namma Metro', count: '14 transactions', amount: 2130, mark: 'M' },
  { name: 'BESCOM', count: '5 transactions', amount: 1820, mark: 'ϟ' },
]
