<template>
  <ChartCard title="行政区热度排行 TOP5" subtitle="按订单量排序">
    <div ref="chartDom" class="chart"></div>
  </ChartCard>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import * as echarts from 'echarts'

const props = defineProps({ data: Object })
const emit = defineEmits(['drill-down'])
const chartDom = ref(null)
let chart = null

const render = () => {
  if (!chartDom.value) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  const borough = Object.entries(props.data?.borough_dist || {}).sort((a,b) => b[1]-a[1]).slice(0,5)
  chart.setOption({
    animationDuration: 1000, animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 90, right: 60, top: 10, bottom: 10 },
    xAxis: { type: 'value', axisLabel: { formatter: v => v>=1000?(v/1000).toFixed(1)+'k':v } },
    yAxis: { type: 'category', data: borough.map(d=>d[0]).reverse(), axisLabel: { fontSize: 12, fontWeight: 'bold' }, axisLine: { show: false }, axisTick: { show: false } },
    series: [{
      data: borough.map(d=>d[1]).reverse(), type: 'bar', barWidth: '55%',
      itemStyle: {
        borderRadius: [0,8,8,0],
        color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#61a0a8'},{offset:1,color:'#2f7b9e'}]),
      },
      label: { show: true, position: 'right', fontWeight: 'bold', formatter: p=>p.value>=1000?(p.value/1000).toFixed(1)+'k':p.value },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(91,155,213,0.4)' } },
    }],
  })
  chart.off('click')
  chart.on('click', params => { if(params.name) emit('drill-down','borough',params.name) })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 300px; }</style>
