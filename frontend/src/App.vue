<template>
  <div class="dashboard">
    <div class="bg"></div>

    <div class="header">
      <div class="title-box">
        <h1>🗽 纽约出租车数据驾驶舱</h1>
        <p>2018年 {{ startMonth }}-{{ endMonth }}月 · NYC TLC开放数据 · 黄色出租车 vs 绿色出租车</p>
      </div>
      <div class="date-box">
        <div class="date">{{ currentDate }}</div>
        <div class="time">{{ currentTime }}</div>
      </div>
    </div>

    <div class="info-card">
      <div class="info-icon">ℹ️</div>
      <div class="info-text">
        <strong>数据说明：</strong>本大屏基于2018年1-12月纽约市出租车与豪华轿车委员会(TLC)真实行程数据，
        涵盖黄色出租车(Yellow)和绿色出租车(Green)。经过清洗（剔除无效行程、异常费用、重复记录），
        展示订单量、费用分布、时段规律、区域热度等核心指标。所有图表均显示具体数值，支持筛选联动。
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" v-for="(item, idx) in kpiList" :key="idx">
        <div class="kpi-icon">{{ item.icon }}</div>
        <div class="kpi-number">{{ formatNumber(item.value) }}<span class="kpi-unit">{{ item.unit }}</span></div>
        <div class="kpi-label">{{ item.label }}</div>
      </div>
    </div>

    <!-- 筛选栏：已删除费用筛选，修复行政区下拉 -->
    <div class="filter-toolbar">
      <div class="filter-group">
        <label>月份区间：</label>
        <select v-model="startMonth" @change="applyFilters" style="width:70px">
          <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
        </select>
        <span>-</span>
        <select v-model="endMonth" @change="applyFilters" style="width:70px">
          <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
        </select>
      </div>

      <div class="filter-group">
        <label>车型：</label>
        <select v-model="filters.company" @change="applyFilters">
          <option value="">全部</option>
          <option value="黄色出租车">黄色出租车</option>
          <option value="绿色出租车">绿色出租车</option>
        </select>
      </div>
      <div class="filter-group">
        <label>行政区：</label>
        <select v-model="filters.borough" @change="applyFilters">
          <option value="">全部</option>
          <option v-for="b in originalBoroughOptions" :key="b" :value="b">{{ b }}</option>
        </select>
      </div>

      <button class="reset-btn" @click="resetFilters">重置筛选</button>
      <div class="filter-note">※ 筛选后全图表联动刷新</div>
    </div>

    <div class="chart-row">
      <div class="chart-card large">
        <div class="card-title">📊 24小时出行趋势</div>
        <div class="card-sub">各时段订单量变化（体现早/晚高峰）</div>
        <div ref="hourlyChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">🚕 车型订单占比</div>
        <div class="card-sub">黄色出租车 vs 绿色出租车</div>
        <div ref="companyChart" class="chart" style="height: 220px;"></div>
        <div class="stats-row">
          <div class="stat-badge yellow">🚕 黄车: {{ companyStats.yellow.toLocaleString() }}单</div>
          <div class="stat-badge green">🟢 绿车: {{ companyStats.green.toLocaleString() }}单</div>
        </div>
      </div>
      <div class="chart-card">
        <div class="card-title">⭐ 多维性能雷达</div>
        <div class="card-sub">黄车 vs 绿车 核心指标对比</div>
        <div ref="radarChart" class="chart"></div>
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-card">
        <div class="card-title">📍 行政区热度排行 TOP5</div>
        <div class="card-sub">按订单量排序</div>
        <div ref="boroughChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">💰 行程费用等级分布</div>
        <div class="card-sub">各价格区间订单数</div>
        <div ref="fareLevelChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">💳 支付方式对比</div>
        <div class="card-sub">信用卡 vs 现金 vs 其他</div>
        <div ref="paymentChart" class="chart"></div>
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-card large">
        <div class="card-title">📅 一周出行规律</div>
        <div class="card-sub">周一至周日订单量变化</div>
        <div ref="weeklyChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">⏰ 出行时段分布</div>
        <div class="card-sub">早高峰/白天/晚高峰/夜间/深夜</div>
        <div ref="periodChart" class="chart"></div>
      </div>
      <div class="chart-card">
        <div class="card-title">👥 乘客数量分布</div>
        <div class="card-sub">1~6人订单占比</div>
        <div ref="passengerChart" class="chart"></div>
      </div>
    </div>

    <div class="chart-row">
      <div class="chart-card">
        <div class="card-title">⚖️ 黄色 vs 绿色 核心指标对比</div>
        <div class="card-sub">平均费用($) / 平均距离(mi) / 平均小费($)</div>
        <div ref="avgCompareChart" class="chart"></div>
      </div>
      <div class="chart-card large">
        <div class="card-title">🔗 数值字段相关性热力图</div>
        <div class="card-sub">行程距离、费用、小费、乘客数等相关系数</div>
        <div ref="corrChart" class="chart"></div>
      </div>
    </div>

    <div class="footer">
      <div class="footer-line"></div>
      <div class="footer-text">
        <span>数据来源：NYC Taxi & Limousine Commission (TLC) 2018年 Trip Record Data</span>
        <span>清洗说明：剔除距离≤0、费用≤0、时长异常、乘客数>6、区域缺失等记录</span>
        <span>可视化设计：数据可视化期末大作业</span>
      </div>
    </div>

    <div v-if="loading" class="loader-overlay">
      <div class="loader"></div>
      <div class="loader-text">正在加载2018年数据，请稍候...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const loading = ref(true)
