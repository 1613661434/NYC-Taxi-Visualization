<template>
  <ChartCard title="支付方式对比" subtitle="信用卡 vs 现金 vs 其他">
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
  const payment = props.data?.payment_dist || {}
  const colors = ['#2f7b9e','#c23531','#4a7c59','#9b59b6','#61a0a8']
  chart.setOption({
    animationDuration: 1000, animationEasing: 'elasticOut',
    tooltip: { trigger: 'item', formatter: '{b}: {c}单 ({d}%)' },
    series: [{
      type: 'pie', radius: ['50%','72%'], center: ['50%','50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 6, borderColor: 'rgba(15,23,42,0.8)', borderWidth: 4 },
      label: { show: true, fontSize: 11 },
      emphasis: { scaleSize: 8 },
      data: Object.entries(payment).map(([n,v],i) => ({ name: n, value: v, itemStyle: { color: colors[i%colors.length] } })),
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>.chart { width: 100%; height: 260px; }</style>
