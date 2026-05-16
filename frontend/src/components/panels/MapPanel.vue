<template>
  <div>
    <div class="info-card">
      <div class="info-icon">🗺️</div>
      <div class="info-text"><strong>NYC 出租车区域订单特点地图：</strong>263个Taxi Zone。颜色深浅=指标高低。</div>
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
      <span class="sep">|</span>
      <button :class="{ active: chartMode === 'bar' }" @click="toggleView">{{ chartMode === 'map' ? '📊 柱状图' : '🗺️ 地图' }}</button>
    </div>

    <div v-if="!ready" style="color:#8b7355;text-align:center;padding:40px;">加载地图数据中...</div>

    <div class="map-card" v-show="ready">
      <div ref="mapChart" class="map-chart"></div>
    </div>

    <div class="chart-explain" v-if="ready && chartMode === 'bar'">
      <strong>📖 柱状图分析：</strong>{{ barAnalysis }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { fetchMapData } from '../../api/index.js'

const props = defineProps({ filters: Object, startMonth: Number, endMonth: Number })
const view = ref('pickup'), metric = ref('订单量'), chartMode = ref('map')
const ready = ref(false), mapData = ref(null)
const mapChart = ref(null)
let chartMap = null, geoLoaded = false

const fieldKey = (m) => ({ '订单量':'订单量','平均费用':'平均费用','平均距离':'平均距离' }[m]||'订单量')

const fmtVal = (v, field) => {
  if (field === '订单量') return Math.round(v).toLocaleString()
  return Number(v).toFixed(2)
}

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
    } catch (e) { console.error('GeoJSON failed:', e); return }
  }
  renderMap()
}

