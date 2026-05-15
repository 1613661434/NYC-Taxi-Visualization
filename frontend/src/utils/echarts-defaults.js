// 统一柔和的 DataV 风格配色
export const palette = {
  blue: '#5B9BD5',
  orange: '#ED7D31',
  green: '#70AD47',
  red: '#E06666',
  purple: '#9B7CD4',
  cyan: '#4ECDC4',
  yellow: '#FFD166',
}

export const paletteList = [palette.blue, palette.orange, palette.green, palette.red, palette.purple, palette.cyan, palette.yellow]

// 深色主题轴默认配置 — 清晰但不刺眼
export function axisStyle() {
  return {
    xAxis: {
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94A3B8', fontSize: 11 },
      splitLine: { show: false },
      nameTextStyle: { color: '#64748B', fontSize: 12 },
    },
    yAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#94A3B8', fontSize: 11 },
      splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
      nameTextStyle: { color: '#64748B', fontSize: 12 },
    },
  }
}

// 通用 tooltip 风格
export function tooltipStyle() {
  return {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    borderColor: '#334155',
    textStyle: { color: '#E2E8F0', fontSize: 12 },
    extraCssText: 'border-radius:8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);',
  }
}

// 饼图色盘
export const pieColors = [palette.blue, palette.orange, palette.green, palette.purple, palette.cyan, palette.red, palette.yellow]

// 通用 grid 配置
export function gridStyle() {
  return { top: 20, right: 30, bottom: 30, left: 50, containLabel: true }
}