const currentDate = ref('')
const currentTime = ref('')
let timer = null

const startMonth = ref(1)
const endMonth = ref(12)

const hourlyChart = ref(null)
const companyChart = ref(null)
const radarChart = ref(null)
const boroughChart = ref(null)
const fareLevelChart = ref(null)
const paymentChart = ref(null)
const weeklyChart = ref(null)
const periodChart = ref(null)
const passengerChart = ref(null)
const avgCompareChart = ref(null)
const corrChart = ref(null)

let chartInstances = {}

const kpiList = ref([
  { icon: '🚕', label: '总订单量', value: 0, unit: '单' },
  { icon: '💰', label: '总营收', value: 0, unit: '万美元' },
  { icon: '💝', label: '平均小费率', value: 0, unit: '%' },
  { icon: '📏', label: '平均行程距离', value: 0, unit: '英里' },
  { icon: '💵', label: '平均费用', value: 0, unit: '$' },
  { icon: '⏰', label: '晚高峰占比', value: 0, unit: '%' }
])

const companyStats = ref({ yellow: 0, green: 0 })
// 修复：保存原始行政区列表（永远显示全部选项）
const originalBoroughOptions = ref([])

// 筛选条件：已删除费用相关
const filters = reactive({
  company: '',
  borough: ''
})

let fullDashboardData = null

const formatNumber = (num) => {
  if (num === undefined || num === null) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

const updateDateTime = () => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

const fixMonthOrder = () => {
  if (startMonth.value > endMonth.value) {
    [startMonth.value, endMonth.value] = [endMonth.value, startMonth.value]
  }
}

// 数据加载：已删除费用参数
const loadDashboardData = async () => {
  fixMonthOrder()
  
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/dashboard-data', {
      params: {
        start_month: startMonth.value,
        end_month: endMonth.value,
        company: filters.company,
        borough: filters.borough
      }
    })
    fullDashboardData = res.data

    const k = fullDashboardData.kpi || {}
    kpiList.value[0].value = k.总行程数 || 0
    kpiList.value[1].value = k['总营收(万美元)'] || 0
    kpiList.value[2].value = k['平均小费率(%)'] || 0
    kpiList.value[3].value = k['平均行程(英里)'] || 0
    kpiList.value[4].value = k['平均费用($)'] || 0
    kpiList.value[5].value = k['晚高峰占比(%)'] || 0

    companyStats.value.yellow = fullDashboardData.company_compare?.黄色出租车 || 0
    companyStats.value.green = fullDashboardData.company_compare?.绿色出租车 || 0

    // 只在首次加载时保存原始行政区列表
    if (originalBoroughOptions.value.length === 0) {
      originalBoroughOptions.value = Object.keys(fullDashboardData.borough_dist || {})
    }

    renderAllCharts(fullDashboardData)
  } catch (err) {
    console.error('数据加载失败', err)
  } finally {
    setTimeout(() => { loading.value = false }, 500)
  }
}

const applyFilters = async () => {
  fixMonthOrder()
  await loadDashboardData()
}

