<template>
  <div class="chart-card" :class="{ large }">
    <dv-border-box-12>
      <div class="card-header">
        <div class="card-title">
          <span class="title-icon">&#9670;</span>
          {{ title }}
        </div>
      </div>
      <div class="card-sub" v-if="subtitle">{{ subtitle }}</div>
      <slot />
    </dv-border-box-12>
    <slot name="extra" />
  </div>
</template>

<script setup>
defineProps({ title: String, subtitle: String, large: Boolean })
</script>

<style scoped>
.chart-card { flex: 1; min-width: 280px; }
.chart-card.large { flex: 2; }

.card-header { display: flex; justify-content: center; align-items: center; margin-bottom: 4px; }
.card-title { font-size: 18px; font-weight: 700; color: #3b1f0e; display: flex; align-items: center; gap: 8px; text-align: center; }
.title-icon { color: #c23531; font-size: 14px; }
.card-sub { font-size: 11px; color: #8b7355; margin-bottom: 10px; text-align: center; }
</style>
