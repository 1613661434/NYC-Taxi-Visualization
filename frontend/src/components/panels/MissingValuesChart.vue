<template>
  <ChartCard title="各字段缺失值比例" subtitle="横向柱状图 - 颜色从绿(低)到红(高)">
    <div ref="chartDom" class="chart"></div>
  </ChartCard>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick} from 'vue'
import ChartCard from '../common/ChartCard.vue'
import * as echarts from 'echarts'

const props = defineProps({ data: Object })
const chartDom = ref(null)
let chart = null

const render = () => {
  if (!chartDom.value) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  const cols = props.data?.columns || []
  const pcts = props.data?.missing_pcts || {}
  const items = cols.map(c => ({ name: c, pct: pcts[c] || 0 })).sort((a, b) => b.pct - a.pct)
  chart.setOption({
    grid: { containLabel: true, left: 140, top: 20, bottom: 20 },
    xAxis: { type: 'value', name: '缺失率 (%)', max: 100 },
    yAxis: { type: 'category', data: items.map(d => d.name), axisLabel: { fontSize: 11 } },
    series: [{
      data: items.map(d => ({
        value: d.pct,
        itemStyle: { color: `hsl(${(1 - d.pct / 100) * 120}, 70%, 50%)` }
      })),
      type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', formatter: (p) => p.value.toFixed(1) + '%' }
    }]
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
