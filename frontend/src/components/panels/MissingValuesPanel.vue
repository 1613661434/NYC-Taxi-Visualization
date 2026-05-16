<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🔍</div>
      <div class="info-text">
        <strong>缺失值检测与分析：</strong>对 {{ totalRows?.toLocaleString() || 0 }} 行清洗后数据逐字段扫描。
        原始 NYC TLC 数据存在约 2~5% 的字段缺失（主要集中在<em>通行费、附加费</em>等可选字段），经清洗后已大幅改善。
        缺失率 > 5% 的字段需特别关注，可能影响分析准确性。
      </div>
    </div>

    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">扫描缺失值中...</div>

    <template v-else>
      <div class="chart-row">
        <ChartCard title="各字段缺失值比例" subtitle="横向柱状图 — 颜色越红缺失越严重">
          <div ref="chart1" class="chart"></div>
          <div class="chart-explain">
            <strong>📖 分析：</strong>共检测 <em>{{ columns.length }}</em> 个存在缺失的字段。
            <span v-if="maxMissingPct < 1">所有字段缺失率均 < 1%，数据质量<em>优秀</em>，可直接用于分析建模。</span>
            <span v-else-if="maxMissingPct < 5">最高缺失率 {{ maxMissingPct }}%，整体数据质量<em>良好</em>，缺失主要集中在非核心字段。</span>
            <span v-else>最高缺失率达 {{ maxMissingPct }}%，建议在使用前对高缺失字段进行填充或排除。</span>
            <span v-if="totalRows">基于 {{ totalRows.toLocaleString() }} 行采样数据统计。</span>
          </div>
        </ChartCard>
      </div>

      <div class="chart-row" v-if="columns.length > 0">
        <ChartCard title="按车型缺失值对比" subtitle="黄色出租车 vs 绿色出租车 各字段缺失数量">
          <div ref="chart2" class="chart"></div>
          <div class="chart-explain">
            <strong>📖 分析：</strong>对比黄色与绿色出租车的缺失情况。
            <span v-if="yellowDominant">黄色出租车在 <em>{{ yellowDominant }}</em> 等字段上缺失较多，可能与数据采集系统差异有关——黄色出租车数据量远超绿色，绝对缺失数自然更大。</span>
            <span v-else>两种车型缺失模式相近，说明缺失主要由原始数据源而非车型差异导致。</span>
            缺失值处理建议：<em>数值字段用中位数填充，类别字段用众数填充</em>，或直接排除缺失率极低的记录。
          </div>
        </ChartCard>
      </div>

      <div class="quality-summary">
        <div class="quality-title">📋 数据质量评估</div>
        <div class="quality-grid">
          <div class="quality-item">
            <span class="qlabel">总采样行数</span>
            <span class="qvalue">{{ totalRows?.toLocaleString() || '-' }}</span>
          </div>
          <div class="quality-item">
            <span class="qlabel">缺失字段数</span>
            <span class="qvalue">{{ columns.length }}</span>
          </div>
          <div class="quality-item">
            <span class="qlabel">最高缺失率</span>
            <span class="qvalue" :class="{ 'text-red': maxMissingPct > 5 }">{{ maxMissingPct }}%</span>
          </div>
          <div class="quality-item">
            <span class="qlabel">综合评级</span>
            <span class="qvalue">{{ qualityGrade }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
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

const totalRows = computed(() => missingData.value?.total_rows)
const maxMissingPct = computed(() => {
  if (!missingData.value?.missing_pcts) return 0
  const pcts = Object.values(missingData.value.missing_pcts)
  return pcts.length ? Math.max(...pcts).toFixed(2) : 0
})
const qualityGrade = computed(() => {
  if (maxMissingPct.value < 1) return '⭐ 优秀'
  if (maxMissingPct.value < 5) return '✅ 良好'
  return '⚠️ 需关注'
})
const yellowDominant = computed(() => {
  if (!missingData.value?.by_taxi_type) return ''
  const bt = missingData.value.by_taxi_type
  const diffFields = []
  for (const col of columns.value) {
    const y = bt[col]?.['黄色出租车'] || 0
    const g = bt[col]?.['绿色出租车'] || 0
    if (y > g * 3 && y > 10) diffFields.push(col)
  }
  return diffFields.slice(0, 2).join('、')
})

const load = async () => {
  try {
    missingData.value = await fetchMissingValues({
      start_month: props.startMonth, end_month: props.endMonth,
      company: props.filters.company, borough: props.filters.borough,
    })
    columns.value = missingData.value.columns || []
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
    xAxis: { type: 'value', name: '缺失率 (%)', max: 100, nameLocation: 'center', nameGap: 25, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
    yAxis: { type: 'category', data: items.map(d => d.name), axisLabel: { fontSize: 11 }, name: '字段', nameLocation: 'center', nameGap: 130, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
    series: [{
      data: items.map(d => ({ value: d.pct,
        itemStyle: { color: `hsl(${(1 - d.pct / 100) * 120}, 70%, 50%)` } })),
      type: 'bar', barWidth: '60%',
      itemStyle: { borderRadius: [0, 6, 6, 0] },
      label: { show: true, position: 'right', formatter: (p) => p.value.toFixed(2) + '%' },
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
    grid: { top: 40, right: 20, bottom: 60, left: 50 },
    xAxis: { type: 'category', data: cols, axisLabel: { rotate: 25, fontSize: 9 }, name: '字段', nameLocation: 'center', nameGap: 25, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
    yAxis: { type: 'value', name: '缺失数量', nameLocation: 'center', nameGap: 40, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
    series: types.map((t, i) => ({
      name: t, type: 'bar',
      data: cols.map(c => (bt[c] || {})[t] || 0),
      itemStyle: { color: ['#e6b422', '#4a7c59'][i], borderRadius: [4, 4, 0, 0] },
    })),
    legend: { data: types, textStyle: { color: '#5c3d2e', fontSize: 11 }, top: 0 },
  })
}

watch([() => props.filters, () => props.startMonth, () => props.endMonth], () => load(), { deep: true })
onMounted(load)
onUnmounted(() => { c1?.dispose(); c2?.dispose() })
</script>

<style scoped>
.info-card { background: rgba(139,69,19,0.08); border-left: 4px solid #568aea; border-radius: 16px; padding: 14px 20px; margin-bottom: 24px; display: flex; gap: 12px; align-items: flex-start; }
.info-icon { font-size: 20px; }
.info-text { font-size: 12px; color: #8b7355; line-height: 1.6; }
.info-text strong { color: #8b4513; }
.info-text em { font-style: normal; color: #c23531; background: rgba(194,53,49,0.08); padding: 1px 4px; border-radius: 3px; }
.chart-row { display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.chart-row > * { flex: 1; min-width: 280px; }
.chart { width: 100%; height: 300px; }

.chart-explain { background: rgba(139,69,19,0.05); border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-size: 12px; color: #8b7355; line-height: 1.7; }
.chart-explain strong { color: #8b4513; }
.chart-explain em { font-style: normal; color: #c23531; background: rgba(194,53,49,0.08); padding: 1px 4px; border-radius: 3px; }

.quality-summary { background: rgba(255,252,245,0.85); border: 1px solid rgba(139,69,19,0.1); border-radius: 16px; padding: 20px; margin-top: 8px; }
.quality-title { font-size: 15px; font-weight: 700; color: #5c3d2e; margin-bottom: 14px; }
.quality-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.quality-item { text-align: center; }
.qlabel { display: block; font-size: 11px; color: #8b7355; margin-bottom: 4px; }
.qvalue { display: block; font-size: 20px; font-weight: 800; color: #5c3d2e; }
.qvalue.text-red { color: #c23531; }

@media (max-width: 800px) { .quality-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