// 重置筛选：已删除费用
const resetFilters = () => {
  startMonth.value = 1
  endMonth.value = 12
  filters.company = ''
  filters.borough = ''
  loadDashboardData()
}

const renderAllCharts = (data) => {
  const hourly = Object.entries(data.hourly_trend || {}).sort((a, b) => a[0] - b[0])
  if (hourlyChart.value) {
    chartInstances.hourly = echarts.init(hourlyChart.value)
    chartInstances.hourly.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', name: '小时', data: hourly.map(d => d[0] + ':00'), axisLabel: { rotate: 0 } },
      yAxis: { type: 'value', name: '订单量 (单)' },
      series: [{
        data: hourly.map(d => d[1]),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#3B82F6' },
        areaStyle: { opacity: 0.2, color: '#3B82F6' },
        label: { show: true, position: 'top', fontWeight: 'bold', fontSize: 11, formatter: (p) => p.value.toLocaleString() }
      }]
    })
  }

  const company = data.company_compare || {}
  if (companyChart.value) {
    chartInstances.company = echarts.init(companyChart.value)
    chartInstances.company.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['50%', '50%'],
        data: [
          { name: '黄色出租车', value: company.黄色出租车 || 0, itemStyle: { color: '#F59E0B' } },
          { name: '绿色出租车', value: company.绿色出租车 || 0, itemStyle: { color: '#10B981' } }
        ],
        label: { show: true, formatter: '{b}: {d}%', fontSize: 12, fontWeight: 'bold' },
        emphasis: { scale: true }
      }]
    })
  }

  const comp = data.yellow_green_comparison || {}
  if (radarChart.value) {
    chartInstances.radar = echarts.init(radarChart.value)
    chartInstances.radar.setOption({
      radar: {
        indicator: [
          { name: '平均费用($)', max: 20 },
          { name: '平均距离(mi)', max: 4 },
          { name: '平均小费($)', max: 3 },
          { name: '效率评分', max: 100 }
        ],
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [
          { value: [comp.平均费用?.黄色出租车 || 0, comp.平均距离?.黄色出租车 || 0, comp.平均小费?.黄色出租车 || 0, 85], name: '黄色出租车', areaStyle: { color: 'rgba(245,158,11,0.2)' }, lineStyle: { color: '#F59E0B' } },
          { value: [comp.平均费用?.绿色出租车 || 0, comp.平均距离?.绿色出租车 || 0, comp.平均小费?.绿色出租车 || 0, 78], name: '绿色出租车', areaStyle: { color: 'rgba(16,185,129,0.2)' }, lineStyle: { color: '#10B981' } }
        ]
      }],
      legend: { data: ['黄色出租车', '绿色出租车'], left: 'center', top: 0, textStyle: { color: '#E5E7EB' } }
    })
  }

  const borough = Object.entries(data.borough_dist || {}).sort((a, b) => b[1] - a[1]).slice(0, 5)
  if (boroughChart.value) {
    chartInstances.borough = echarts.init(boroughChart.value)
    chartInstances.borough.setOption({
      grid: { containLabel: true, left: 70, top: 20 },
      xAxis: { type: 'value', name: '订单量 (单)' },
      yAxis: { type: 'category', data: borough.map(d => d[0]), axisLabel: { fontWeight: 'bold' } },
      series: [{
        data: borough.map(d => d[1]),
        type: 'bar',
        barWidth: '50%',
        itemStyle: { borderRadius: [0, 8, 8, 0], color: '#3B82F6' },
        label: { show: true, position: 'right', fontWeight: 'bold', formatter: (p) => p.value.toLocaleString() }
      }]
    })
  }

  const fare = Object.entries(data.fare_level_dist || {})
  if (fareLevelChart.value) {
    chartInstances.fare = echarts.init(fareLevelChart.value)
    chartInstances.fare.setOption({
      xAxis: { type: 'category', data: fare.map(d => d[0]), axisLabel: { rotate: 15, fontSize: 10 } },
      yAxis: { type: 'value', name: '订单量' },
      series: [{
        data: fare.map(d => d[1]),
        type: 'bar',
        barWidth: '60%',
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#10B981' },
        label: { show: true, position: 'top', fontWeight: 'bold', formatter: (p) => p.value.toLocaleString() }
      }]
    })
  }

  const payment = data.payment_dist || {}
  if (paymentChart.value) {
    chartInstances.payment = echarts.init(paymentChart.value)
    chartInstances.payment.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        data: Object.entries(payment).map(([n, v]) => ({ name: n, value: v })),
        label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
        itemStyle: { borderRadius: 8, borderColor: '#0F172A', borderWidth: 2 }
      }]
    })
  }

  const week = Object.entries(data.weekday_trend || {}).sort((a, b) => a[0] - b[0])
  const weekNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  if (weeklyChart.value) {
    chartInstances.weekly = echarts.init(weeklyChart.value)
    chartInstances.weekly.setOption({
      xAxis: { type: 'category', data: weekNames },
      yAxis: { type: 'value', name: '订单量' },
      series: [{
        data: week.map(d => d[1]),
        type: 'line',
        smooth: true,
        symbol: 'diamond',
        symbolSize: 10,
        lineStyle: { width: 3, color: '#8B5CF6' },
        areaStyle: { opacity: 0.2 },
        label: { show: true, position: 'top', fontWeight: 'bold', formatter: (p) => p.value.toLocaleString() }
      }]
    })
  }

  const period = data.period_dist || {}
  if (periodChart.value) {
    chartInstances.period = echarts.init(periodChart.value)
    chartInstances.period.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: Object.entries(period).map(([n, v]) => ({ name: n, value: v })),
        label: { show: true, formatter: '{b}: {d}%', fontSize: 11 }
      }]
    })
  }

  const passengers = Object.entries(data.passenger_dist || {}).sort((a, b) => a[0] - b[0])
  if (passengerChart.value) {
    chartInstances.passenger = echarts.init(passengerChart.value)
    chartInstances.passenger.setOption({
      xAxis: { type: 'category', data: passengers.map(p => p[0] + '人') },
      yAxis: { type: 'value', name: '订单量' },
      series: [{
        data: passengers.map(p => p[1]),
        type: 'bar',
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#F59E0B' },
        label: { show: true, position: 'top', fontWeight: 'bold', formatter: (p) => p.value.toLocaleString() }
      }]
    })
  }

  if (avgCompareChart.value) {
  chartInstances.avgComp = echarts.init(avgCompareChart.value)
  const yellowFare = comp.平均费用?.['黄色出租车'] || 0
  const greenFare = comp.平均费用?.['绿色出租车'] || 0
  const yellowDist = comp.平均距离?.['黄色出租车'] || 0
  const greenDist = comp.平均距离?.['绿色出租车'] || 0
  const yellowTip = comp.平均小费?.['黄色出租车'] || 0
  const greenTip = comp.平均小费?.['绿色出租车'] || 0

  chartInstances.avgComp.setOption({
    xAxis: { type: 'category', data: ['平均费用 ($)', '平均距离 (mi)', '平均小费 ($)'] },
    yAxis: { type: 'value' },
    series: [
      { 
        name: '黄色出租车', 
        type: 'bar', 
        data: [yellowFare, yellowDist, yellowTip], 
        color: '#F59E0B', 
        label: { show: true, position: 'top', fontWeight: 'bold', formatter: (p) => p.value.toFixed(1) } 
      },
      { 
        name: '绿色出租车', 
        type: 'bar', 
        data: [greenFare, greenDist, greenTip], 
        color: '#10B981', 
        label: { show: true, position: 'top', fontWeight: 'bold', formatter: (p) => p.value.toFixed(1) } 
      }
    ],
    legend: { data: ['黄色出租车', '绿色出租车'], textStyle: { color: '#E5E7EB' }, top: 0, right: 0 }
  })
}

  const corrMatrix = data.correlation || {}
  const fields = Object.keys(corrMatrix)
  if (corrChart.value && fields.length) {
    chartInstances.corr = echarts.init(corrChart.value)
    const values = fields.flatMap((row, i) => fields.map((col, j) => [j, i, corrMatrix[row]?.[col] || 0]))
    chartInstances.corr.setOption({
      xAxis: { type: 'category', data: fields, axisLabel: { rotate: 30, fontSize: 10 } },
      yAxis: { type: 'category', data: fields },
      visualMap: { min: -1, max: 1, calculable: true, inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'] } },
      series: [{
        type: 'heatmap',
        data: values,
        label: { show: true, formatter: (p) => p.data[2].toFixed(2), fontSize: 10 },
        emphasis: { itemStyle: { shadowBlur: 10 } }
      }]
    })
  }
}

