<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🔮</div>
      <div class="info-text"><strong>预测建模：</strong>线性回归预测车费。特征：行程距离、乘客数、时段、月份。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">模型训练中...</div>
    <template v-else>
      <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-label">R-squared</div><div class="kpi-number">{{ metrics.r2 }}</div></div>
        <div class="kpi-card"><div class="kpi-label">MAE</div><div class="kpi-number">${{ metrics.mae }}</div></div>
        <div class="kpi-card"><div class="kpi-label">RMSE</div><div class="kpi-number">${{ metrics.rmse }}</div></div>
      </div>
      <div class="chart-row">
        <ChartCard title="预测值 vs 实际值" subtitle="对角线=完美预测" :large="true">
          <div ref="c1" class="chart" style="height:380px;"></div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="残差分布">
          <div ref="c2" class="chart"></div>
        </ChartCard>
        <ChartCard title="特征重要性（回归系数）">
          <div ref="c3" class="chart"></div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchPredictionTrain, fetchPredictionCompare } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), metrics = ref({})
const preds = ref([]), resids = ref([]), coefs = ref([])
const c1 = ref(null), c2 = ref(null), c3 = ref(null)
let charts = {}

const load = async () => {
  ready.value = false
  try {
    const [tr, cmp] = await Promise.all([
      fetchPredictionTrain({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }),
      fetchPredictionCompare({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }),
    ])
    metrics.value = tr.metrics; coefs.value = tr.coefficients || []
    preds.value = cmp.predictions || []; resids.value = cmp.residual_distribution || []
  } catch (e) { console.error(e) }
  ready.value = true
  await nextTick()
  renderAll()
}

const renderAll = () => {
  if (c1.value && preds.value.length) {
    if (!charts.c1) charts.c1 = echarts.init(c1.value, 'vintage-warm')
    const max = Math.max(...preds.value.map(p=>p.actual))
    charts.c1.setOption({
      tooltip: { trigger:'item', formatter: p=>`实际:$${p.data[0]}<br/>预测:$${p.data[1]}` },
      xAxis: { type:'value', name:'实际车费($)' },
      yAxis: { type:'value', name:'预测车费($)' },
      series: [
        { type:'scatter', symbolSize:4, data: preds.value.map(p=>[p.actual,p.predicted]), itemStyle:{color:'#2f7b9e'} },
        { type:'line', data:[[0,0],[max,max]], lineStyle:{color:'#b84c5c',type:'dashed'}, symbol:'none' },
      ],
    })
  }
  if (c2.value && resids.value.length) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    charts.c2.setOption({
      xAxis: { type:'category', data: resids.value.map(d=>d.bin_start.toFixed(0)), axisLabel:{rotate:20,fontSize:9} },
      yAxis: { type:'value', name:'频次' },
      series: [{ type:'bar', barWidth:'80%', data: resids.value.map(d=>d.count), itemStyle:{color:'#9b59b6',borderRadius:[4,4,0,0]} }],
    })
  }
  if (c3.value && coefs.value.length) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    charts.c3.setOption({
      grid: { containLabel:true, left:130 },
      xAxis: { type:'value', name:'系数' },
      yAxis: { type:'category', data: coefs.value.map(c=>c.feature).reverse() },
      series: [{ type:'bar', barWidth:'50%', data: coefs.value.map(c=>c.coefficient).reverse(), itemStyle:{borderRadius:[0,6,6,0],color:'#4a7c59'}, label:{show:true,position:'right',formatter:p=>p.value.toFixed(3)} }],
    })
  }
}

watch([()=>props.filters, ()=>props.startMonth, ()=>props.endMonth], ()=>load(), { deep:true })
onMounted(load)
onUnmounted(()=>Object.values(charts).forEach(c=>c?.dispose()))
</script>

<style scoped>
.info-card { background:rgba(139,69,19,0.08); border-left:4px solid #cd853f; border-radius:16px; padding:14px 20px; margin-bottom:24px; display:flex; gap:12px; align-items:flex-start; }
.info-icon { font-size:20px; }
.info-text { font-size:12px; color:#8b7355; line-height:1.5; }
.info-text strong { color:#8b4513; }
.kpi-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:24px; }
.kpi-card { background:rgba(255,252,245,0.9); border-radius:20px; padding:16px; border:1px solid rgba(86,138,234,0.25); text-align:center; }
.kpi-label { font-size:14px; color:#2f7b9e; font-weight:600; }
.kpi-number { font-size:28px; font-weight:800; color:#5c3d2e; margin-top:8px; }
.chart-row { display:flex; gap:20px; margin-bottom:24px; flex-wrap:wrap; }
.chart-row > * { flex:1; min-width:280px; }
.chart { width:100%; height:260px; }
</style>
