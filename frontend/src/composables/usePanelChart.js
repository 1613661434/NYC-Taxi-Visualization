import { nextTick } from 'vue'
import * as echarts from 'echarts'

/**
 * 统一的面板图表渲染工具
 * 用法: const { loadData, renderChart } = usePanelChart()
 *        await loadData(fetchFn, params)
 *        renderChart(ref, (chart) => { chart.setOption({...}) })
 */
export function usePanelChart() {
  const charts = {}

  const initChart = (domRef) => {
    if (!domRef?.value) return null
    const key = domRef.value
    if (charts[key]) return charts[key]
    const instance = echarts.init(domRef.value)
    charts[key] = instance
    return instance
  }

  const disposeAll = () => {
    Object.values(charts).forEach(c => c?.dispose())
    Object.keys(charts).forEach(k => delete charts[k])
  }

  return { initChart, disposeAll }
}