const handleResize = () => {
  Object.values(chartInstances).forEach(ch => ch?.resize())
}

onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)
  loadDashboardData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('resize', handleResize)
  Object.values(chartInstances).forEach(ch => ch?.dispose())
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard {
  min-height: 100vh;
  background: radial-gradient(ellipse at 20% 30%, #0B1120 0%, #030712 100%);
  padding: 24px 32px;
  font-family: 'Inter', 'Segoe UI', 'PingFang SC', system-ui, sans-serif;
}

.bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.title-box h1 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #FFFFFF, #60A5FA);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: -0.5px;
}

.title-box p {
  color: #6B7280;
  font-size: 13px;
  margin-top: 6px;
}

.date-box {
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 20px;
  border-radius: 40px;
  backdrop-filter: blur(4px);
  text-align: right;
}

.date {
  font-size: 14px;
  color: #9CA3AF;
}

.time {
  font-size: 20px;
  font-weight: 600;
  color: #F3F4F6;
}

.info-card {
  background: rgba(59, 130, 246, 0.1);
  border-left: 4px solid #3B82F6;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  backdrop-filter: blur(4px);
}

.info-icon {
  font-size: 20px;
}

.info-text {
  font-size: 12px;
  color: #CBD5E1;
  line-height: 1.5;
}