const renderMap = () => {
  const d = mapData.value; if (!d) return
  const current = view.value==='pickup' ? d.pickup : d.dropoff
  if (!current.length) return
  const field = fieldKey(metric.value)

  if (!mapChart.value || !geoLoaded) return
  if (chartMap) chartMap.dispose()
  chartMap = echarts.init(mapChart.value)

  const seriesData = current
    .filter(z => (z[field]||0) > 0)
    .map(z => ({ name: z.zone_name, value: z[field] || 0 }))

  const values = seriesData.map(d => d.value)
  const maxV = values.length ? Math.ceil(Math.max(...values)) : 100

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        if (!p || p.value === undefined) return ''
        const z = current.find(z => z.zone_name === p.name)
        if (!z) return `${p.name}<br/>${metric.value}: <b>${fmtVal(p.value, field)}</b>`
        return `<strong>${z.zone_name}</strong><br/>
          行政区: ${z['行政区']||'-'}<br/>
          ${metric.value}: <b>${fmtVal(z[field]||0, field)}</b><br/>
          订单量: ${Math.round(z['订单量']||0).toLocaleString()}<br/>
          平均费用: $${(z['平均费用']||0).toFixed(2)}<br/>
          平均距离: ${(z['平均距离']||0).toFixed(2)} mi`
      },
    },
    visualMap: {
      left: 'right',
      min: 0, max: maxV,
      calculable: true,
      inRange: { color: ['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#ffffbf','#fee090','#fdae61','#f46d43','#d73027','#a50026'] },
      text: ['高', '低'],
    },
    series: [{
      id: 'population',
      type: 'map', map: 'nycZones',
      roam: true,
      animationDurationUpdate: 1000,
      universalTransition: true,
      nameProperty: 'zone',
      data: seriesData,
      emphasis: { label: { show: true, fontSize: 10, fontWeight: 'bold' } },
    }],
  }

  // 柱状图 — 只显示前20
  const sorted = [...seriesData].sort((a,b) => b.value - a.value).slice(0, 20)
  const barOption = {
    tooltip: { trigger: 'axis', formatter: (p) => `${p[0].name}<br/>${metric.value}: <b>${fmtVal(p[0].value, field)}</b>` },
    grid: { left: 120, right: 60, top: 10, bottom: 10 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: sorted.map(d => d.name).reverse(), axisLabel: { fontSize: 10 } },
    animationDurationUpdate: 1000,
    series: { type: 'bar', id: 'population', data: sorted.map(d => d.value).reverse(), universalTransition: true,
      itemStyle: { borderRadius: [0,6,6,0], color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#4575b4'},{offset:1,color:'#d73027'}]) } },
  }

  chartMap._mapOption = option
  chartMap._barOption = barOption
  chartMap.setOption(chartMode.value === 'bar' ? barOption : option, true)
}

const barAnalysis = computed(() => {
  const d = mapData.value; if (!d) return ''
  const current = view.value === 'pickup' ? d.pickup : d.dropoff
  if (!current?.length) return ''
  const field = fieldKey(metric.value)
  const sorted = [...current].sort((a, b) => (b[field] || 0) - (a[field] || 0))
  const mode = view.value === 'pickup' ? '上车' : '下车'
  const name = (z) => z.zone_name || '未知区域'
  const val = (z) => Math.round(z[field] || 0)
  const boro = (z) => z['行政区'] || '未知'

  const top3 = sorted.slice(0, 3)
  const totalVal = sorted.reduce((s, z) => s + val(z), 0)
  const top3Total = top3.reduce((s, z) => s + val(z), 0)
  const top3Pct = totalVal > 0 ? (top3Total / totalVal * 100).toFixed(0) : 0
  const gap12 = val(top3[1]) > 0 ? (val(top3[0]) / val(top3[1])).toFixed(1) : 0

  // 行政区集中度
  const boroMap = {}
  sorted.forEach(z => { const b = boro(z); boroMap[b] = (boroMap[b] || 0) + val(z) })
  const topBoro = Object.entries(boroMap).sort((a, b) => b[1] - a[1])[0]
  const boroPct = topBoro && totalVal > 0 ? (topBoro[1] / totalVal * 100).toFixed(0) : 0

  const metricsLabel = { '订单量': '单', '平均费用': '美元', '平均距离': '英里' }
  const unit = metricsLabel[metric.value] || ''

  let text = `① ${name(top3[0])}（${boro(top3[0])}）以 ${val(top3[0]).toLocaleString()}${unit} 位居第一，`
  text += `是第二名 ${name(top3[1])} 的 ${gap12} 倍。`
  text += `② Top 3 区域合计贡献了全城 ${top3Pct}% 的${mode}${metric.value}，`
  text += `其中 ${topBoro?.[0]} 独占 ${boroPct}%，为绝对核心。③ `

  if (metric.value === '订单量') {
    if (mode === '上车') text += '高订单量上车点对应交通枢纽和商业中心，建议在这些区域增加运力调度以减少乘客等待时间。'
    else text += '下车热点集中在 CBD 和机场，高峰时段拥堵严重，建议关注下车效率对周转率的影响。'
  } else if (metric.value === '平均费用') {
    text += '费用最高的区域通常对应机场及远郊区，长途行程的客单价虽高但周转率低，司机需权衡收益效率。'
  } else {
    text += '高距离区域集中在机场和郊区，反映了跨区长途出行的空间特征，短途订单虽多但总额贡献有限。'
  }

  return text
})

const toggleView = () => {
  chartMode.value = chartMode.value === 'map' ? 'bar' : 'map'
  if (!chartMap) return
  chartMap.setOption(chartMode.value === 'bar' ? chartMap._barOption : chartMap._mapOption, true)
}

watch([()=>props.filters,()=>props.startMonth,()=>props.endMonth],()=>load(),{deep:true})
watch([view,metric],()=>{if(ready.value)renderMap()})
onMounted(load)
onUnmounted(()=> chartMap?.dispose())
</script>

<style scoped>
.info-card { background:rgba(139,69,19,0.08); border-left:4px solid #cd853f; border-radius:16px; padding:14px 20px; margin-bottom:20px; display:flex; gap:12px; align-items:flex-start; }
.info-icon { font-size:20px; }
.info-text { font-size:12px; color:#8b7355; line-height:1.5; }
.info-text strong { color:#8b4513; }
.controls { display:flex; gap:8px; align-items:center; margin-bottom:16px; flex-wrap:wrap; }
.ctrl-label { font-size:13px; color:#8b7355; }
.sep { color:#d4c4a8; margin:0 4px; }
.controls button { background:rgba(139,69,19,0.06); border:1px solid rgba(139,69,19,0.15); padding:6px 14px; border-radius:20px; color:#8b7355; cursor:pointer; font-size:12px; transition:0.2s; }
.controls button.active { background:#8b4513; border-color:#8b4513; color:#fdf6ec; }
.controls button:hover:not(.active) { border-color:#8b4513; color:#5c3d2e; }
.map-card { background:rgba(255,252,245,0.85); border:1px solid rgba(139,69,19,0.1); border-radius:8px; padding:4px; min-height:560px; }
.map-chart { width:100%; height:560px; }
.chart-explain { background:rgba(139,69,19,0.05); border-radius:10px; padding:10px 14px; margin-top:12px; font-size:12px; color:#8b7355; line-height:1.7; }
.chart-explain strong { color:#8b4513; }
</style>
