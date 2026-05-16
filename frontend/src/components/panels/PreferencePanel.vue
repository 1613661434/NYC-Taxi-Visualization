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
          <div class="chart-explain">
            <strong>📖 怎么看：</strong><em>横轴为行政区，纵轴为订单量</em>，不同颜色代表不同支付方式（现金/信用卡等）。对比各行政区柱子高度可知<em>哪里出租车需求最大</em>；颜色比例反映<em>各区域乘客支付习惯差异</em>——如曼哈顿信用卡占比通常较高。
          </div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="小费率×时段" subtitle="折线图" v-if="pref.tip_by_period">
          <div ref="c2" class="chart"></div>
          <div class="chart-explain">
            <strong>📖 怎么看：</strong><em>横轴为时段（深夜/早高峰/白天/晚高峰/夜间），纵轴为小费率（%）</em>。不同颜色的折线代表不同维度（如车型、行政区）。折线走高表示<em>该时段乘客更愿意给小费</em>，可发现"夜间小费率更高"等行为模式。
          </div>
        </ChartCard>
        <ChartCard title="距离×小时" subtitle="折线图" v-if="pref.distance_by_hour">
          <div ref="c3" class="chart"></div>
          <div class="chart-explain">
            <strong>📖 怎么看：</strong><em>横轴为小时（0~23点），纵轴为平均行程距离（英里）</em>。不同颜色的折线代表不同维度。可发现<em>哪些时段以长途出行为主</em>（如凌晨可能长距离机场线较多），哪些时段以短途为主（如白天市区通勤）。
          </div>
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
  Object.values(charts).forEach(c => c?.dispose())
  charts = {}
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
      xAxis: { type:'category', data: p.payment_by_borough.boroughs, name:'行政区', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'}, axisLabel: { rotate:15, fontSize:10 } },
      yAxis: { type:'value', name:'订单量', nameLocation:'center', nameGap:45, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
      series: p.payment_by_borough.categories.map((cat,i) => ({ name:cat, type:'bar', stack:'total', data: p.payment_by_borough.data.map(r=>r[i]) })),
      legend: { data: p.payment_by_borough.categories, textStyle:{color:'#5c3d2e'}, top:0 },
    })
  }
  if (c2.value && p.tip_by_period) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    charts.c2.setOption({
      tooltip: { trigger:'axis' },
      xAxis: { type:'category', data: p.tip_by_period.periods, name:'时段', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
      yAxis: { type:'value', name:'小费率（%）', nameLocation:'center', nameGap:45, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
      series: p.tip_by_period.categories.map((cat,i) => ({ name:cat, type:'line', smooth:true, data: p.tip_by_period.data.map(r=>r[i]), label:{show:true,position:'top',fontSize:10} })),
      legend: { data: p.tip_by_period.categories, textStyle:{color:'#5c3d2e'}, top:0 },
    })
  }
  if (c3.value && p.distance_by_hour) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    charts.c3.setOption({
      tooltip: { trigger:'axis' },
      xAxis: { type:'category', data: p.distance_by_hour.hours.map(h=>h+':00'), name:'小时', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
      yAxis: { type:'value', name:'平均距离（mi）', nameLocation:'center', nameGap:45, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'} },
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
.chart-explain { background:rgba(139,69,19,0.05); border-radius:10px; padding:10px 14px; margin-top:8px; font-size:12px; color:#8b7355; line-height:1.7; }
.chart-explain strong { color:#8b4513; }
.chart-explain em { font-style:normal; color:#c23531; background:rgba(194,53,49,0.08); padding:1px 4px; border-radius:3px; }
</style>
