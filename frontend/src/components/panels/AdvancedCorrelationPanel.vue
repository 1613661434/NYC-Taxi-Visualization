<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🔗</div>
      <div class="info-text"><strong>增强相关性：</strong>Pearson + Spearman 相关系数 + 显著性检验 + 行政区关联。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">计算中...</div>
    <template v-else>
      <!-- 第一页：热力图 -->
      <div v-show="page === 0">
        <div class="chart-row">
          <ChartCard title="Pearson 相关系数热力图" subtitle="数值字段两两相关" :large="true">
            <div ref="c1" class="chart" style="height:360px;"></div>
            <div class="chart-explain">
              <strong>📖 怎么看：</strong><em>横轴和纵轴均为特征字段</em>，颜色代表 Pearson 相关系数（-1 到 1）。蓝色接近 1 = 强正相关（A 大则 B 大），红色靠近 -1 = 强负相关（A 大则 B 小），浅色接近 0 = 无线性关系。<em>关注对角线两侧的深色格子</em>，它们揭示了最重要的特征关联。
            </div>
          </ChartCard>
        </div>
      </div>

      <!-- 第二页：排名 -->
      <div v-show="page === 1">
        <div class="chart-row">
          <ChartCard title="Top 相关性排名" subtitle="Pearson r + Spearman ρ，按强度排序">
            <div class="sort-bar">
              <span class="sort-hint">按：</span>
              <button :class="{ active: sortType === 'pearson' }" @click="sortType = 'pearson'">Pearson</button>
              <button :class="{ active: sortType === 'spearman' }" @click="sortType = 'spearman'">Spearman</button>
              <span class="legend-dot" style="background:#c23531;"></span><span class="legend-txt">强 (≥0.7)</span>
              <span class="legend-dot" style="background:#e68a2e;"></span><span class="legend-txt">中 (0.4~0.7)</span>
              <span class="legend-dot" style="background:#aaa;"></span><span class="legend-txt">弱 (&lt;0.4)</span>
            </div>
            <div ref="c2" class="chart" style="height:320px;"></div>
            <div class="chart-explain">
              <strong>📖 怎么看：</strong>每条代表一对特征的相关性。<em>实心条 = Pearson（线性相关），空心菱形 = Spearman（单调相关）</em>。颜色越深越强。<em>Pearson ≈ Spearman 说明是稳定线性关系</em>；两者差距大则可能存在非线性模式或异常值干扰。
            </div>
          </ChartCard>
        </div>
      </div>

      <!-- 第三页：行政区关联 -->
      <div v-show="page === 2">
        <div class="chart-row">
          <ChartCard title="行政区多维指标雷达图" subtitle="各行政区在费用、距离、小费、乘客数上的差异" :large="true">
            <div ref="c3" class="chart" style="height:380px;"></div>
            <div class="chart-explain" v-if="boroughData">
              <strong>📖 怎么看：</strong>每个多边形代表一个行政区，轴为各指标均值。<em>面积越大整体消费越高</em>。Manhattan 通常在费用和距离上突出，而 Bronx/Queens 更为经济。形状相似的行政区说明出行模式趋同。
            </div>
          </ChartCard>
        </div>
        <div class="chart-row">
          <ChartCard title="行政区支付方式分布" subtitle="各行政区信用卡/现金/免收费占比">
            <div ref="c4" class="chart" style="height:320px;"></div>
            <div class="chart-explain" v-if="boroughData?.payment_distribution">
              <strong>📖 怎么看：</strong><em>横轴为行政区，纵轴为支付占比（%）</em>。颜色代表支付方式。对比各行政区的色块比例可知<em>不同区域的支付习惯差异</em>——通常曼哈顿信用卡占比最高，反映商务/游客出行特征。
            </div>
          </ChartCard>
        </div>
      </div>

      <!-- 分页器 -->
      <div class="pager">
        <button :disabled="page === 0" @click="page = 0">◀◀</button>
        <button :disabled="page === 0" @click="page--">◀</button>
        <span v-for="(pg, i) in pages" :key="i"
          :class="{ active: page === i, dot: true }"
          @click="page = i">{{ pg.label }}</span>
        <button :disabled="page === pages.length - 1" @click="page++">▶</button>
        <button :disabled="page === pages.length - 1" @click="page = pages.length - 1">▶▶</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchCorrelationAdvanced, fetchBoroughAnalysis } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), corrData = ref({}), boroughData = ref(null)
const sortType = ref('pearson'), page = ref(0)
const c1 = ref(null), c2 = ref(null), c3 = ref(null), c4 = ref(null)
let charts = {}

const pages = [
  { label: '热力图' },
  { label: '排名' },
  { label: '行政区' },
]

const load = async () => {
  ready.value = false
  Object.values(charts).forEach(c => c?.dispose())
  charts = {}
  try {
    const [corr, borough] = await Promise.all([
      fetchCorrelationAdvanced({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }),
      fetchBoroughAnalysis({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }),
    ])
    corrData.value = corr
    boroughData.value = borough
  } catch (e) { console.error(e) }
  ready.value = true; await nextTick(); renderAll()
}

