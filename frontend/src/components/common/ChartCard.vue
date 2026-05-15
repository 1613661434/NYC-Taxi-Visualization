<template>
  <div class="chart-card" :class="{ large, zoomed: enlarged }">
    <dv-border-box-12>
      <div class="card-header">
        <div class="card-title">
          <span class="title-icon">&#9670;</span>
          {{ title }}
        </div>
        <button class="expand-btn" @click.stop="enlarged = !enlarged" title="放大查看">⛶</button>
      </div>
      <div class="card-sub" v-if="subtitle && !enlarged">{{ subtitle }}</div>
      <slot />
    </dv-border-box-12>
    <slot name="extra" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

defineProps({ title: String, subtitle: String, large: Boolean })
const enlarged = ref(false)

watch(enlarged, async (v) => {
  await nextTick()
  setTimeout(() => window.dispatchEvent(new Event('resize')), 200)
})
</script>

<style scoped>
.chart-card { flex: 1; min-width: 300px; transition: all 0.35s ease; }
.chart-card.large { flex: 2; }

/* 放大状态 */
.chart-card.zoomed {
  position: fixed; inset: 0; z-index: 2000;
  background: #fdf6ec;
  display: flex; align-items: center; justify-content: center;
  padding: 5vw;
}
.chart-card.zoomed :deep(.dv-border-box-12) {
  width: 85vw; height: 85vh;
  background: #fdf6ec;
  border-radius: 12px;
  padding: 20px;
}
.chart-card.zoomed :deep(canvas) {
  width: 100% !important;
  height: calc(100% - 40px) !important;
}

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
</style>
