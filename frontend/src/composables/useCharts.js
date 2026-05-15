import { onUnmounted } from 'vue'

export function useCharts() {
  const instances = {}

  const initChart = (key, domRef) => {
    if (!domRef?.value) return null
    if (instances[key]) instances[key].dispose()
    const instance = window.echarts.init(domRef.value)
    instances[key] = instance
    return instance
  }

  const resizeAll = () => {
    Object.values(instances).forEach(ch => ch?.resize())
  }

  const disposeAll = () => {
    Object.values(instances).forEach(ch => ch?.dispose())
    Object.keys(instances).forEach(k => delete instances[k])
  }

  return { initChart, resizeAll, disposeAll, instances }
}
