<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <button class="close-btn" @click="close">✕</button>
        </div>
        <div class="modal-body">
          <div class="kpi-grid" v-if="data.kpi">
            <div class="kpi-item" v-for="(val, key) in data.kpi" :key="key">
              <div class="kpi-val">{{ formatCell(val) }}</div>
              <div class="kpi-lbl">{{ key }}</div>
            </div>
          </div>
          <div class="chart-row" v-if="data.hourly_trend">
            <div ref="drillChart" class="drill-chart"></div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  visible: Boolean,
  title: String,
  data: Object,
})
const emit = defineEmits(['close'])
const drillChart = ref(null)
let chart = null

const formatCell = (v) => {
  if (typeof v === 'number') return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v.toFixed(1)
  return v ?? '-'
}

const close = () => emit('close')

const render = async () => {
  if (!drillChart.value || !props.data?.hourly_trend) return
  await nextTick()
  if (chart) chart.dispose()
  chart = echarts.init(drillChart.value, 'vintage-warm')
  const hourly = Object.entries(props.data.hourly_trend).sort((a, b) => a[0] - b[0])
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hourly.map(d => d[0] + ':00') },
    yAxis: { type: 'value', name: '订单量' },
    series: [{
      data: hourly.map(d => d[1]), type: 'line', smooth: true,
      areaStyle: { opacity: 0.2 },
      lineStyle: { color: '#3B82F6' },
      label: { show: true, position: 'top', fontSize: 10, formatter: (p) => p.value.toLocaleString() },
    }],
  })
}

watch(() => props.visible, async (v) => { if (v) { await nextTick(); render() } })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-content {
  background: #0F172A; border: 1px solid #374151;
  border-radius: 20px; padding: 24px;
  min-width: 600px; max-width: 800px; max-height: 80vh; overflow-y: auto;
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-header h3 { font-size: 20px; color: #F3F4F6; margin: 0; }
.close-btn {
  background: none; border: none; color: #9CA3AF; font-size: 20px;
  cursor: pointer; padding: 4px 8px; border-radius: 8px;
}
.close-btn:hover { background: rgba(255,255,255,0.1); color: #F3F4F6; }
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-item { text-align: center; background: rgba(30,41,59,0.5); border-radius: 12px; padding: 12px 8px; }
.kpi-val { font-size: 20px; font-weight: 700; color: #60A5FA; }
.kpi-lbl { font-size: 11px; color: #9CA3AF; margin-top: 4px; }
.drill-chart { width: 100%; height: 260px; }
</style>
