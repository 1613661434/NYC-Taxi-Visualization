<template>
  <div id="app-root" class="dv-bg">
    <!-- 顶部标题行 — DataV装饰 -->
    <div class="header-top">
      <dv-decoration-10 style="flex:1;height:5px;" />
      <div class="title-center">
        <dv-decoration-8 :color="['#568aea','#000']" style="width:180px;height:45px;" />
        <div class="title-block">
          <span class="title-text">NYC 出租车数据驾驶舱</span>
          <dv-decoration-6 :color="['#50e3c2','#67a1e5']" style="width:280px;height:7px;" />
        </div>
        <dv-decoration-8 :reverse="true" :color="['#568aea','#000']" style="width:180px;height:45px;" />
      </div>
      <dv-decoration-10 style="flex:1;height:5px;" />
    </div>

    <!-- 第二行：副标题平行四边形 -->
    <div class="header-row2">
      <div class="d-flex" style="width:40%">
        <div class="skew-title-left">
          <span class="inner">{{ currentTabLabel }}</span>
        </div>
      </div>
      <div class="d-flex jc-end" style="width:40%">
        <div class="skew-title-right">
          <span class="inner">2018年 NYC TLC 出租车行程数据</span>
        </div>
      </div>
    </div>

    <!-- 主体：左侧筛选 + 右侧内容 -->
    <div class="main-layout">
      <!-- 左侧可折叠筛选栏 -->
      <div class="left-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
          <span v-if="sidebarCollapsed">▶</span>
          <span v-else>◀</span>
        </div>
        <div v-show="!sidebarCollapsed" class="sidebar-content">
          <div class="filter-section">
            <div class="filter-label">
              <i class="filter-icon">📅</i> 月份区间
            </div>
            <select :value="startMonth" @change="e => { startMonth = Number(e.target.value); applyFilters() }">
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
            <span class="range-sep">至</span>
            <select :value="endMonth" @change="e => { endMonth = Number(e.target.value); applyFilters() }">
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
          </div>
          <div class="filter-section">
            <div class="filter-label">
              <i class="filter-icon">🚕</i> 车型
            </div>
            <select :value="filters.company" @change="e => { filters.company = e.target.value; applyFilters() }">
              <option value="">全部车型</option>
              <option value="黄色出租车">黄色出租车</option>
              <option value="绿色出租车">绿色出租车</option>
            </select>
          </div>
          <div class="filter-section">
            <div class="filter-label">
              <i class="filter-icon">📍</i> 行政区
            </div>
            <select :value="filters.borough" @change="e => { filters.borough = e.target.value; applyFilters() }">
              <option value="">全部区域</option>
              <option v-for="b in originalBoroughOptions" :key="b" :value="b">{{ b }}</option>
            </select>
          </div>
          <button class="reset-btn" @click="resetFilters">
            <span>↻ 重置筛选</span>
          </button>
          <div class="export-section">
            <button class="export-btn" @click="exportAllCharts">📥 导出图表</button>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="right-content">
        <!-- Tab 导航 -->
        <div class="tab-bar">
          <button v-for="tab in tabs" :key="tab.id"
            :class="{ active: currentTab === tab.id }"
            @click="currentTab = tab.id">
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>

        <!-- Tab 内容 — DataV边框包裹 -->
        <div class="content-section">
          <dv-border-box-12 v-if="currentTab === 'overview'">
            <OverviewPanel :data="dashboardData" @drill-down="openDrillDown" />
          </dv-border-box-12>
          <dv-border-box-12 v-else-if="currentTab === 'cluster'">
            <AnalysisPanel :filters="filters" :startMonth="startMonth" :endMonth="endMonth" />
          </dv-border-box-12>
          <dv-border-box-12 v-else-if="currentTab === 'prediction'">
            <PredictionPanel :filters="filters" :startMonth="startMonth" :endMonth="endMonth" />
          </dv-border-box-12>
          <dv-border-box-12 v-else-if="currentTab === 'preference'">
            <PreferencePanel :filters="filters" :startMonth="startMonth" :endMonth="endMonth" />
          </dv-border-box-12>
          <dv-border-box-12 v-else-if="currentTab === 'correlation'">
            <AdvancedCorrelationPanel :filters="filters" :startMonth="startMonth" :endMonth="endMonth" />
          </dv-border-box-12>
          <dv-border-box-12 v-else-if="currentTab === 'map'">
            <MapPanel :filters="filters" :startMonth="startMonth" :endMonth="endMonth" />
          </dv-border-box-12>
        </div>

        <!-- 底部装饰 -->
        <div class="footer-bar">
          <dv-decoration-10 style="height:4px;" />
          <div class="footer-text">
            <span>数据来源：NYC Taxi & Limousine Commission (TLC)</span>
            <span>2018年 Trip Record Data | 全字段清洗</span>
          </div>
        </div>
      </div>
    </div>

    <DrillDownModal :visible="drillVisible" :title="drillTitle" :data="drillData" @close="drillVisible = false" />

    <dv-loading v-if="loading">数据加载中...</dv-loading>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { fetchDashboard, fetchDrillDown } from './api/index.js'
