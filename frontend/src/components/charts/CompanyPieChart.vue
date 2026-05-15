<template>
  <ChartCard title="车型订单占比" subtitle="黄色出租车 vs 绿色出租车">
    <div ref="chartDom" class="chart"></div>
    <template #extra>
      <div class="stats-row">
        <div class="stat-badge yellow">黄车: {{ yellow.toLocaleString() }}单</div>
        <div class="stat-badge green">绿车: {{ green.toLocaleString() }}单</div>
      </div>
    </template>
  </ChartCard>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import * as echarts from 'echarts'

const props = defineProps({ data: Object })
const chartDom = ref(null)
let chart = null
const company = computed(() => props.data?.company_compare || {})
const yellow = computed(() => company.value?.黄色出租车 || 0)
const green = computed(() => company.value?.绿色出租车 || 0)

const render = () => {
  if (!chartDom.value) return
  if (!chart) { chart = echarts.init(chartDom.value, 'vintage-warm'); doRender() }
  else doRender()
}

const doRender = () => {
  chart.setOption({
    animationDuration: 1200, animationEasing: 'elasticOut',
    tooltip: { trigger: 'item', formatter: '{b}: {c}单 ({d}%)' },
    series: [{
      type: 'pie', radius: ['58%', '80%'], center: ['50%', '48%'], roseType: 'radius',
      itemStyle: { borderRadius: 8, borderColor: 'rgba(15,23,42,0.8)', borderWidth: 5 },
      label: { show: true, position: 'outside', formatter: '{b}\n{d}%', fontSize: 12, fontWeight: 'bold' },
      labelLine: { lineStyle: { color: '#64748B' } },
      emphasis: { scaleSize: 10, label: { fontSize: 16 } },
      data: [
        { name: '黄色出租车', value: yellow.value, itemStyle: { color: '#c23531' } },
        { name: '绿色出租车', value: green.value, itemStyle: { color: '#4a7c59' } },
      ],
    }],
  })
}

watch(() => props.data, render, { deep: true })
onMounted(() => { render() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>
.chart { width: 100%; height: 260px; }
.stats-row { display: flex; justify-content: center; gap: 16px; margin-top: 8px; }
.stat-badge { padding: 4px 16px; border-radius: 16px; font-size: 12px; font-weight: 600; }
.stat-badge.yellow { background: rgba(237,125,49,0.15); color: #c23531; }
.stat-badge.green { background: rgba(112,173,71,0.15); color: #4a7c59; }
</style>
