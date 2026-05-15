import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import DataV from 'datav-vue3'
import 'echarts/theme/vintage.js'
import * as echarts from 'echarts'

// 基于 vintage 扩展，优化文字样式
echarts.registerTheme('vintage-warm', {
  color: ['#c23531', '#2f7b9e', '#d48265', '#61a0a8', '#8b5e3c', '#749f83', '#ca6924', '#b84c5c', '#4a7c59', '#9b59b6'],
  textStyle: { color: '#4a3028', fontSize: 13, fontFamily: "'Inter','PingFang SC',sans-serif" },
  title: { textStyle: { color: '#5c3d2e', fontSize: 16, fontWeight: 'bold' } },
  legend: { textStyle: { color: '#5c3d2e', fontSize: 12 } },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#6b3a2a', width: 1.5 } },
    axisTick: { lineStyle: { color: '#6b3a2a' } },
    axisLabel: { color: '#3b1f0e', fontSize: 13, fontWeight: 'bold' },
    nameTextStyle: { color: '#5c3d2e', fontSize: 12, fontWeight: 'bold' },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#5c3d2e', fontSize: 12, fontWeight: 'bold' },
    nameTextStyle: { color: '#5c3d2e', fontSize: 12, fontWeight: 'bold' },
    splitLine: { lineStyle: { color: '#d4c4a8', type: 'dashed', width: 1 } },
  },
  tooltip: {
    backgroundColor: 'rgba(255,252,245,0.97)',
    borderColor: '#cd853f',
    textStyle: { color: '#4a3028', fontSize: 13 },
  },
  grid: { containLabel: true },
})

const app = createApp(App)
app.use(DataV, { classNamePrefix: 'dv-' })
app.mount('#app')
