<template>
  <div>
    <div class="info-card">
      <div class="info-icon">⏱️</div>
      <div class="info-text"><strong>时间线动态比对：</strong>随时间推移观察订单量、小费率、距离、费用的变化趋势与增幅减幅，可切换 按月/按小时/按周 粒度。</div>
    </div>

    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">加载中...</div>
    <template v-else>
      <TimelinePlayer
        :buckets="buckets" :granularity="granularity"
        @update:granularity="g => granularity = g"
        @index-change="idx => currentIndex = idx"
      />

      <!-- 指标选择 -->
      <div class="metric-bar">
        <button v-for="m in metrics" :key="m.key" :class="{ active: metric === m.key }" @click="metric = m.key">{{ m.label }}</button>
      </div>

      <!-- 当前时段 KPI + 增幅减幅 -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">{{ curBucket?.label || '-' }}</div>
          <div class="kpi-sub">当前时段</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-number">{{ curBucket?.total_trips?.toLocaleString() || 0 }}</div>
          <div class="kpi-delta" :class="deltaClass('total_trips')">{{ deltaText('total_trips') }}</div>
          <div class="kpi-sub">订单量</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-number">{{ curBucket?.avg_tip_pct || 0 }}%</div>
          <div class="kpi-delta" :class="deltaClass('avg_tip_pct')">{{ deltaText('avg_tip_pct') }}</div>
          <div class="kpi-sub">小费率</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-number">{{ curBucket?.avg_distance || 0 }} mi</div>
          <div class="kpi-delta" :class="deltaClass('avg_distance')">{{ deltaText('avg_distance') }}</div>
          <div class="kpi-sub">平均距离</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-number">${{ curBucket?.avg_fare || 0 }}</div>
          <div class="kpi-delta" :class="deltaClass('avg_fare')">{{ deltaText('avg_fare') }}</div>
          <div class="kpi-sub">平均费用</div>
        </div>
      </div>

      <!-- 订单量 — 黄绿分开两张图 -->
      <div class="chart-row" v-if="metric === 'trips'">
        <ChartCard title="黄色出租车 — 订单量趋势" subtitle="各时段订单量变化">
          <div ref="c1" class="chart" style="height:320px;"></div>
        </ChartCard>
        <ChartCard title="绿色出租车 — 订单量趋势" subtitle="各时段订单量变化">
          <div ref="c2" class="chart" style="height:320px;"></div>
        </ChartCard>
      </div>
      <div class="chart-explain" v-if="metric === 'trips'">
        <strong>📖 怎么看：</strong>黄绿分开对比，更能看清各自的变化规律。黄车订单量远大于绿车，放在同一坐标下绿车趋势会被压缩。当前 <em>{{ curBucket?.label }}</em> 相比上一时段订单量{{ deltaDesc }}。
      </div>

      <!-- 其他指标 — 单图 -->
      <div class="chart-row" v-else>
        <ChartCard :title="currentMetricLabel + '趋势'" subtitle="各时段变化" :large="true">
          <div ref="c1" class="chart" style="height:380px;"></div>
          <div class="chart-explain">
            <strong>📖 怎么看：</strong>点击 ▶ 播放观察数据随时间变化。<em>{{ currentMetricLabel }} 波动反映了出行需求的时空规律</em>。
            当前 <em>{{ curBucket?.label }}</em> 相比上一时段{{ deltaDesc }}。
          </div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import TimelinePlayer from '../common/TimelinePlayer.vue'
import { fetchTimelineData } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), buckets = ref([]), granularity = ref('monthly'), currentIndex = ref(0), metric = ref('trips')
const c1 = ref(null), c2 = ref(null)
let chart = null, chart2 = null

const metrics = [
  { key: 'trips', label: '订单量', yellow: 'yellow', green: 'green', unit: '单' },
  { key: 'tip', label: '小费率', yellow: 'yellow_tip', green: 'green_tip', unit: '%' },
  { key: 'distance', label: '距离', yellow: 'yellow_dist', green: 'green_dist', unit: 'mi' },
  { key: 'fare', label: '费用', yellow: 'yellow_fare', green: 'green_fare', unit: '$' },
]

const currentMetricLabel = computed(() => metrics.find(m => m.key === metric.value)?.label || '')
const curBucket = computed(() => buckets.value[currentIndex.value] || {})

// 增幅减幅计算
const getDelta = (field) => {
  if (currentIndex.value < 1) return null
  const cur = buckets.value[currentIndex.value]?.[field]
  const prev = buckets.value[currentIndex.value - 1]?.[field]
  if (!cur || !prev || prev === 0) return null
  return ((cur - prev) / prev * 100)
}

