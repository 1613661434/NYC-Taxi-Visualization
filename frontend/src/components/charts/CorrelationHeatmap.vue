<template>
  <ChartCard title="数值字段相关性热力图" subtitle="行程距离、费用、小费、乘客数等相关系数" :large="true">
    <div ref="chartDom" class="chart"></div>
  </ChartCard>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import * as echarts from 'echarts'

const props = defineProps({ data: Object, advanced: Boolean })
const chartDom = ref(null)
let chart = null

const render = () => {
  if (!chartDom.value || !props.data) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  const corrData = props.advanced ? props.data.pearson : props.data.correlation
  if (!corrData) return
  const rename = (s) => s === '修正后总费用' ? '总费用' : s
  const rawFields = Object.keys(corrData)
  const fields = rawFields.map(rename)
  const values = []
  for (let i=0;i<fields.length;i++) for(let j=0;j<fields.length;j++) values.push([j,i,corrData[rawFields[i]]?.[rawFields[j]]||0])
  chart.setOption({
    animationDuration: 800,
    tooltip: { position: 'top', formatter: p => `${fields[p.data[0]]} × ${fields[p.data[1]]}<br/>r = <b>${p.data[2].toFixed(3)}</b>` },
    grid: { top: 5, right: 20, bottom: 60, left: 80 },
    xAxis: { type: 'category', data: fields, axisLabel: { rotate: 30, fontSize: 9 }, position: 'bottom', name:'字段', nameLocation:'center', nameGap:10, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
    yAxis: { type: 'category', data: fields, axisLabel: { fontSize: 9 }, name:'字段', nameLocation:'center', nameGap:60, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
    visualMap: { min: -1, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 5,
      inRange: { color: ['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#ffffbf','#fee090','#fdae61','#f46d43','#d73027','#a50026'] } },
    series: [{ type: 'heatmap', data: values, label: { show: true, formatter: p=>p.data[2].toFixed(2), fontSize: 9 }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 380px; }</style>
