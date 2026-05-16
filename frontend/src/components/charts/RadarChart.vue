<template>
  <ChartCard title="多维性能雷达" subtitle="黄车 vs 绿车 核心指标对比">
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
    animationDuration: 1200,
    legend: { data:['黄色出租车','绿色出租车'], left:'center', top:0 },
    radar: {
      center:['50%','55%'], radius:'65%', shape:'circle',
      axisName: { fontSize:11 },
      splitArea: { areaStyle: { color:['rgba(210,130,100,0.05)','rgba(210,130,100,0.1)'] } },
      splitLine: { lineStyle: { color:'#d4c4a8' } },
      axisLine: { lineStyle: { color:'#d4c4a8' } },
      indicator: [
        { name:'平均费用($)', max:Math.max(yf,gf)*1.5||20 },
        { name:'平均距离(mi)', max:Math.max(yd,gd)*1.5||4 },
        { name:'平均小费($)', max:Math.max(yt,gt)*1.5||3 },
        { name:'效率评分', max:100 },
      ],
    },
    series: [{
      type: 'radar',
      data: [
        { value:[yf,yd,yt,85], name:'黄色出租车', areaStyle:{color:'rgba(230,180,34,0.25)'}, lineStyle:{color:'#e6b422',width:2}, itemStyle:{color:'#e6b422'}, symbol:'circle', symbolSize:5 },
        { value:[gf,gd,gt,78], name:'绿色出租车', areaStyle:{color:'rgba(74,124,89,0.25)'}, lineStyle:{color:'#4a7c59',width:2}, itemStyle:{color:'#4a7c59'}, symbol:'circle', symbolSize:5 },
      ],
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; width: 80%; height: 380px; margin: 0 auto; }</style>
