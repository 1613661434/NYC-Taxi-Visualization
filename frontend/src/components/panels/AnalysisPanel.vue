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
          <div class="chart-explain">
            <strong>📖 怎么看：</strong>横轴为聚类数 K（2~8），纵轴为惯性值（簇内误差平方和）。随着 K 增大惯性会持续下降，<em>寻找曲线的"拐点"（肘部）</em>——拐点之后惯性下降明显变缓，该点即为最佳 K 值。若曲线平滑无明显拐点，则参考轮廓系数图。
          </div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="聚类散点 (PCA 2D)" subtitle="每点=一次行程，颜色=聚类" :large="true">
          <div ref="c2" class="chart" style="height:400px;"></div>
          <div class="chart-explain">
            <strong>📖 怎么看：</strong>用 PCA 将多维特征压缩到二维平面，<em>横轴为主成分1（PC1），纵轴为主成分2（PC2）</em>。每个点代表一次行程，同色点属于同一聚类。若各聚类在图上<em>分离清晰、重叠少</em>，说明聚类效果良好；若大量混杂，说明特征对行程模式的区分力有限。
          </div>
        </ChartCard>
      </div>
      <div class="chart-row">
        <ChartCard title="聚类画像雷达图" subtitle="各聚类特征均值" :large="true">
          <div ref="c3" class="chart" style="height:400px;"></div>
          <div class="chart-explain">
            <strong>📖 怎么看：</strong>雷达图的每个轴代表一个特征（如行程距离、车费等），<em>多边形越大表示该聚类在该特征上的均值越高</em>。
            <div v-if="clusterProfiles.length" class="cluster-labels">
              <div v-for="p in clusterProfiles" :key="p.cluster" class="cluster-tag">
                <span class="cluster-dot" :style="{background: clusterColor(p.cluster)}"></span>
                <strong>{{ p.label || '聚类'+(p.cluster+1) }}</strong>
                <span class="cluster-stats">（{{ (p.count/1000).toFixed(1) }}k 单，{{ (p.count/clusterTotal*100).toFixed(0) }}%）</span>
              </div>
            </div>
          </div>
        </ChartCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChartCard from '../common/ChartCard.vue'
import { fetchClustering } from '../../api/index.js'
import * as echarts from 'echarts'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const ready = ref(false), data = ref(null)
const c1 = ref(null), c2 = ref(null), c3 = ref(null)
let charts = {}

const clusterProfiles = computed(() => data.value?.cluster_profiles || [])
const clusterTotal = computed(() => clusterProfiles.value.reduce((s, p) => s + p.count, 0) || 1)
const colors = ['#2f7b9e', '#c23531', '#4a7c59', '#b84c5c', '#9b59b6', '#e68a2e']
const clusterColor = (c) => colors[c % colors.length]

const load = async () => {
  ready.value = false
  Object.values(charts).forEach(c => c?.dispose())
  charts = {}
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
      tooltip:{trigger:'axis', formatter: p => `<b>K=${p[0].axisValueLabel}</b><br/>惯性值：${p[0].data.toLocaleString()}`},
      xAxis:{type:'category', data:(d.elbow||[]).map(e=>'K='+e.k), name:'K值（聚类数量）', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'}},
      yAxis:{type:'value', name:'惯性值（Inertia）', nameLocation:'center', nameGap:45, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'}},
      series:[{data:(d.elbow||[]).map(e=>e.inertia),type:'line',smooth:true,symbol:'circle',symbolSize:10,lineStyle:{color:'#2f7b9e'}}],
    })
  }
  if (c2.value && d.scatter_data) {
    if (!charts.c2) charts.c2 = echarts.init(c2.value, 'vintage-warm')
    const clusters = [...new Set(d.scatter_data.map(p=>p.cluster))]
    const getLabel = (c) => (d.cluster_profiles?.[c]?.label) || '聚类' + (c + 1)
    charts.c2.setOption({
      tooltip:{trigger:'item', formatter:p=>'<b>'+getLabel(p.data[2])+'</b><br/>PC1：'+p.data[0].toFixed(2)+'<br/>PC2：'+p.data[1].toFixed(2)},
      xAxis:{type:'value', name:'主成分1（PC1）', nameLocation:'center', nameGap:30, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'}},
      yAxis:{type:'value', name:'主成分2（PC2）', nameLocation:'center', nameGap:45, nameTextStyle:{fontSize:13, color:'#5c3d2e', fontWeight:'bold'}},
      series: clusters.map(c=>({name:getLabel(c),type:'scatter',data:d.scatter_data.filter(p=>p.cluster===c).map(p=>[p.x,p.y,p.cluster]),symbolSize:5,itemStyle:{color:colors[c%colors.length]}})),
      legend:{data:clusters.map(c=>getLabel(c)),textStyle:{color:'#5c3d2e',fontSize:10},top:5},
    })
  }
  if (c3.value && d.cluster_profiles) {
    if (!charts.c3) charts.c3 = echarts.init(c3.value, 'vintage-warm')
    const feats = d.features_used||[], maxs={}
    feats.forEach(f=>{maxs[f]=Math.max(...d.cluster_profiles.map(p=>p[f]||0))*1.3||10})
    charts.c3.setOption({
      tooltip:{},
      radar:{indicator:feats.map(f=>({name:addUnit(f),max:maxs[f]})),shape:'polygon',center:['50%','55%'],radius:'65%', name:{textStyle:{fontSize:12, color:'#5c3d2e', fontWeight:'bold'}}},
      series:[{type:'radar',data:d.cluster_profiles.map((p,i)=>({name:p.label||'聚类'+(i+1),value:feats.map(f=>p[f]||0)}))}],
      legend:{data:d.cluster_profiles.map(p=>p.label||'聚类'+(p.cluster+1)),textStyle:{color:'#5c3d2e',fontSize:10},top:5},
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
.chart-explain { background:rgba(139,69,19,0.05); border-radius:10px; padding:10px 14px; margin-top:8px; font-size:12px; color:#8b7355; line-height:1.7; }
.chart-explain strong { color:#8b4513; }
.chart-explain em { font-style:normal; color:#c23531; background:rgba(194,53,49,0.08); padding:1px 4px; border-radius:3px; }
.cluster-labels { display:flex; gap:16px; flex-wrap:wrap; margin-top:8px; }
.cluster-tag { display:flex; align-items:center; gap:6px; font-size:12px; color:#5c3d2e; background:rgba(139,69,19,0.05); border-radius:8px; padding:6px 12px; }
.cluster-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.cluster-stats { color:#8b7355; font-size:11px; }
</style>
