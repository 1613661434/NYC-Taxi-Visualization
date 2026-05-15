<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🗺️</div>
      <div class="info-text"><strong>NYC 出租车区域订单特点地图：</strong>基于263个Taxi Zone地理边界。颜色深浅=指标高低。</div>
    </div>

    <div class="controls">
      <span class="ctrl-label">视图：</span>
      <button :class="{ active: view === 'pickup' }" @click="view = 'pickup'">上车区域</button>
      <button :class="{ active: view === 'dropoff' }" @click="view = 'dropoff'">下车区域</button>
      <span class="sep">|</span>
      <span class="ctrl-label">指标：</span>
      <button :class="{ active: metric === '订单量' }" @click="metric = '订单量'">订单量</button>
      <button :class="{ active: metric === '平均费用' }" @click="metric = '平均费用'">平均费用($)</button>
      <button :class="{ active: metric === '平均距离' }" @click="metric = '平均距离'">平均距离(mi)</button>
    </div>

    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">加载地图数据中...</div>

    <div class="chart-row" v-if="ready">
      <div class="map-card">
        <div ref="mapChart" class="map-chart"></div>
      </div>
    </div>
    <div class="chart-row" v-if="ready">
      <div class="rank-card">
        <div class="rank-title">TOP5 - {{ metric }}</div>
        <div ref="rankChart" class="chart" style="height:280px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { fetchMapData } from '../../api/index.js'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const view = ref('pickup'), metric = ref('订单量')
const ready = ref(false), mapData = ref(null)
const mapChart = ref(null), rankChart = ref(null)
let charts = {}, geoLoaded = false

const load = async () => {
  ready.value = false
  try { mapData.value = await fetchMapData({ start_month: props.startMonth, end_month: props.endMonth, company: props.filters.company, borough: props.filters.borough }) }
  catch (e) { console.error(e) }
  ready.value = true; await nextTick()
  if (!geoLoaded) {
    try {
      const resp = await fetch('/nyc-taxi-zones.json')
      echarts.registerMap('nycZones', await resp.json())
      geoLoaded = true
    } catch (e) { console.error('GeoJSON load failed:', e) }
  }
  renderAll()
}

const fieldKey = (m) => ({ '订单量':'订单量','平均费用':'平均费用','平均距离':'平均距离' }[m]||'订单量')

const renderAll = () => {
  const d = mapData.value; if (!d) return
  const current = view.value==='pickup' ? d.pickup : d.dropoff
  if (!current.length) return
  const field = fieldKey(metric.value)

  if (mapChart.value && geoLoaded) {
    if (!charts.map) charts.map = echarts.init(mapChart.value, 'vintage-warm')
    const dm = {}; current.forEach(z => { dm[z.location_id]=z[field]||0 })
    const maxV = Math.ceil(Math.max(...Object.values(dm).filter(v=>v>0))||100)
    charts.map.setOption({
      tooltip:{trigger:'item',formatter:p=>{
        const z=current.find(z=>z.location_id===parseInt(p.name))
        return `<strong>${z?.zone_name||'Zone '+p.name}</strong><br/>${metric.value}: <b>${(p.data?.value||0).toLocaleString()}</b><br/>订单量: ${(z?.订单量||0).toLocaleString()}<br/>平均费用: $${(z?.平均费用||0).toFixed(1)}<br/>平均距离: ${(z?.平均距离||0).toFixed(1)}mi`
      }},
      visualMap:{min:0,max:maxV,calculable:true,orient:'horizontal',left:'center',bottom:8,textStyle:{color:'#5c3d2e'},inRange:{color:['#fffdf7','#d4c4a8','#2f7b9e','#2f7b9e','#2f7b9e','#93C5FD']}},
      series:[{type:'map',map:'nycZones',roam:true,zoom:1.2,center:[-73.94,40.71],nameProperty:'LocationID',
        data:Object.entries(dm).map(([id,val])=>({name:Number(id),value:parseFloat(val.toFixed(1))})),
        label:{show:false},emphasis:{label:{show:true,fontSize:9},itemStyle:{areaColor:'#ca6924'}},itemStyle:{borderColor:'#d4c4a8',borderWidth:0.6,areaColor:'#fffdf7'},
      }],
    })
  }

  if (rankChart.value) {
    if (!charts.rank) charts.rank = echarts.init(rankChart.value, 'vintage-warm')
    const sorted = [...current].sort((a,b)=>(b[field]||0)-(a[field]||0)).slice(0,5)
    charts.rank.setOption({
      tooltip:{trigger:'axis'}, grid:{containLabel:true,left:160},
      xAxis:{type:'value',name:metric.value},
      yAxis:{type:'category',data:sorted.map(d=>d.zone_name||`Zone ${d.location_id}`).reverse(),axisLabel:{fontSize:11}},
      series:[{type:'bar',barWidth:'50%',data:sorted.map(d=>d[field]||0).reverse(),
        itemStyle:{borderRadius:[0,6,6,0],color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#2f7b9e'},{offset:1,color:'#2f7b9e'}])},
        label:{show:true,position:'right',fontWeight:'bold',formatter:p=>metric.value==='订单量'?p.value.toLocaleString():p.value.toFixed(1)}}],
    })
  }
}

watch([()=>props.filters,()=>props.startMonth,()=>props.endMonth],()=>load(),{deep:true})
watch([view,metric],()=>{if(ready.value)renderAll()})
onMounted(load)
onUnmounted(()=>Object.values(charts).forEach(c=>c?.dispose()))
</script>

<style scoped>
.info-card { background:rgba(139,69,19,0.08); border-left:4px solid #cd853f; border-radius:16px; padding:14px 20px; margin-bottom:20px; display:flex; gap:12px; align-items:flex-start; }
.info-icon { font-size:20px; }
.info-text { font-size:12px; color:#8b7355; line-height:1.5; }
.info-text strong { color:#8b4513; }
.controls { display:flex; gap:8px; align-items:center; margin-bottom:16px; flex-wrap:wrap; }
.ctrl-label { font-size:13px; color:#8b7355; }
.sep { color:#c4b090; margin:0 4px; }
.controls button { background:rgba(30,41,59,0.8); border:1px solid rgba(86,138,234,0.3); padding:6px 14px; border-radius:20px; color:#8b7355; cursor:pointer; font-size:12px; transition:0.2s; }
.controls button.active { background:#568aea; border-color:#568aea; color:white; }
.controls button:hover:not(.active) { border-color:#2f7b9e; color:#5c3d2e; }
.chart-row { display:flex; gap:20px; margin-bottom:20px; flex-wrap:wrap; }
.chart-row > * { flex:1; min-width:280px; }
.map-card { position:relative; background:rgba(255,252,245,0.85); border:1px solid rgba(86,138,234,0.2); border-radius:8px; padding:4px; min-height:540px; }
.map-chart { width:100%; height:540px; }
.rank-card { background:rgba(255,252,245,0.85); border:1px solid rgba(86,138,234,0.2); border-radius:8px; padding:16px 20px; }
.rank-title { font-size:15px; font-weight:600; color:#5c3d2e; margin-bottom:12px; }
.chart { width:100%; }
</style>
