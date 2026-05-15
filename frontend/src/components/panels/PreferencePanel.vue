<template>
  <div>
    <div class="info-card">
      <div class="info-icon">📋</div>
      <div class="info-text"><strong>偏好分析：</strong>多维度出行偏好（支付方式、时段、距离、高峰/非高峰、乘客数量）。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">加载中...</div>
    <template v-else>
      <div class="chart-row">
        <ChartCard title="支付方式×行政区" subtitle="堆叠柱状图" :large="true" v-if="pref.payment_by_borough">
          <div ref="c1" class="chart" style="height:320px;"></div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="小费率×时段" subtitle="折线图" v-if="pref.tip_by_period">
          <div ref="c2" class="chart"></div>
        </ChartCard>
        <ChartCard title="距离×小时" subtitle="折线图" v-if="pref.distance_by_hour">
          <div ref="c3" class="chart"></div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchPreference } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), pref = ref({})
const c1 = ref(null), c2 = ref(null), c3 = ref(null)
let charts = {}

const load = async () => {
  ready.value = false
  try { pref.value = await fetchPreference({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }) }
  catch (e) { console.error(e) }
  ready.value = true; await nextTick(); renderAll()
}

const renderAll = () => {
  const p = pref.value
  if (c1.value && p.payment_by_borough) {
    if (!charts.c1) charts.c1 = echarts.init(c1.value, 'vintage-warm')
    charts.c1.setOption({
      tooltip: { trigger:'axis' },
      xAxis: { type:'category', data: p.payment_by_borough.boroughs, axisLabel: { rotate:15, fontSize:10 } },
      yAxis: { type:'value', name:'订单量' },
      series: p.payment_by_borough.categories.map((cat,i) => ({ name:cat, type:'bar', stack:'total', data: p.payment_by_borough.data.map(r=>r[i]) })),
      legend: { data: p.payment_by_borough.categories, textStyle:{color:'#5c3d2e'}, top:0 },
    })
  }
  if (c2.value && p.tip_by_period) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    charts.c2.setOption({
      tooltip: { trigger:'axis' },
      xAxis: { type:'category', data: p.tip_by_period.periods },
      yAxis: { type:'value', name:'小费率(%)' },
      series: p.tip_by_period.categories.map((cat,i) => ({ name:cat, type:'line', smooth:true, data: p.tip_by_period.data.map(r=>r[i]), label:{show:true,position:'top',fontSize:10} })),
      legend: { data: p.tip_by_period.categories, textStyle:{color:'#5c3d2e'}, top:0 },
    })
  }
  if (c3.value && p.distance_by_hour) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    charts.c3.setOption({
      tooltip: { trigger:'axis' },
      xAxis: { type:'category', data: p.distance_by_hour.hours.map(h=>h+':00') },
      yAxis: { type:'value', name:'距离(mi)' },
      series: p.distance_by_hour.categories.map((cat,i) => ({ name:cat, type:'line', smooth:true, data: p.distance_by_hour.data.map(r=>r[i]) })),
      legend: { data: p.distance_by_hour.categories, textStyle:{color:'#5c3d2e'}, top:0 },
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
.chart-row { display:flex; gap:20px; margin-bottom:24px; flex-wrap:wrap; }
.chart-row > * { flex:1; min-width:280px; }
.chart { width:100%; height:260px; }
</style>
