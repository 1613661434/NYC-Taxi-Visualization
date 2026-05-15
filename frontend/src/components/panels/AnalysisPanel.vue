<template>
  <div>
    <div class="info-card">
      <div class="info-icon">📊</div>
      <div class="info-text"><strong>聚类分析：</strong>K-means + PCA降维。特征：行程距离、车费、小费、乘客数量、总费用、时段。</div>
    </div>
    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">聚类计算中（约20秒）...</div>
    <template v-else>
      <div class="chart-row">
        <ChartCard title="肘部法则 - K值选择" subtitle="惯性随K值变化">
          <div ref="c1" class="chart"></div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="聚类散点 (PCA 2D)" subtitle="每点=一次行程，颜色=聚类" :large="true">
          <div ref="c2" class="chart" style="height:400px;"></div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="聚类画像雷达图" subtitle="各聚类特征均值" :large="true">
          <div ref="c3" class="chart" style="height:400px;"></div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchClustering } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), data = ref(null)
const c1 = ref(null), c2 = ref(null), c3 = ref(null)
let charts = {}

const load = async () => {
  ready.value = false
  try { data.value = await fetchClustering({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }) }
  catch (e) { console.error(e) }
  ready.value = true; await nextTick(); renderAll()
}

const addUnit = (f) => {
  const m = { '行程距离':'行程距离(mi)', '车费':'车费($)', '小费':'小费($)', '乘客数量':'乘客数量(人)', '修正后总费用':'总费用($)', '小时':'时段(时)' }
  return m[f] || f
}

const renderAll = () => {
  const d = data.value; if (!d) return
  if (c1.value) {
    if (!charts.c1) charts.c1 = echarts.init(c1.value, 'vintage-warm')
    charts.c1.setOption({
      tooltip:{trigger:'axis'}, xAxis:{type:'category',data:(d.elbow||[]).map(e=>'K='+e.k)}, yAxis:{type:'value',name:'Inertia'},
      series:[{data:(d.elbow||[]).map(e=>e.inertia),type:'line',smooth:true,symbol:'circle',symbolSize:10,lineStyle:{color:'#2f7b9e'}}],
    })
  }
  if (c2.value && d.scatter_data) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    const clusters = [...new Set(d.scatter_data.map(p=>p.cluster))]
    const colors = ['#2f7b9e','#c23531','#4a7c59','#b84c5c','#9b59b6','#c23531']
    charts.c2.setOption({
      tooltip:{trigger:'item',formatter:p=>'聚类'+(p.data[2]+1)}, xAxis:{type:'value',name:'主成分1 (PC1)'}, yAxis:{type:'value',name:'主成分2 (PC2)'},
      series: clusters.map(c=>({name:'聚类'+(c+1),type:'scatter',data:d.scatter_data.filter(p=>p.cluster===c).map(p=>[p.x,p.y,p.cluster]),symbolSize:5,itemStyle:{color:colors[c%colors.length]}})),
      legend:{data:clusters.map(c=>'聚类'+(c+1)),textStyle:{color:'#5c3d2e'},top:5},
    })
  }
  if (c3.value && d.cluster_profiles) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    const feats = d.features_used||[], maxs={}
    feats.forEach(f=>{maxs[f]=Math.max(...d.cluster_profiles.map(p=>p[f]||0))*1.3||10})
    charts.c3.setOption({
      radar:{indicator:feats.map(f=>({name:addUnit(f),max:maxs[f]})),shape:'polygon',center:['50%','55%'],radius:'65%'},
      series:[{type:'radar',data:d.cluster_profiles.map((p,i)=>({name:'聚类'+(i+1),value:feats.map(f=>p[f]||0)}))}],
      legend:{data:d.cluster_profiles.map((_,i)=>'聚类'+(i+1)),textStyle:{color:'#5c3d2e'},top:5},
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
