<template>
  <div>
    <div class="info-card">
      <div class="info-icon">ℹ️</div>
      <div class="info-text">
        <strong>缺失值分析：</strong>对清洗后数据各字段进行缺失值检测。当前数据经清洗后较为干净。
      </div>
    </div>
    <div class="chart-row" v-if="ready">
      <ChartCard title="各字段缺失值比例" subtitle="横向柱状图">
        <div ref="chart1" class="chart"></div>
      </ChartCard>
    </div>
    <div class="chart-row" v-if="ready && columns.length > 0">
      <ChartCard title="按车型缺失值对比" subtitle="黄色 vs 绿色">
        <div ref="chart2" class="chart"></div>
      </ChartCard>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">加载中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchMissingValues } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false)
const columns = ref([])
const missingData = ref(null)
const chart1 = ref(null)
const chart2 = ref(null)
let c1 = null, c2 = null

const load = async () => {
  try {
    missingData.value = await fetchMissingValues({
      start_month: props.startMonth, end_month: props.endMonth,
      company: props.filters.company, borough: props.filters.borough,
    })
  } catch (e) { console.error(e) }
  ready.value = true
  await nextTick()
  renderChart1()
  renderChart2()
}

const renderChart1 = () => {
  if (!chart1.value || !missingData.value) return
  if (!c1) c1 = echarts.init(chart1.value, 'vintage-warm')
  const cols = missingData.value.columns || []
  const pcts = missingData.value.missing_pcts || {}
  const items = cols.map(c => ({ name: c, pct: pcts[c] || 0 })).sort((a, b) => b.pct - a.pct)
  c1.setOption({
    grid: { containLabel: true, left: 140, top: 20, bottom: 20 },
    xAxis: { type: 'value', name: '缺失率 (%)', max: 100 },
    yAxis: { type: 'category', data: items.map(d => d.name), axisLabel: { fontSize: 11 } },
    series: [{
      data: items.map(d => ({ value: d.pct,
        itemStyle: { color: `hsl(${(1 - d.pct / 100) * 120}, 70%, 50%)` } })),
      type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', formatter: (p) => p.value.toFixed(1) + '%' },
    }],
  })
}

const renderChart2 = () => {
  if (!chart2.value || !missingData.value) return
  const cols = missingData.value.columns || []
  if (!cols.length) return
  if (!c2) c2 = echarts.init(chart2.value, 'vintage-warm')
  const bt = missingData.value.by_taxi_type || {}
  const types = Object.keys(bt[cols[0]] || {})
  c2.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cols, axisLabel: { rotate: 20, fontSize: 10 } },
    yAxis: { type: 'value', name: '缺失数量' },
    series: types.map((t, i) => ({
      name: t, type: 'bar',
      data: cols.map(c => (bt[c] || {})[t] || 0),
      color: ['#c23531', '#4a7c59'][i],
    })),
    legend: { data: types, textStyle: { color: '#5c3d2e' }, top: 0 },
  })
}

watch([() => props.filters, () => props.startMonth, () => props.endMonth], () => load(), { deep: true })
onMounted(load)
onUnmounted(() => { c1?.dispose(); c2?.dispose() })
</script>

<style scoped>
.info-card {
  background: rgba(139,69,19,0.08); border-left: 4px solid #568aea;
  border-radius: 16px; padding: 14px 20px; margin-bottom: 24px;
  display: flex; gap: 12px; align-items: flex-start;
}
.info-icon { font-size: 20px; }
.info-text { font-size: 12px; color: #8b7355; line-height: 1.5; }
.info-text strong { color: #8b4513; }
.chart-row { display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.chart-row > * { flex: 1; min-width: 280px; }
.chart { width: 100%; height: 260px; }
</style>
