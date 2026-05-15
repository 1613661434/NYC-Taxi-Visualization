<template>
  <div class="filter-toolbar">
    <div class="filter-group">
      <label>月份区间：</label>
      <select :value="startMonth" @change="$emit('update:startMonth', Number($event.target.value))">
        <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
      </select>
      <span>-</span>
      <select :value="endMonth" @change="$emit('update:endMonth', Number($event.target.value))">
        <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
      </select>
    </div>
    <div class="filter-group">
      <label>车型：</label>
      <select :value="filters.company" @change="$emit('update:company', $event.target.value)">
        <option value="">全部</option>
        <option value="黄色出租车">黄色出租车</option>
        <option value="绿色出租车">绿色出租车</option>
      </select>
    </div>
    <div class="filter-group">
      <label>行政区：</label>
      <select :value="filters.borough" @change="$emit('update:borough', $event.target.value)">
        <option value="">全部</option>
        <option v-for="b in boroughOptions" :key="b" :value="b">{{ b }}</option>
      </select>
    </div>
    <button class="reset-btn" @click="$emit('reset')">重置筛选</button>
    <div class="filter-note">筛选后全图表联动刷新</div>
  </div>
</template>

<script setup>
defineProps({
  startMonth: Number,
  endMonth: Number,
  filters: Object,
  boroughOptions: Array,
})
defineEmits(['update:startMonth', 'update:endMonth', 'update:company', 'update:borough', 'reset'])
</script>

<style scoped>
.filter-toolbar {
  background: rgba(15,23,42,0.6);
  backdrop-filter: blur(8px);
  border-radius: 48px;
  padding: 12px 24px;
  margin-bottom: 28px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(59,130,246,0.2);
}
.filter-group { display: flex; align-items: center; gap: 8px; }
.filter-group label { font-size: 13px; color: #CBD5E1; }
.filter-group select {
  background: #1E293B;
  border: 1px solid #334155;
  padding: 6px 12px;
  border-radius: 24px;
  color: #F3F4F6;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}
.reset-btn {
  background: #3B82F6;
  border: none;
  padding: 6px 18px;
  border-radius: 32px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}
.reset-btn:hover { background: #2563EB; }
.filter-note { font-size: 11px; color: #6B7280; margin-left: auto; }
@media (max-width: 1200px) { .filter-toolbar { flex-direction: column; align-items: stretch; } }
</style>
