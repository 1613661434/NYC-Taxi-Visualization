<template>
  <ChartCard title="黄色 vs 绿色 核心指标对比" subtitle="平均费用($) / 平均距离(mi) / 平均小费($)">
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
  const comp = props.data?.yellow_green_comparison || {}
  const yf=comp.平均费用?.['黄色出租车']||0, gf=comp.平均费用?.['绿色出租车']||0
  const yd=comp.平均距离?.['黄色出租车']||0, gd=comp.平均距离?.['绿色出租车']||0
  const yt=comp.平均小费?.['黄色出租车']||0, gt=comp.平均小费?.['绿色出租车']||0
  chart.setOption({
    animationDuration: 1000, animationEasing: 'cubicOut',
    tooltip: { trigger: 'axis' },
    legend: { data:['黄色出租车','绿色出租车'], top:0, right:0 },
    grid: { top:40, right:20, bottom:30, left:50 },
    xAxis: { type:'category', data:['平均费用($)','平均距离(mi)','平均小费($)'], name:'指标', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
    yAxis: { type:'value', name:'数值', nameLocation:'center', nameGap:40, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
    series: [
      { name: '黄色出租车', type: 'bar', barWidth: '35%', data: [yf,yd,yt], itemStyle: { borderRadius: [6,6,0,0], color: '#e6b422' }, label: { show: true, position: 'top', formatter: p=>p.value.toFixed(1) }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(230,180,34,0.4)' } } },
      { name: '绿色出租车', type: 'bar', barWidth: '35%', data: [gf,gd,gt], itemStyle: { borderRadius: [6,6,0,0], color: '#4a7c59' }, label: { show: true, position: 'top', formatter: p=>p.value.toFixed(1) }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(112,173,71,0.4)' } } },
    ],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 260px; }</style>
