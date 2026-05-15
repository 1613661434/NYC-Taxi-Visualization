<template>
  <ChartCard title="24小时出行趋势" subtitle="各时段订单量变化（体现早/晚高峰）" :large="true">
    <div ref="chartDom" class="chart"></div>
  </ChartCard>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import * as echarts from 'echarts'

const props = defineProps({ data: Object })
const chartDom = ref(null)
let chart = null

const render = () => {
  if (!chartDom.value || !props.data) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  const hourly = Object.entries(props.data.hourly_trend || {}).sort((a, b) => a[0] - b[0])
  const values = hourly.map(d => d[1])
  chart.setOption({
    animationDuration: 1500,
    animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross', crossStyle: { color: '#64748B' } } },
    grid: { top: 40, right: 30, bottom: 30, left: 50 },
    xAxis: { type: 'category', data: hourly.map(d => d[0] + ':00'), axisLabel: { fontSize: 10 },
      axisLine: { lineStyle: { color: '#6b3a2a' } } },
    yAxis: { type: 'value', name: '订单量(单)', nameTextStyle: { fontSize: 11 },
      splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } } },
    series: [{
      data: values, type: 'line', smooth: true,
      symbol: 'emptyCircle', symbolSize: 8,
      lineStyle: { width: 3, color: '#2f7b9e' },
      itemStyle: { color: '#2f7b9e', borderColor: '#2f7b9e', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(91,155,213,0.4)' },
          { offset: 1, color: 'rgba(91,155,213,0.02)' },
        ]),
      },
      label: { show: true, position: 'top', fontSize: 10, fontWeight: 'bold',
        formatter: p => p.value >= 1000 ? (p.value / 1000).toFixed(1) + 'k' : p.value },
      emphasis: { focus: 'series', itemStyle: { shadowBlur: 10, shadowColor: 'rgba(91,155,213,0.5)' } },
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
