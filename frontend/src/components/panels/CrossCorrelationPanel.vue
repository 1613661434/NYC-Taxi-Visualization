<template>
  <div>
    <div class="info-card">
      <div class="info-icon">💡</div>
      <div class="info-text"><strong>跨维度发现：</strong>自动探索数据中有趣的关联模式。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">分析中...</div>
    <div v-else class="discovery-grid">
      <div v-for="(d,i) in discoveries" :key="i" class="discovery-card">
        <div class="disc-title">{{ d.title }}</div>
        <div class="disc-desc">{{ d.description }}</div>
        <div :ref="el => { if(el) refs[i]=el }" class="disc-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { fetchCrossCorrelation } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), discoveries = ref([])
const refs = ref([])
let charts = {}

const load = async () => {
  ready.value = false
  try {
    const res = await fetchCrossCorrelation({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough })
    discoveries.value = res.discoveries || []
  } catch (e) { console.error(e) }
  ready.value = true; await nextTick(); renderAll()
}

const renderAll = () => {
  discoveries.value.forEach((d,i) => {
    const el = refs.value[i]; if (!el) return
    if (charts[i]) charts[i].dispose()
    charts[i] = echarts.init(el, 'vintage-warm')
    if (d.chart_type==='bar') {
      const cats=d.data.categories,series=d.data.series,names=Object.keys(series)
      charts[i].setOption({
        tooltip:{trigger:'axis'}, xAxis:{type:'category',data:cats,axisLabel:{rotate:15,fontSize:8}}, yAxis:{type:'value'},
        series:names.map(n=>({name:n,type:'bar',data:series[n],barWidth:names.length>1?'40%':'60%'})),
        legend:names.length>1?{data:names,textStyle:{color:'#8b7355',fontSize:10},top:0}:undefined,
      })
    } else if (d.chart_type==='line') {
      const cats=d.data.categories,series=d.data.series,names=Object.keys(series)
      charts[i].setOption({
        tooltip:{trigger:'axis'}, xAxis:{type:'category',data:cats,axisLabel:{rotate:15,fontSize:8}}, yAxis:{type:'value'},
        series:names.map(n=>({name:n,type:'line',smooth:true,data:series[n],symbolSize:4})),
        legend:{data:names,textStyle:{color:'#8b7355',fontSize:10},top:0},
      })
    }
  })
}

watch([()=>props.filters,()=>props.startMonth,()=>props.endMonth],()=>load(),{deep:true})
onMounted(load)
onUnmounted(()=>Object.values(charts).forEach(c=>c?.dispose()))
</script>

<style scoped>
.info-card { background:rgba(139,69,19,0.08); border-left:4px solid #cd853f; border-radius:16px; padding:14px 20px; margin-bottom:24px; display:flex; gap:12px; align-items:flex-start; }
.info-icon { font-size:20px; }
.info-text { font-size:12px; color:#8b7355; line-height:1.5; }
.info-text strong { color:#8b4513; }
.discovery-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:20px; }
.discovery-card { background:rgba(255,252,245,0.85); border-radius:20px; padding:20px; border:1px solid rgba(86,138,234,0.15); }
.disc-title { font-size:15px; font-weight:600; color:#5c3d2e; margin-bottom:4px; }
.disc-desc { font-size:11px; color:#8b7355; margin-bottom:10px; }
.disc-chart { width:100%; height:220px; }
@media (max-width:1000px) { .discovery-grid { grid-template-columns:1fr; } }
</style>
