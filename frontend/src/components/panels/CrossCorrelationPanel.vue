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
        tooltip:{trigger:'axis'},
        xAxis:{type:'category',data:cats,axisLabel:{rotate:15,fontSize:8}, name:d.data.x_label||'', nameLocation:'center', nameGap:22, nameTextStyle:{fontSize:10,color:'#8b7355'}},
        yAxis:{type:'value', name:d.data.y_label||'', nameLocation:'center', nameGap:35, nameTextStyle:{fontSize:10,color:'#8b7355'}},
        series:names.map(n=>({name:n,type:'bar',data:series[n],barWidth:names.length>1?'40%':'60%'})),
        legend:names.length>1?{data:names,textStyle:{color:'#8b7355',fontSize:10},top:0}:undefined,
      })
    } else if (d.chart_type==='line') {
      const cats=d.data.categories,series=d.data.series,names=Object.keys(series)
      charts[i].setOption({
        tooltip:{trigger:'axis'},
        xAxis:{type:'category',data:cats,axisLabel:{rotate:15,fontSize:8}, name:d.data.x_label||'', nameLocation:'center', nameGap:22, nameTextStyle:{fontSize:10,color:'#8b7355'}},
        yAxis:{type:'value', name:d.data.y_label||'', nameLocation:'center', nameGap:35, nameTextStyle:{fontSize:10,color:'#8b7355'}},
        series:names.map(n=>({name:n,type:'line',smooth:true,data:series[n],symbolSize:4})),
        legend:{data:names,textStyle:{color:'#8b7355',fontSize:10},top:0},
      })
    } else if (d.chart_type==='heatmap') {
      const cats=d.data.categories, rows=d.data.rows, vals=d.data.values
      const heatData = []
      for (let r = 0; r < rows.length; r++)
        for (let c = 0; c < cats.length; c++)
          heatData.push([c, r, vals[r]?.[c] || 0])
      charts[i].setOption({
        tooltip: { formatter: p => `${rows[p.data[1]]}<br/>${cats[p.data[0]]}：<b>${(p.data[2]*100).toFixed(1)}%</b>` },
        grid: { top: 5, right: 20, bottom: 50, left: 60 },
        xAxis: { type: 'category', data: cats, axisLabel: { rotate: 20, fontSize: 9 }, position: 'bottom' },
        yAxis: { type: 'category', data: rows, axisLabel: { fontSize: 10 } },
        visualMap: { min: 0, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 5,
          inRange: { color: ['#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027'] },
          formatter: v => (v * 100).toFixed(0) + '%' },
        series: [{ type: 'heatmap', data: heatData, label: { show: true, formatter: p => (p.data[2] * 100).toFixed(1) + '%', fontSize: 9 } }],
      })
    } else if (d.chart_type==='scatter') {
      const pts = d.data.points || []
      const sizes = pts.map(p => Math.max(8, Math.min(60, Math.sqrt(p.size || 100) * 0.8)))
      charts[i].setOption({
        tooltip: { formatter: p => `<b>${p.data[3]}</b><br/>距离：${p.data[0].toFixed(1)} mi<br/>费用：$${p.data[1].toFixed(2)}<br/>订单量：${p.data[2].toLocaleString()}` },
        grid: { top: 10, right: 20, bottom: 35, left: 55 },
        xAxis: { type: 'value', name: d.data.x_label || '', nameTextStyle: { fontSize: 10, color: '#5c3d2e' }, axisLabel: { fontSize: 9 } },
        yAxis: { type: 'value', name: d.data.y_label || '', nameTextStyle: { fontSize: 10, color: '#5c3d2e' }, axisLabel: { fontSize: 9 } },
        series: [{
          type: 'scatter', data: pts.map((p, idx) => [p.x, p.y, sizes[idx], p.label]),
          symbolSize: val => val[2],
          itemStyle: { color: '#568aea', opacity: 0.7, borderColor: '#fff', borderWidth: 1 },
          label: { show: true, formatter: p => p.data[3], position: 'right', fontSize: 8, color: '#5c3d2e' },
          emphasis: { itemStyle: { opacity: 1, shadowBlur: 8 } },
        }],
      })
    } else if (d.chart_type==='funnel') {
      const items = d.data.items || []
      const total = items.reduce((s, it) => s + it.value, 0)
      charts[i].setOption({
        tooltip: { formatter: p => `${p.data.name}：${p.data.value.toLocaleString()} 单 (${(p.data.value/total*100).toFixed(1)}%)` },
        series: [{
          type: 'funnel', left: '15%', right: '15%', top: 10, bottom: 10,
          minSize: '20%', maxSize: '100%', gap: 4,
          label: { show: true, position: 'inside', fontSize: 10, formatter: p => `${p.data.name}\n${p.data.value.toLocaleString()}` },
          data: items.map(it => ({ name: it.name, value: it.value })),
          itemStyle: { borderColor: '#fff', borderWidth: 1 },
        }],
      })
    } else if (d.chart_type==='pie') {
      const items = d.data.items || []
      const colors = ['#568aea', '#e6b422', '#4a7c59', '#c23531', '#9b59b6', '#e68a2e']
      charts[i].setOption({
        tooltip: { formatter: p => `${p.data.name}：${p.data.value.toLocaleString()} 单 (${p.percent}%)` },
        legend: { top: 5, textStyle: { fontSize: 9, color: '#5c3d2e' } },
        series: [{
          type: 'pie', radius: ['30%', '65%'], center: ['50%', '55%'], roseType: 'area',
          data: items.map((it, idx) => ({ name: it.name, value: it.value, itemStyle: { color: colors[idx % colors.length] } })),
          label: { fontSize: 9, formatter: '{b}\n{d}%' },
        }],
      })
    } else if (d.chart_type==='radar') {
      const ind = d.data.indicators || []
      const maxVals = d.data.max_values || ind.map(() => 100)
      const series = d.data.series || []
      const colors = ['#568aea', '#c23531', '#4a7c59']
      charts[i].setOption({
        tooltip: {},
        legend: { data: series.map(s => s.name), top: 0, textStyle: { fontSize: 9, color: '#5c3d2e' } },
        radar: {
          center: ['50%', '55%'], radius: '60%',
          indicator: ind.map((name, idx) => ({ name, max: maxVals[idx] || 100 })),
          name: { textStyle: { fontSize: 9, color: '#5c3d2e' } },
        },
        series: [{
          type: 'radar',
          data: series.map((s, idx) => ({
            name: s.name, value: s.values,
            areaStyle: { color: colors[idx % colors.length], opacity: 0.2 },
            lineStyle: { color: colors[idx % colors.length], width: 2 },
            itemStyle: { color: colors[idx % colors.length] },
            symbol: 'circle', symbolSize: 3,
          })),
        }],
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