const deltaText = (field) => {
  const d = getDelta(field)
  if (d === null) return '—'
  const sign = d >= 0 ? '↑' : '↓'
  return `${sign} ${Math.abs(d).toFixed(1)}%`
}

const deltaClass = (field) => {
  const d = getDelta(field)
  if (d === null) return ''
  return d >= 0 ? 'delta-up' : 'delta-down'
}

const deltaDesc = computed(() => {
  const field = metric.value === 'trips' ? 'total_trips' : metric.value === 'tip' ? 'avg_tip_pct' : metric.value === 'distance' ? 'avg_distance' : 'avg_fare'
  const d = getDelta(field)
  if (d === null) return '（数据不足）'
  const dir = d >= 0 ? '增长' : '下降'
  return `${dir} ${Math.abs(d).toFixed(1)}%`
})

const load = async () => {
  ready.value = false
  try {
    const res = await fetchTimelineData({
      granularity: granularity.value,
      start_month: props.startMonth, end_month: props.endMonth,
      company: props.filters.company, borough: props.filters.borough,
    })
    buckets.value = res.buckets || []
    currentIndex.value = 0
  } catch (e) { console.error(e) }
  ready.value = true
  await nextTick()
  renderChart()
}

const commonGrid = { top: 40, right: 20, bottom: 25, left: 50 }
const commonX = (labels) => ({
  type: 'category', data: labels,
  axisLabel: granularity.value === 'hourly' ? { rotate: 45, fontSize: 9 } : { fontSize: 9 },
  name: granularity.value === 'monthly' ? '月份' : granularity.value === 'hourly' ? '小时' : '周',
  nameLocation: 'center', nameGap: 22,
  nameTextStyle: { fontSize: 11, color: '#5c3d2e', fontWeight: 'bold' }
})

