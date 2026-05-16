<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🔮</div>
      <div class="info-text">
        <strong>月度时序预测：</strong>用前11个月数据做多项式拟合，预测第12个月，与实际值对比验证。
        <br/>此模块使用全年数据，<em>不受左侧月份筛选影响</em>。
      </div>
    </div>

    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">月度预测计算中...</div>

    <template v-else>
      <!-- 第一页：订单量预测（总体 + 黄车 + 绿车） -->
      <div v-show="page === 0">
        <div class="chart-row">
          <ChartCard title="总体 — 月度订单量拟合预测" subtitle="黄车+绿车合计：1~11月拟合（虚线）→ 12月预测（星标）vs 实际（实线）" :large="true">
            <div ref="c5" class="chart" style="height:360px;"></div>
            <div class="chart-explain" v-if="predData.total">
              <strong>📖 分析：</strong>{{ predData.total.trips.analysis }}
            </div>
          </ChartCard>
        </div>
        <div class="chart-row">
          <ChartCard title="黄色出租车 — 月度订单量拟合预测" subtitle="1~11月拟合 → 12月预测 vs 实际">
            <div v-if="predData.yellow" ref="c1" class="chart" style="height:320px;"></div>
            <div v-else class="chart-empty">当前筛选无黄色出租车数据</div>
            <div class="chart-explain" v-if="predData.yellow">
              <strong>📖 分析：</strong>{{ predData.yellow.trips.analysis }}
            </div>
          </ChartCard>
          <ChartCard title="绿色出租车 — 月度订单量拟合预测" subtitle="1~11月拟合 → 12月预测 vs 实际">
            <div v-if="predData.green" ref="c2" class="chart" style="height:320px;"></div>
            <div v-else class="chart-empty">当前筛选无绿色出租车数据</div>
            <div class="chart-explain" v-if="predData.green">
              <strong>📖 分析：</strong>{{ predData.green.trips.analysis }}
            </div>
          </ChartCard>
        </div>
      </div>

      <!-- 第二页：距离 vs 费用 回归分析 -->
      <div v-show="page === 1">
        <div class="chart-row">
          <ChartCard title="黄色出租车 — 距离 vs 总费用" subtitle="散点 + 线性回归线">
            <div ref="c3" class="chart" style="height:340px;"></div>
            <div class="chart-explain" v-if="predData.yellow?.distance_fare_regression">
              <strong>📖 分析：</strong>{{ predData.yellow.distance_fare_regression.analysis }}
            </div>
          </ChartCard>
          <ChartCard title="绿色出租车 — 距离 vs 总费用" subtitle="散点 + 线性回归线">
            <div ref="c4" class="chart" style="height:340px;"></div>
            <div class="chart-explain" v-if="predData.green?.distance_fare_regression">
              <strong>📖 分析：</strong>{{ predData.green.distance_fare_regression.analysis }}
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
import { fetchMonthlyPrediction } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object })
const ready = ref(false), predData = ref({}), page = ref(0)
const c1 = ref(null), c2 = ref(null), c3 = ref(null), c4 = ref(null), c5 = ref(null)
let charts = {}

const pages = [
  { label: '月度订单量预测' },
  { label: '距离 vs 费用关系' },
]

const load = async () => {
  ready.value = false
  Object.values(charts).forEach(c => c?.dispose())
  charts = {}
  try {
    predData.value = await fetchMonthlyPrediction({ company: props.filters.company, borough: props.filters.borough })
  } catch (e) { console.error(e) }
  ready.value = true
  await nextTick()
  renderAll()
}

const renderAll = () => {
  const d = predData.value
  if (!d) return

  if (page.value === 0) {
    renderPage1(d)
  } else {
    renderPage2(d)
  }
}

const renderOneFitChart = (refEl, key, data, colorActual, colorFit, title) => {
  if (!refEl.value || !data) return
  if (!charts[key]) charts[key] = echarts.init(refEl.value, 'vintage-warm')

  const months = data.months
  const actual = data.actual
  const fitted = data.fitted
  const predicted = data.predicted

  charts[key].setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `<b>${params[0].axisValue}月</b><br/>`
        params.forEach(p => {
          const v = Array.isArray(p.value) ? p.value[1] : p.value
          if (v != null && !isNaN(v)) {
            html += `${p.marker} ${p.seriesName}：${Number(v).toLocaleString()} 单<br/>`
          }
        })
        return html
      }
    },
    legend: { top: 5, textStyle: { color: '#5c3d2e', fontSize: 10 } },
    grid: { top: 45, right: 30, bottom: 30, left: 55 },
    xAxis: {
      type: 'category', data: months.map(m => m + '月'),
      name: '月份', nameLocation: 'center', nameGap: 25,
      nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' }
    },
    yAxis: {
      type: 'value', name: '订单量（单）', nameLocation: 'center', nameGap: 45,
      nameTextStyle: { fontSize: 12, color: '#5c3d2e', fontWeight: 'bold' }
    },
    series: [
      {
        name: '实际值', type: 'line', data: actual, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: colorActual, width: 2.5 },
        itemStyle: { color: colorActual },
      },
      {
        name: '拟合曲线', type: 'line',
        data: fitted,
        smooth: true, symbol: 'diamond', symbolSize: 3,
        lineStyle: { color: colorFit, type: 'dashed', width: 2 },
        itemStyle: { color: colorFit },
      },
      {
        name: '12月预测', type: 'scatter',
        data: [[months.length - 1, predicted]],
        symbol: 'star', symbolSize: 22,
        itemStyle: { color: colorFit, borderColor: '#fff', borderWidth: 1 },
        label: { show: true, formatter: isNaN(predicted) ? '' : `预测 ${predicted.toLocaleString()}`, position: 'top', fontSize: 11, fontWeight: 'bold', color: colorFit },
      },
    ],
  })
}

