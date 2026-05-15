<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🔗</div>
      <div class="info-text"><strong>增强相关性：</strong>Pearson + Spearman 相关系数 + 显著性检验。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">计算中...</div>
    <template v-else>
      <div class="chart-row">
        <ChartCard title="Pearson 相关系数热力图" subtitle="数值字段两两相关" :large="true">
          <div ref="c1" class="chart" style="height:360px;"></div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="Top 相关性排名" subtitle="按|r|降序">
          <div ref="c2" class="chart"></div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchCorrelationAdvanced } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), corrData = ref({})
const c1 = ref(null), c2 = ref(null)
let charts = {}

const load = async () => {
  ready.value = false
  try { corrData.value = await fetchCorrelationAdvanced({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }) }
  catch (e) { console.error(e) }
  ready.value = true; await nextTick(); renderAll()
}

const renderAll = () => {
  const d = corrData.value
  if (c1.value && d.pearson) {
    if (!charts.c1) charts.c1 = echarts.init(c1.value, 'vintage-warm')
    const fields = d.columns || [], vals = []
    for (let i=0;i<fields.length;i++) for(let j=0;j<fields.length;j++) vals.push([j,i,d.pearson[fields[i]]?.[fields[j]]||0])
    charts.c1.setOption({
      xAxis:{type:'category',data:fields,axisLabel:{rotate:30,fontSize:9}}, yAxis:{type:'category',data:fields},
      visualMap:{min:-1,max:1,calculable:true,inRange:{color:['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#ffffbf','#fee090','#fdae61','#f46d43','#d73027','#a50026']}},
      series:[{type:'heatmap',data:vals,label:{show:true,formatter:p=>p.data[2].toFixed(2),fontSize:9}}],
    })
  }
  if (c2.value && d.top_pairs) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    charts.c2.setOption({
      grid:{containLabel:true,left:180}, xAxis:{type:'value',name:'Pearson r'},
      yAxis:{type:'category',data:d.top_pairs.map(p=>p.col1+' vs '+p.col2).reverse()},
      series:[{type:'bar',barWidth:'60%',data:d.top_pairs.map(p=>p.pearson).reverse(),
        itemStyle:{borderRadius:[0,6,6,0],color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#2f7b9e'},{offset:1,color:'#c23531'}])},
        label:{show:true,position:'right',formatter:p=>p.value.toFixed(3)}}],
    })
  }
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
.chart-row { display:flex; gap:20px; margin-bottom:24px; flex-wrap:wrap; }
.chart-row > * { flex:1; min-width:280px; }
.chart { width:100%; height:280px; }
</style>
