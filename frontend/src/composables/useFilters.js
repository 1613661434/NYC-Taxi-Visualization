import { ref, reactive, readonly, watch } from 'vue'

const startMonth = ref(1)
const endMonth = ref(12)
const filters = reactive({ company: '', borough: '' })
const originalBoroughOptions = ref([])
const loading = ref(true)

export function useFilters() {
  const filterParams = () => ({
    start_month: startMonth.value,
    end_month: endMonth.value,
    company: filters.company,
    borough: filters.borough,
  })

  const fixMonthOrder = () => {
    if (startMonth.value > endMonth.value) {
      [startMonth.value, endMonth.value] = [endMonth.value, startMonth.value]
    }
  }

  const resetFilters = () => {
    startMonth.value = 1
    endMonth.value = 12
    filters.company = ''
    filters.borough = ''
  }

  return {
    startMonth: readonly(startMonth),
    endMonth: readonly(endMonth),
    filters,
    originalBoroughOptions,
    loading,
    filterParams,
    fixMonthOrder,
    resetFilters,
    setStartMonth: (v) => { startMonth.value = v },
    setEndMonth: (v) => { endMonth.value = v },
  }
}
