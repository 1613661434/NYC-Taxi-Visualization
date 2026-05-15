<template>
  <ChartCard title="乘客数量分布" subtitle="1~6人订单占比">
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
  const passengers = Object.entries(props.data?.passenger_dist || {}).sort((a,b) => a[0]-b[0])
  const values = passengers.map(p => p[1])
  const maxV = Math.max(...values, 1)
  chart.setOption({
    animationDuration: 800, animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis' },
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    xAxis: { type: 'category', data: passengers.map(p => p[0]+'人'), axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } } },
    series: [{
      data: values.map((v,i) => ({ value: v, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#c23531'},{offset:1,color:'#ca6924'}]) } })),
      type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [6,6,0,0] },
      label: { show: true, position: 'top', fontWeight: 'bold', formatter: p=>p.value.toLocaleString() },
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
