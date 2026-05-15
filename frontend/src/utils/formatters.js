export function formatNumber(num) {
  if (num === undefined || num === null) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

export function formatPercent(num) {
  if (num === undefined || num === null) return '0%'
  return num.toFixed(1) + '%'
}

export function formatDollar(num) {
  if (num === undefined || num === null) return '$0'
  return '$' + num.toFixed(1)
}