import DrillDownModal from './components/common/DrillDownModal.vue'
import OverviewPanel from './components/panels/OverviewPanel.vue'
import AnalysisPanel from './components/panels/AnalysisPanel.vue'
import PredictionPanel from './components/panels/PredictionPanel.vue'
import PreferencePanel from './components/panels/PreferencePanel.vue'
import AdvancedCorrelationPanel from './components/panels/AdvancedCorrelationPanel.vue'
import MapPanel from './components/panels/MapPanel.vue'

const loading = ref(true)
const currentTab = ref('overview')
const startMonth = ref(1)
const endMonth = ref(12)
const sidebarCollapsed = ref(false)
const filters = reactive({ company: '', borough: '' })
const originalBoroughOptions = ref([])
const dashboardData = ref(null)
const drillVisible = ref(false)
const drillTitle = ref('')
const drillData = ref({})

const tabs = [
  { id: 'overview', label: '图表分析', icon: '📊' },
  { id: 'cluster', label: '聚类分析', icon: '🎯' },
  { id: 'prediction', label: '预测建模', icon: '🔮' },
  { id: 'preference', label: '偏好分析', icon: '📋' },
  { id: 'correlation', label: '相关性', icon: '🔗' },
  { id: 'map', label: '地图视图', icon: '🗺️' },
]

const currentTabLabel = computed(() => tabs.find(t => t.id === currentTab.value)?.label || '图表分析')

const fixMonthOrder = () => {
  if (startMonth.value > endMonth.value)
    [startMonth.value, endMonth.value] = [endMonth.value, startMonth.value]
}

const loadDashboard = async () => {
  fixMonthOrder(); loading.value = true
  try {
    const res = await fetchDashboard({
      start_month: startMonth.value, end_month: endMonth.value,
      company: filters.company, borough: filters.borough,
    })
    dashboardData.value = res
    if (originalBoroughOptions.value.length === 0)
      originalBoroughOptions.value = Object.keys(res.borough_dist || {})
  } catch (err) { console.error(err) }
  finally { setTimeout(() => { loading.value = false }, 500) }
}

const applyFilters = () => { fixMonthOrder(); loadDashboard() }

const resetFilters = () => {
  startMonth.value = 1; endMonth.value = 12
  filters.company = ''; filters.borough = ''
  loadDashboard()
}

const exportAllCharts = () => {
  const canvases = document.querySelectorAll('.content-section canvas')
  if (canvases.length === 0) { alert('当前面板无图表'); return }
  canvases.forEach((canvas, i) => {
    if (canvas.width > 50 && canvas.height > 50) {
      setTimeout(() => {
        const link = document.createElement('a')
        link.download = `${currentTab.value}_chart_${i + 1}.png`
        link.href = canvas.toDataURL('image/png')
        link.click()
      }, i * 200)
    }
  })
}

const openDrillDown = async (dimension, value) => {
  drillTitle.value = `${value} - 详细数据`
  drillVisible.value = true
  try {
    drillData.value = await fetchDrillDown({
      dimension, value,
      start_month: startMonth.value, end_month: endMonth.value,
      company: filters.company, borough: filters.borough,
    })
  } catch (e) { console.error(e) }
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') drillVisible.value = false })
})
</script>