const rename = (s) => s === '修正后总费用' ? '总费用' : s

const boroughColors = ['#c23531', '#2f7b9e', '#4a7c59', '#e6b422', '#9b59b6', '#e68a2e']

const renderPage1 = (d) => {
  if (!c1.value || !d.pearson) return
  if (!charts.c1) charts.c1 = echarts.init(c1.value, 'vintage-warm')
  const fields = (d.columns || []).map(rename), vals = []
  for (let i = 0; i < fields.length; i++) for (let j = 0; j < fields.length; j++) vals.push([j, i, d.pearson[d.columns[i]]?.[d.columns[j]] || 0])
  charts.c1.setOption({
    xAxis: { type: 'category', data: fields, axisLabel: { rotate: 30, fontSize: 9 }, name: '字段', nameLocation: 'center', nameGap: 15, nameTextStyle: { fontSize: 13, color: '#5c3d2e', fontWeight: 'bold' } },
    yAxis: { type: 'category', data: fields, name: '字段', nameLocation: 'center', nameGap: 45, nameTextStyle: { fontSize: 13, color: '#5c3d2e', fontWeight: 'bold' } },
    visualMap: { min: -1, max: 1, calculable: true, inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'] } },
    series: [{ type: 'heatmap', data: vals, label: { show: true, formatter: p => p.data[2].toFixed(2), fontSize: 9 } }],
  })
}

const renderPage2 = (d) => {
  if (!c2.value || !d.top_pairs) return
  if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
  const sortKey = sortType.value === 'spearman' ? 'spearman' : 'pearson'
  const pairs = [...d.top_pairs].sort((a, b) => (b[sortKey] || 0) - (a[sortKey] || 0))

  const strengthColor = (r) => {
    const v = Math.abs(r)
    if (v >= 0.7) return '#c23531'
    if (v >= 0.4) return '#e68a2e'
    return '#aaa'
  }

  const makeLabel = (a, b) => {
    const x = rename(a); const y = rename(b)
    return x.length + y.length > 9 ? x.slice(0, 4) + '→' + y.slice(0, 4) : x + ' → ' + y
  }

  charts.c2.setOption({
    tooltip: {
      trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const p = pairs[pairs.length - 1 - params[0].dataIndex]
        const strong = Math.abs(p.pearson) >= 0.7 ? '强相关' : Math.abs(p.pearson) >= 0.4 ? '中等相关' : '弱相关'
        return `<b>${rename(p.col1)} ↔ ${rename(p.col2)}</b><br/>Pearson r = ${p.pearson.toFixed(3)}<br/>Spearman ρ = ${(p.spearman || 0).toFixed(3)}<br/>强度：${strong}${p.pvalue ? '<br/>p = ' + p.pvalue : ''}`
      }
    },
    grid: { containLabel: true, left: 20, right: 80, top: 5, bottom: 5 },
    xAxis: { type: 'value', min: 0, max: 1, name: '相关系数', nameLocation: 'center', nameGap: 25, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' }, splitLine: { lineStyle: { color: 'rgba(139,69,19,0.1)', type: 'dashed' } }, axisLabel: { formatter: v => v.toFixed(1) } },
    yAxis: { type: 'category', data: pairs.map(p => makeLabel(p.col1, p.col2)).reverse(), axisLabel: { fontSize: 11, color: '#5c3d2e' }, axisLine: { show: false }, axisTick: { show: false } },
    series: [
      { name: 'Pearson r', type: 'bar', barWidth: '40%', barGap: '10%', data: pairs.map(p => ({ value: p.pearson, itemStyle: { borderRadius: [0, 4, 4, 0], color: strengthColor(p.pearson) } })).reverse(), label: { show: true, position: 'right', fontSize: 10, fontWeight: 'bold', formatter: p => p.value.toFixed(2) + ' P' } },
      { name: 'Spearman ρ', type: 'scatter', data: pairs.map(p => ({ value: p.spearman || 0, itemStyle: { color: '#2f7b9e', borderColor: '#fff', borderWidth: 1 } })).reverse(), symbol: 'diamond', symbolSize: 12, label: { show: true, position: 'right', fontSize: 9, offset: [30, 0], formatter: p => (p.value || 0).toFixed(2) + ' S' } },
    ],
    markLine: { silent: true, symbol: 'none', lineStyle: { type: 'dashed', color: '#ccc', width: 1 }, data: [{ xAxis: 0.7, label: { formatter: '强 0.7', fontSize: 9, color: '#c23531' } }, { xAxis: 0.4, label: { formatter: '中 0.4', fontSize: 9, color: '#e68a2e' } }] }
  })
}

const renderPage3 = (bd) => {
  if (!bd?.radar) return

  // 雷达图
  if (c3.value && bd.radar_metrics?.length) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    const metrics = bd.radar_metrics
    const maxVals = {}
    metrics.forEach(m => { maxVals[m] = bd.radar_max?.[m] || (Math.max(...(bd.radar[m] || [])) * 1.3) })
    charts.c3.setOption({
      tooltip: {},
      legend: { data: bd.boroughs, top: 5, textStyle: { color: '#5c3d2e', fontSize: 11 } },
      radar: {
        indicator: metrics.map(m => ({ name: m, max: maxVals[m] })),
        shape: 'polygon', center: ['50%', '55%'], radius: '65%',
        name: { textStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } }
      },
      series: [{
        type: 'radar',
        data: bd.boroughs.map((b, i) => ({
          name: b, value: metrics.map(m => bd.radar[m]?.[i] || 0),
          itemStyle: { color: boroughColors[i % boroughColors.length] },
          lineStyle: { color: boroughColors[i % boroughColors.length] },
        }))
      }],
    })
  }

  // 支付方式堆叠柱状图
  if (c4.value && bd.payment_distribution?.data?.length) {
    if (!charts.c4) charts.c4 = echarts.init(c4.value, 'vintage-warm')
    const pd = bd.payment_distribution
    charts.c4.setOption({
      tooltip: { trigger: 'axis', formatter: (params) => { let h = `<b>${params[0].axisValue}</b><br/>`; params.forEach(p => { h += `${p.marker} ${p.seriesName}：${(p.value * 100).toFixed(1)}%<br/>` }); return h } },
      legend: { data: pd.categories, top: 5, textStyle: { color: '#5c3d2e', fontSize: 10 } },
      grid: { top: 40, right: 20, bottom: 25, left: 50 },
      xAxis: { type: 'category', data: pd.boroughs, name: '行政区', nameLocation: 'center', nameGap: 25, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' } },
      yAxis: { type: 'value', max: 1, name: '占比', nameLocation: 'center', nameGap: 35, nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' }, axisLabel: { formatter: v => (v * 100).toFixed(0) + '%' } },
      series: pd.categories.map((cat, i) => ({
        name: cat, type: 'bar', stack: 'total', barWidth: '50%',
        data: pd.data.map(row => row[i] || 0),
        label: { show: true, fontSize: 9, formatter: p => p.value > 0.05 ? (p.value * 100).toFixed(0) + '%' : '' }
      })),
    })
  }
}

const renderAll = () => {
  const d = corrData.value
  if (!d) return
  if (page.value === 0) renderPage1(d)
  else if (page.value === 1) renderPage2(d)
  else renderPage3(boroughData.value)
}

watch(page, () => { nextTick(() => { Object.values(charts).forEach(c => c?.dispose()); charts = {}; renderAll() }) })
watch([() => props.filters, () => props.startMonth, () => props.endMonth], () => load(), { deep: true })
watch(sortType, () => { if (page.value === 1) renderPage2(corrData.value) })
onMounted(load)
onUnmounted(() => Object.values(charts).forEach(c => c?.dispose()))
</script>

<style scoped>
.info-card { background: rgba(139,69,19,0.08); border-left: 4px solid #cd853f; border-radius: 16px; padding: 14px 20px; margin-bottom: 24px; display: flex; gap: 12px; align-items: flex-start; }
.info-icon { font-size: 20px; }
.info-text { font-size: 12px; color: #8b7355; line-height: 1.5; }
.info-text strong { color: #8b4513; }
.chart-row { display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.chart-row > * { flex: 1; min-width: 280px; }
.chart { width: 100%; }
.chart-explain { background: rgba(139,69,19,0.05); border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-size: 12px; color: #8b7355; line-height: 1.7; }
.chart-explain strong { color: #8b4513; }
.chart-explain em { font-style: normal; color: #c23531; background: rgba(194,53,49,0.08); padding: 1px 4px; border-radius: 3px; }

.sort-bar { display: flex; gap: 6px; margin-bottom: 8px; justify-content: flex-end; align-items: center; flex-wrap: wrap; }
.sort-hint { font-size: 11px; color: #8b7355; }
.sort-bar button { padding: 3px 12px; border-radius: 12px; border: 1px solid rgba(139,69,19,0.2); background: transparent; color: #8b7355; font-size: 11px; cursor: pointer; transition: 0.2s; }
.sort-bar button:hover { border-color: #8b4513; color: #5c3d2e; }
.sort-bar button.active { background: #8b4513; color: #fdf6ec; border-color: #8b4513; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-left: 8px; }
.legend-txt { font-size: 10px; color: #8b7355; }

.pager { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 8px; padding: 12px 0; }
.pager button { background: rgba(139,69,19,0.08); border: 1px solid rgba(139,69,19,0.15); border-radius: 6px; color: #8b4513; padding: 4px 12px; cursor: pointer; font-size: 13px; transition: 0.2s; }
.pager button:hover:not(:disabled) { background: rgba(139,69,19,0.18); }
.pager button:disabled { opacity: 0.3; cursor: default; }
.pager .dot { padding: 4px 14px; border-radius: 14px; font-size: 12px; color: #8b7355; cursor: pointer; transition: 0.2s; border: 1px solid transparent; }
.pager .dot:hover { background: rgba(139,69,19,0.06); }
.pager .dot.active { background: #8b4513; color: #fdf6ec; font-weight: 600; }
</style>
