<template>
  <div>
    <!-- 当前页图表 -->
    <div class="chart-row">
      <template v-for="comp in currentPage" :key="comp.name">
        <component :is="comp.c" :data="data" @drill-down="(d, v) => $emit('drill-down', d, v)" />
      </template>
    </div>

    <!-- 分页控制器 -->
    <div class="pager">
      <button :disabled="page === 0" @click="page = 0">◀◀</button>
      <button :disabled="page === 0" @click="page--">◀</button>
      <span v-for="(pg, i) in pages" :key="i"
        :class="{ active: page === i, dot: true }"
        @click="page = i">
        {{ pg.label }}
      </span>
      <button :disabled="page === pages.length - 1" @click="page++">▶</button>
      <button :disabled="page === pages.length - 1" @click="page = pages.length - 1">▶▶</button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import HourlyTrendChart from '../charts/HourlyTrendChart.vue'
import RadarChart from '../charts/RadarChart.vue'
import BoroughBarChart from '../charts/BoroughBarChart.vue'
import FareLevelChart from '../charts/FareLevelChart.vue'
import PaymentChart from '../charts/PaymentChart.vue'
import WeeklyTrendChart from '../charts/WeeklyTrendChart.vue'
import PeriodPieChart from '../charts/PeriodPieChart.vue'
import PassengerChart from '../charts/PassengerChart.vue'
import ComparisonBarChart from '../charts/ComparisonBarChart.vue'
import CorrelationHeatmap from '../charts/CorrelationHeatmap.vue'

defineProps({ data: Object })
defineEmits(['drill-down'])

const page = ref(0)

const pages = [
  { label: '时间规律', charts: [
    { c: HourlyTrendChart, name: 'hourly' },
    { c: WeeklyTrendChart, name: 'weekly' },
    { c: PeriodPieChart, name: 'period' },
  ]},
  { label: '车型对比', charts: [
    { c: ComparisonBarChart, name: 'compare' },
    { c: RadarChart, name: 'radar' },
  ]},
  { label: '区域与乘客', charts: [
    { c: BoroughBarChart, name: 'borough' },
    { c: PaymentChart, name: 'payment' },
    { c: PassengerChart, name: 'passenger' },
  ]},
  { label: '费用关联', charts: [
    { c: FareLevelChart, name: 'fare' },
    { c: CorrelationHeatmap, name: 'corr' },
  ]},
]

const currentPage = computed(() => pages[page.value]?.charts || [])
</script>

<style scoped>
.chart-row {
  display: flex; flex-direction: column; gap: 20px; margin-bottom: 20px;
}

/* 分页器 */
.pager {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; margin-top: 8px; padding: 12px 0;
}
.pager button {
  background: rgba(139,69,19,0.08);
  border: 1px solid rgba(139,69,19,0.15);
  border-radius: 6px; color: #8b4513;
  padding: 4px 12px; cursor: pointer; font-size: 13px;
  transition: 0.2s;
}
.pager button:hover:not(:disabled) { background: rgba(139,69,19,0.18); }
.pager button:disabled { opacity: 0.3; cursor: default; }

.pager .dot {
  padding: 4px 14px; border-radius: 14px;
  font-size: 12px; color: #8b7355; cursor: pointer;
  transition: 0.2s; border: 1px solid transparent;
}
.pager .dot:hover { background: rgba(139,69,19,0.06); }
.pager .dot.active {
  background: #8b4513; color: #fdf6ec; font-weight: 600;
}

@media (max-width: 1200px) { .chart-row { flex-direction: column; } }
</style>