.info-text strong {
  color: #60A5FA;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.kpi-card {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  padding: 18px 16px;
  border: 1px solid rgba(59, 130, 246, 0.25);
  transition: all 0.2s;
}

.kpi-card:hover {
  transform: translateY(-3px);
  border-color: #3B82F6;
  box-shadow: 0 12px 24px -12px rgba(59, 130, 246, 0.3);
}

.kpi-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.kpi-number {
  font-size: 30px;
  font-weight: 800;
  color: #F3F4F6;
  line-height: 1.2;
}

.kpi-unit {
  font-size: 14px;
  font-weight: 400;
  color: #9CA3AF;
  margin-left: 4px;
}

.kpi-label {
  font-size: 13px;
  color: #9CA3AF;
  margin: 8px 0 4px;
}

.filter-toolbar {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 48px;
  padding: 12px 24px;
  margin-bottom: 28px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 13px;
  color: #CBD5E1;
}

.filter-group select, .filter-group input {
  background: #1E293B;
  border: 1px solid #334155;
  padding: 6px 12px;
  border-radius: 24px;
  color: #F3F4F6;
  font-size: 13px;
  outline: none;
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

.reset-btn:hover {
  background: #2563EB;
}

.filter-note {
  font-size: 11px;
  color: #6B7280;
  margin-left: auto;
}

.chart-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.chart-card {
  flex: 1;
  min-width: 280px;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(12px);
  border-radius: 28px;
  padding: 20px 24px;
  border: 1px solid rgba(59, 130, 246, 0.15);
  transition: 0.2s;
}

.chart-card.large {
  flex: 2;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #F3F4F6;
  margin-bottom: 4px;
}

.card-sub {
  font-size: 12px;
  color: #6B7280;
  margin-bottom: 16px;
  border-left: 2px solid #3B82F6;
  padding-left: 10px;
}

.chart {
  width: 100%;
  height: 260px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  gap: 12px;
}

.stat-badge {
  flex: 1;
  text-align: center;
  padding: 6px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.stat-badge.yellow {
  background: rgba(245,158,11,0.15);
  color: #FBBF24;
}

.stat-badge.green {
  background: rgba(16,185,129,0.15);
  color: #34D399;
}

.footer {
  margin-top: 32px;
}

.footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, #3B82F6, #8B5CF6, transparent);
  margin-bottom: 16px;
}

.footer-text {
  display: flex;
  justify-content: center;
  gap: 32px;
  font-size: 11px;
  color: #4B5563;
  flex-wrap: wrap;
}

.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(3, 7, 18, 0.95);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.loader {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loader-text {
  margin-top: 16px;
  color: #CBD5E1;
  font-size: 14px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .chart-row { flex-direction: column; }
  .filter-toolbar { flex-direction: column; align-items: stretch; }
  .filter-note { margin-left: 0; }
}
</style>