<template>
  <div>
    <div class="chart-row">
      <HourlyTrendChart :data="data" />
      <CompanyPieChart :data="data" />
      <RadarChart :data="data" />
    </div>
    <div class="chart-row">
      <BoroughBarChart :data="data" @drill-down="(dim, val) => $emit('drill-down', dim, val)" />
      <FareLevelChart :data="data" />
      <PaymentChart :data="data" />
    </div>
    <div class="chart-row">
      <WeeklyTrendChart :data="data" />
      <PeriodPieChart :data="data" />
      <PassengerChart :data="data" />
    </div>
    <div class="chart-row">
      <ComparisonBarChart :data="data" />
      <CorrelationHeatmap :data="data" />
    </div>
  </div>
</template>

<script setup>
import HourlyTrendChart from '../charts/HourlyTrendChart.vue'
import CompanyPieChart from '../charts/CompanyPieChart.vue'
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
</script>

<style scoped>
.chart-row {
  display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;
}
@media (max-width: 1200px) { .chart-row { flex-direction: column; } }
</style>
