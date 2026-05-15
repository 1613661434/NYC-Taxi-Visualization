<template>
  <div class="kpi-grid">
    <div class="kpi-card" v-for="(item, idx) in kpiList" :key="idx">
      <div class="kpi-border">
        <div class="kpi-icon">{{ item.icon }}</div>
        <div class="kpi-number">{{ formatNumber(item.value) }}<span class="kpi-unit">{{ item.unit }}</span></div>
        <div class="kpi-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatNumber } from '../../utils/formatters.js'

const props = defineProps({ data: Object })

const kpiList = computed(() => {
  const k = props.data || {}
  return [
    { icon: '🚕', label: '总订单量', value: k.总行程数 || 0, unit: '单' },
    { icon: '💰', label: '总营收', value: k['总营收(万美元)'] || 0, unit: '万美元' },
    { icon: '💝', label: '平均小费率', value: k['平均小费率(%)'] || 0, unit: '%' },
    { icon: '📏', label: '平均行程距离', value: k['平均行程(英里)'] || 0, unit: '英里' },
    { icon: '💵', label: '平均费用', value: k['平均费用($)'] || 0, unit: '$' },
    { icon: '⏰', label: '晚高峰占比', value: k['晚高峰占比(%)'] || 0, unit: '%' },
  ]
})
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  position: relative;
  background: rgba(255,252,245,0.85);
  border: 1px solid rgba(139,69,19,0.2);
  border-radius: 6px;
  padding: 16px 14px;
  transition: all 0.25s;
}

.kpi-card::before {
  content: '';
  position: absolute; top: -1px; left: -1px;
  width: 12px; height: 12px;
  border-left: 2px solid #cd853f;
  border-top: 2px solid #cd853f;
}

.kpi-card::after {
  content: '';
  position: absolute; bottom: -1px; right: -1px;
  width: 12px; height: 12px;
  border-right: 2px solid #cd853f;
  border-bottom: 2px solid #cd853f;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: #8b4513;
  box-shadow: 0 8px 20px -8px rgba(139,69,19,0.25);
}

.kpi-icon { font-size: 28px; margin-bottom: 10px; }
.kpi-number { font-size: 26px; font-weight: 800; color: #5c3d2e; line-height: 1.2; }
.kpi-unit { font-size: 12px; font-weight: 400; color: #8b7355; margin-left: 4px; }
.kpi-label { font-size: 12px; color: #8b7355; margin-top: 6px; }

@media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
</style>
