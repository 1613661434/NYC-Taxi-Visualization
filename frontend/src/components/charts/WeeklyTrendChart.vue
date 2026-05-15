<template>
  <ChartCard title="一周出行规律" subtitle="周一至周日订单量变化" :large="true">
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
  if (!chartDom.value) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  const week = Object.entries(props.data?.weekday_trend || {}).sort((a,b) => a[0]-b[0])
  const weekNames = ['周一','周二','周三','周四','周五','周六','周日']
  const values = week.map(d=>d[1])
  chart.setOption({
    animationDuration: 1400, animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis' },
    grid: { top: 40, right: 20, bottom: 30, left: 50 },
    xAxis: { type: 'category', data: weekNames, axisLabel: { fontSize: 11, fontWeight: 'bold' }, axisLine: { lineStyle: { color: '#6b3a2a' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } } },
    series: [{
      data: values, type: 'line', smooth: true,
      symbol: 'roundRect', symbolSize: 10,
      lineStyle: { width: 3, color: '#9b59b6' },
      itemStyle: { color: '#9b59b6' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(155,124,212,0.35)'},{offset:1,color:'rgba(155,124,212,0.02)'}]) },
      label: { show: true, position: 'top', fontSize: 10, fontWeight: 'bold', formatter: p=>p.value>=1000?(p.value/1000).toFixed(1)+'k':p.value },
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
