<template>
  <div class="data-table-wrapper">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" @click="sortBy(col.key)" class="sortable">
            {{ col.label }}
            <span v-if="sortKey === col.key">{{ sortDir === 'asc' ? '▲' : '▼' }}</span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in sortedRows" :key="i">
          <td v-for="col in columns" :key="col.key">{{ formatCell(row[col.key]) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
})

const sortKey = ref('')
const sortDir = ref('asc')

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  const sorted = [...props.rows].sort((a, b) => {
    const va = a[sortKey.value] ?? 0, vb = b[sortKey.value] ?? 0
    return typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb))
  })
  return sortDir.value === 'desc' ? sorted.reverse() : sorted
})

const formatCell = (v) => {
  if (typeof v === 'number') return v.toLocaleString()
  return v ?? '-'
}
</script>

<style scoped>
.data-table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  background: rgba(30,41,59,0.8);
  color: #CBD5E1;
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #374151;
}
.data-table th.sortable { cursor: pointer; user-select: none; }
.data-table th.sortable:hover { color: #60A5FA; }
.data-table td {
  padding: 8px 14px;
  color: #E5E7EB;
  border-bottom: 1px solid #1F2937;
}
.data-table tbody tr:hover { background: rgba(59,130,246,0.08); }
</style>