<style lang="scss">
#app-root {
  color: #5c3d2e;
  background: linear-gradient(160deg, #fdf6ec 0%, #f7e8d0 30%, #eedcc8 60%, #e8d5b7 100%);
  min-height: 100vh;
  padding: 16px;
  font-family: 'Inter', 'Segoe UI', 'PingFang SC', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 标题 */
.header-top {
  display: flex; justify-content: center; align-items: center;
  gap: 8px; margin-bottom: 10px;
}
.title-center { display: flex; align-items: center; gap: 8px; }
.title-block { text-align: center; }
.title-text {
  font-size: 28px; font-weight: 700;
  color: #8b4513; letter-spacing: 2px;
  text-shadow: 1px 1px 2px rgba(139,69,19,0.15);
}

/* 第二行 */
.header-row2 {
  display: flex; justify-content: space-between;
  padding: 0 8px; margin-bottom: 14px;
}
.skew-title-left {
  font-size: 1.1rem; width: 260px; height: 38px; line-height: 38px;
  text-align: center; transform: skewX(-45deg);
  background: #8b4513; cursor: pointer;
  .inner { display: inline-block; transform: skewX(45deg); color: #fdf6ec; font-weight: 600; }
}
.skew-title-right {
  font-size: 1.1rem; width: 320px; height: 38px; line-height: 38px;
  text-align: center; transform: skewX(45deg);
  background: #a0522d;
  .inner { display: inline-block; transform: skewX(-45deg); color: #fdf6ec; }
}

.d-flex { display: flex; }
.jc-end { justify-content: flex-end; }

/* 主布局 */
.main-layout { display: flex; gap: 12px; }

/* 左侧筛选栏 */
.left-sidebar {
  width: 190px; min-width: 190px;
  background: rgba(255,252,245,0.9);
  border: 1px solid rgba(139,69,19,0.2);
  border-radius: 8px; transition: all 0.3s;
  display: flex; flex-direction: column;
  align-self: flex-start;
  box-shadow: 0 2px 8px rgba(139,69,19,0.08);
  &.collapsed { width: 36px; min-width: 36px; }
}
.sidebar-toggle {
  padding: 10px; cursor: pointer; text-align: center;
  color: #8b4513; font-size: 14px;
  border-bottom: 1px solid rgba(139,69,19,0.1);
  user-select: none;
  &:hover { background: rgba(139,69,19,0.06); }
}
.sidebar-content { padding: 14px; display: flex; flex-direction: column; gap: 16px; }
.filter-section { display: flex; flex-direction: column; gap: 6px; }
.filter-label { font-size: 12px; color: #8b4513; display: flex; align-items: center; gap: 4px; font-weight: 600; }
.filter-icon { font-size: 13px; }
.filter-section select {
  background: #fffdf7; border: 1px solid rgba(139,69,19,0.25);
  padding: 7px 8px; border-radius: 6px; color: #5c3d2e;
  font-size: 12px; outline: none; cursor: pointer; width: 100%;
  &:focus { border-color: #8b4513; }
}
.range-sep { text-align: center; color: #8b4513; font-size: 12px; }
.reset-btn {
  background: linear-gradient(135deg, #8b4513, #a0522d);
  border: none; padding: 8px 0; border-radius: 6px;
  color: #fdf6ec; font-weight: 600; font-size: 12px; cursor: pointer;
  &:hover { opacity: 0.85; }
}
.export-section { margin-top: 4px; }
.export-btn {
  width: 100%; background: rgba(46,139,87,0.12);
  border: 1px solid rgba(46,139,87,0.25);
  padding: 8px 0; border-radius: 6px;
  color: #2e8b57; font-size: 12px; cursor: pointer;
  &:hover { background: rgba(46,139,87,0.25); }
}

/* 右侧内容 */
.right-content { flex: 1; min-width: 0; }

/* Tab 栏 */
.tab-bar {
  display: flex; gap: 3px; margin-bottom: 12px;
  background: rgba(0,0,0,0.04); border-radius: 28px;
  padding: 4px; overflow-x: auto;
  border: 1px solid rgba(139,69,19,0.12);
}
.tab-bar button {
  padding: 8px 14px; border-radius: 26px; border: none;
  background: transparent; color: #8b7355;
  font-size: 12px; cursor: pointer; transition: 0.2s;
  white-space: nowrap; font-weight: 500;
  &:hover { color: #5c3d2e; background: rgba(139,69,19,0.08); }
  &.active { background: linear-gradient(135deg, #8b4513, #a0522d); color: #fdf6ec; }
}

.content-section { min-height: 400px; }

/* 底部 */
.footer-bar { margin-top: 20px; }
.footer-text {
  display: flex; justify-content: center; gap: 24px;
  font-size: 10px; color: #8b7355; margin-top: 8px;
}
</style>
