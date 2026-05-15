<template>
  <div class="chart-card" :class="{ large }">
    <dv-border-box-12>
      <div class="card-header">
        <div class="card-title">
          <span class="title-icon">&#9670;</span>
          {{ title }}
        </div>
        <button class="expand-btn" @click.stop="expandChart" title="放大查看">⛶</button>
      </div>
      <div class="card-sub" v-if="subtitle">{{ subtitle }}</div>
      <slot />
    </dv-border-box-12>
    <slot name="extra" />

    <!-- 放大弹窗 -->
    <Teleport to="body">
      <div v-if="expanded" class="expand-overlay" @click="close">
        <div class="expand-modal" @click.stop>
          <div class="expand-header">
            <span>{{ title }}</span>
            <button @click="close">✕</button>
          </div>
          <div ref="expandDom" class="expand-chart"></div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ title: String, subtitle: String, large: Boolean })
const expanded = ref(false)
const expandDom = ref(null)
let expandedChart = null

const expandChart = async () => {
  expanded.value = true
  await nextTick()
  if (!expandDom.value) return

  if (expandedChart) expandedChart.dispose()

  // Find source canvas in current card (not in overlay)
  const cardEl = expandDom.value.closest('.chart-card')
  const sourceCanvas = cardEl?.querySelector('canvas')
  if (sourceCanvas?.parentElement) {
    const instance = echarts.getInstanceByDom(sourceCanvas.parentElement)
    if (instance) {
      expandedChart = echarts.init(expandDom.value, 'vintage-warm')
      expandedChart.setOption(instance.getOption())
      window.addEventListener('resize', () => expandedChart?.resize())
      return
    }
  }
}

const close = () => { expanded.value = false; expandedChart?.dispose(); expandedChart = null }

onUnmounted(() => expandedChart?.dispose())
</script>

<style scoped>
.chart-card { flex: 1; min-width: 300px; position: relative; }
.chart-card.large { flex: 2; }

.card-header { position: relative; display: flex; justify-content: center; align-items: center; margin-bottom: 4px; }
.card-title { font-size: 15px; font-weight: 600; color: #5c3d2e; display: flex; align-items: center; gap: 8px; text-align: center; }
.title-icon { color: #cd853f; font-size: 12px; }
.card-sub { font-size: 11px; color: #8b7355; margin-bottom: 10px; text-align: center; }

.expand-btn {
  position: absolute; right: 0; top: 50%; transform: translateY(-50%);
  background: none; border: 1px solid rgba(139,69,19,0.2);
  border-radius: 6px; color: #8b7355; cursor: pointer;
  font-size: 16px; padding: 2px 8px; opacity: 0.4; transition: 0.2s;
  line-height: 1;
}
.expand-btn:hover { border-color: #8b4513; color: #5c3d2e; opacity: 1; }

/* 全屏放大 */
.expand-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 2000;
  background: rgba(0,0,0,0.85);
  display: flex; align-items: center; justify-content: center;
  padding: 40px;
}
.expand-modal {
  background: #fdf6ec;
  border-radius: 12px;
  padding: 20px;
  width: 90vw;
  height: 85vh;
  display: flex; flex-direction: column;
}
.expand-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
  font-size: 18px; font-weight: 700; color: #5c3d2e;
}
.expand-header button {
  background: none; border: none;
  font-size: 24px; color: #8b7355; cursor: pointer;
}
.expand-header button:hover { color: #c23531; }
.expand-chart { flex: 1; min-height: 400px; }
</style>