const renderPage1 = (d) => {
  renderOneFitChart(c5, 'c5', d.total?.trips, '#568aea', '#3a5a9e')
  renderOneFitChart(c1, 'c1', d.yellow?.trips, '#e6b422', '#c8960c')
  renderOneFitChart(c2, 'c2', d.green?.trips, '#4a7c59', '#2d5a3a')
}

const renderPage2 = (d) => {
  const makeRegChart = (refEl, key, regData, color) => {
    if (!refEl.value || !regData) return
    if (!charts[key]) charts[key] = echarts.init(refEl.value, 'vintage-warm')

    const scatter = regData.scatter.map(p => [p.distance, p.fare])
    const line = regData.regression_line.map(p => [p.distance, p.fare])

    charts[key].setOption({
      tooltip: {
        trigger: 'item',
        formatter: p => `距离：${p.data[0].toFixed(1)} mi<br/>费用：$${p.data[1].toFixed(2)}`
      },
      grid: { top: 15, right: 30, bottom: 35, left: 65 },
      xAxis: {
        type: 'value', name: '行程距离（mi）', nameLocation: 'center', nameGap: 30,
        nameTextStyle: { fontSize: 13, color: '#5c3d2e', fontWeight: 'bold' }
      },
      yAxis: {
        type: 'value', name: '总费用（$）', nameLocation: 'center', nameGap: 50,
        nameTextStyle: { fontSize: 13, color: '#5c3d2e', fontWeight: 'bold' }
      },
      series: [
        {
          name: '行程散点', type: 'scatter', data: scatter,
          symbolSize: 4, itemStyle: { color: color, opacity: 0.4 },
        },
        {
          name: '回归线', type: 'line', data: line, smooth: false,
          symbol: 'none', lineStyle: { color: '#c23531', width: 2.5 },
        },
      ],
      // 显示 R²
      graphic: [{
        type: 'text', left: 'center', top: 8,
        style: {
          text: `R² = ${regData.r2}  |  斜率 = ${regData.slope}  |  截距 = $${regData.intercept}`,
          fontSize: 12, fontWeight: 'bold', fill: '#5c3d2e',
        },
      }],
    })
  }

  makeRegChart(c3, 'c3', d.yellow?.distance_fare_regression, '#e6b422')
  makeRegChart(c4, 'c4', d.green?.distance_fare_regression, '#4a7c59')
}

watch(page, () => {
  nextTick(() => { Object.values(charts).forEach(c => c?.dispose()); charts = {}; renderAll() })
})

watch([() => props.filters], () => load(), { deep: true })
onMounted(load)
onUnmounted(() => Object.values(charts).forEach(c => c?.dispose()))
</script>

<style scoped>
.info-card { background: rgba(139,69,19,0.08); border-left: 4px solid #cd853f; border-radius: 16px; padding: 14px 20px; margin-bottom: 24px; display: flex; gap: 12px; align-items: flex-start; }
.info-icon { font-size: 20px; }
.info-text { font-size: 12px; color: #8b7355; line-height: 1.6; }
.info-text strong { color: #8b4513; }
.info-text em { font-style: normal; color: #c23531; background: rgba(194,53,49,0.08); padding: 1px 4px; border-radius: 3px; }

.chart-row { display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.chart-row > * { flex: 1; min-width: 280px; }
.chart { width: 100%; }
.chart-empty { width: 100%; height: 320px; display: flex; align-items: center; justify-content: center; color: #8b7355; font-size: 13px; background: rgba(139,69,19,0.03); border-radius: 8px; }

.analysis-grid { display: flex; gap: 16px; margin-top: 8px; flex-wrap: wrap; }
.analysis-item { flex: 1; min-width: 250px; background: rgba(139,69,19,0.05); border-radius: 10px; padding: 10px 14px; font-size: 12px; color: #8b7355; line-height: 1.7; }
.analysis-item strong { color: #8b4513; }

.chart-explain { background: rgba(139,69,19,0.05); border-radius: 10px; padding: 10px 14px; margin-top: 8px; font-size: 12px; color: #8b7355; line-height: 1.7; }
.chart-explain strong { color: #8b4513; }

.pager {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; margin-top: 8px; padding: 12px 0;
}
.pager button {
  background: rgba(139,69,19,0.08);
  border: 1px solid rgba(139,69,19,0.15);
  border-radius: 6px; color: #8b4513;
  padding: 4px 12px; cursor: pointer; font-size: 13px;
  transition: 0.2s;
}
.pager button:hover:not(:disabled) { background: rgba(139,69,19,0.18); }
.pager button:disabled { opacity: 0.3; cursor: default; }

.pager .dot {
  padding: 4px 14px; border-radius: 14px;
  font-size: 12px; color: #8b7355; cursor: pointer;
  transition: 0.2s; border: 1px solid transparent;
}
.pager .dot:hover { background: rgba(139,69,19,0.06); }
.pager .dot.active {
  background: #8b4513; color: #fdf6ec; font-weight: 600;
}
</style>
