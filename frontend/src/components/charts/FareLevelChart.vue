<template>
  <ChartCard title="行程费用等级分布" subtitle="各价格区间订单数">
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
  const fare = Object.entries(props.data?.fare_level_dist || {})
  chart.setOption({
    animationDuration: 800, animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis' },
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    xAxis: { type: 'category', data: fare.map(d=>d[0]), axisLabel: { fontSize: 10, rotate: 15 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } } },
    series: [{
      data: fare.map(d=>d[1]), type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [6,6,0,0], color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#4a7c59'},{offset:1,color:'#61a0a8'}]) },
      label: { show: true, position: 'top', fontWeight: 'bold', formatter: p=>p.value.toLocaleString() },
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