const renderChart = () => {
  if (!buckets.value.length) return
  const labels = buckets.value.map(b => b.label)

  if (metric.value === 'trips') {
    // 黄绿分开两张图
    if (c1.value) {
      if (chart) chart.dispose()
      chart = echarts.init(c1.value, 'vintage-warm')
      const yellowData = buckets.value.map(b => b.yellow)
      chart.setOption({
        tooltip: { trigger: 'axis', formatter: p => `<b>${p[0].axisValue}</b><br/>🟡 黄色出租车：${Number(p[0].value).toLocaleString()} 单` },
        grid: commonGrid,
        xAxis: commonX(labels),
        yAxis: { type: 'value', name: '单', nameTextStyle: { fontSize: 11, color: '#5c3d2e', fontWeight: 'bold' } },
        series: [
          { type: 'line', data: yellowData, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { color: '#e6b422', width: 2.5 }, itemStyle: { color: '#e6b422' }, areaStyle: { color: 'rgba(230,180,34,0.12)' }, markLine: { silent: true, symbol: 'none', lineStyle: { color: '#c23531', type: 'solid', width: 2 }, data: [{ xAxis: currentIndex.value, label: { formatter: labels[currentIndex.value], fontSize: 10, color: '#c23531', fontWeight: 'bold' } }] } },
        ],
      })
    }
    if (c2.value) {
      if (chart2) chart2.dispose()
      chart2 = echarts.init(c2.value, 'vintage-warm')
      const greenData = buckets.value.map(b => b.green)
      chart2.setOption({
        tooltip: { trigger: 'axis', formatter: p => `<b>${p[0].axisValue}</b><br/>🟢 绿色出租车：${Number(p[0].value).toLocaleString()} 单` },
        grid: commonGrid,
        xAxis: commonX(labels),
        yAxis: { type: 'value', name: '单', nameTextStyle: { fontSize: 11, color: '#5c3d2e', fontWeight: 'bold' } },
        series: [
          { type: 'line', data: greenData, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { color: '#4a7c59', width: 2.5 }, itemStyle: { color: '#4a7c59' }, areaStyle: { color: 'rgba(74,124,89,0.12)' }, markLine: { silent: true, symbol: 'none', lineStyle: { color: '#c23531', type: 'solid', width: 2 }, data: [{ xAxis: currentIndex.value, label: { formatter: labels[currentIndex.value], fontSize: 10, color: '#c23531', fontWeight: 'bold' } }] } },
        ],
      })
    }
  } else {
    // 其他指标单图
    if (!c1.value) return
    if (chart) chart.dispose()
    chart = echarts.init(c1.value, 'vintage-warm')
    let data, unit
    if (metric.value === 'tip') { data = buckets.value.map(b => b.avg_tip_pct); unit = '%' }
    else if (metric.value === 'distance') { data = buckets.value.map(b => b.avg_distance); unit = 'mi' }
    else { data = buckets.value.map(b => b.avg_fare); unit = '$' }

    chart.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => { let h = `<b>${params[0].axisValue}</b><br/>`; params.forEach(p => { if (p.value != null) h += `${p.marker} ${p.seriesName}：${Number(p.value).toLocaleString()} ${unit}<br/>` }); return h } },
      legend: { data: [currentMetricLabel.value], top: 5, textStyle: { color: '#5c3d2e' } },
      grid: { top: 40, right: 20, bottom: 30, left: 55 },
      xAxis: commonX(labels),
      yAxis: { type: 'value', name: unit, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
      series: [{ name: currentMetricLabel.value, type: 'line', data, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { color: '#568aea', width: 3 }, itemStyle: { color: '#568aea' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(86,138,234,0.3)' }, { offset: 1, color: 'rgba(86,138,234,0.02)' }]) }, markLine: { silent: true, symbol: 'none', lineStyle: { color: '#c23531', type: 'solid', width: 2 }, data: [{ xAxis: currentIndex.value, label: { formatter: labels[currentIndex.value], fontSize: 10, color: '#c23531', fontWeight: 'bold' } }] } }],
    })
  }
}

const highlightCurrent = () => {
  const label = buckets.value[currentIndex.value]?.label || ''
  const lineData = [{ xAxis: currentIndex.value, label: { formatter: label, fontSize: 10, color: '#c23531', fontWeight: 'bold' } }]
  const update = { series: [{ markLine: { silent: true, symbol: 'none', lineStyle: { color: '#c23531', type: 'solid', width: 2 }, data: lineData } }] }
  if (metric.value === 'trips') {
    [chart, chart2].forEach(c => {
      if (!c) return
      c.setOption(update, false)
      c.dispatchAction({ type: 'downplay' })
      if (currentIndex.value < buckets.value.length) c.dispatchAction({ type: 'highlight', dataIndex: currentIndex.value })
    })
  } else {
    if (!chart) return
    chart.setOption(update, false)
    chart.dispatchAction({ type: 'downplay' })
    if (currentIndex.value < buckets.value.length) chart.dispatchAction({ type: 'highlight', dataIndex: currentIndex.value })
  }
}

watch(currentIndex, highlightCurrent)
watch(metric, () => { nextTick(renderChart) })
watch(granularity, () => load())
watch([() => props.filters, () => props.startMonth, () => props.endMonth], () => load(), { deep: true })
onMounted(load)
onUnmounted(() => { chart?.dispose(); chart2?.dispose() })
</script>

<style scoped>
.info-card { background: rgba(139,69,19,0.08); border-left: 4px solid #568aea; border-radius: 16px; padding: 14px 20px; margin-bottom: 24px; display: flex; gap: 12px; align-items: flex-start; }
.info-icon { font-size: 20px; }
.info-text { font-size: 12px; color: #8b7355; line-height: 1.5; }
.info-text strong { color: #8b4513; }

.metric-bar { display: flex; gap: 6px; margin-bottom: 16px; justify-content: center; }
.metric-bar button { padding: 6px 18px; border-radius: 20px; border: 1px solid rgba(139,69,19,0.2); background: transparent; color: #8b7355; font-size: 12px; cursor: pointer; transition: 0.2s; }
.metric-bar button:hover { border-color: #8b4513; color: #5c3d2e; }
.metric-bar button.active { background: #568aea; border-color: #568aea; color: #fff; }

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card { background: rgba(255,252,245,0.9); border-radius: 16px; padding: 14px; border: 1px solid rgba(86,138,234,0.2); text-align: center; }
.kpi-label { font-size: 15px; font-weight: 700; color: #5c3d2e; }
.kpi-number { font-size: 22px; font-weight: 800; color: #5c3d2e; }
.kpi-sub { font-size: 10px; color: #8b7355; margin-top: 4px; }
.kpi-delta { font-size: 13px; font-weight: 700; margin-top: 2px; }
.kpi-delta.delta-up { color: #c23531; }
.kpi-delta.delta-down { color: #4a7c59; }

.chart-row { display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.chart-row > * { flex: 1; min-width: 280px; }
.chart { width: 100%; }

.chart-explain { background: rgba(139,69,19,0.05); border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-size: 12px; color: #8b7355; line-height: 1.7; }
.chart-explain strong { color: #8b4513; }
.chart-explain em { font-style: normal; color: #c23531; background: rgba(194,53,49,0.08); padding: 1px 4px; border-radius: 3px; }

@media (max-width: 1000px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
</style>
