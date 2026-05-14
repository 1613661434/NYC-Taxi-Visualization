<template>
  <div class="grid-container">
    <div class="chart-box">
      <div ref="chart1" class="chart"></div>
    </div>
    <div class="chart-box">
      <div ref="chart2" class="chart"></div>
    </div>
    <div class="chart-box">
      <div ref="chart3" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const chart1 = ref(null)
const chart2 = ref(null)
const chart3 = ref(null)

onMounted(async () => {
  const myChart1 = echarts.init(chart1.value)
  const myChart2 = echarts.init(chart2.value)
  const myChart3 = echarts.init(chart3.value)

  // 相关性热力图
  const corrLabels = ['行程距离', '车费', '小费', '时长', '乘客数']
  const corrData = [
    [0,0,1.00],[0,1,0.94],[0,2,0.32],[0,3,0.88],[0,4,0.11],
    [1,0,0.94],[1,1,1.00],[1,2,0.41],[1,3,0.91],[1,4,0.06],
    [2,0,0.32],[2,1,0.41],[2,2,1.00],[2,3,0.27],[2,4,0.12],
    [3,0,0.88],[3,1,0.91],[3,2,0.27],[3,3,1.00],[3,4,0.07],
    [4,0,0.11],[4,1,0.06],[4,2,0.12],[4,3,0.07],[4,4,1.00]
  ]

  myChart1.setOption({
    title: { text: '字段相关性热力图', textStyle: { color: '#fff' } },
    tooltip: {
      trigger: 'item',
      formatter(p) {
        return `${corrLabels[p.data[0]]} ↔ ${corrLabels[p.data[1]]}<br/>相关系数：${p.data[2].toFixed(2)}`
      }
    },
    xAxis: { data: corrLabels, axisLabel: { color: '#fff' } },
    yAxis: { data: corrLabels, axisLabel: { color: '#fff' } },
    visualMap: { min: -1, max: 1, inRange: { color: ['#023e8a','#4361ee','#f72585','#fff'] }, textStyle: { color: '#fff' } },
    series: [{ type: 'heatmap', data: corrData }]
  })

  // 区域相似性
  const zones = ['曼哈顿','布鲁克林','皇后区','布朗克斯','斯塔滕岛']
  const simData = [
    [0,0,0],[0,1,2],[0,2,3],[0,3,5],[0,4,8],
    [1,0,2],[1,1,0],[1,2,1],[1,3,4],[1,4,7],
    [2,0,3],[2,1,1],[2,2,0],[2,3,3],[2,4,6],
    [3,0,5],[3,1,4],[3,2,3],[3,3,0],[3,4,4],
    [4,0,8],[4,1,7],[4,2,6],[4,3,4],[4,4,0]
  ]

  myChart2.setOption({
    title: { text: '区域相似性热力图', textStyle: { color: '#fff' } },
    tooltip: {
      trigger: 'item',
      formatter(p) {
        return `${zones[p.data[0]]} ↔ ${zones[p.data[1]]}<br/>相似度：${p.data[2]}`
      }
    },
    xAxis: { data: zones, axisLabel: { color: '#fff', rotate: 30 } },
    yAxis: { data: zones, axisLabel: { color: '#fff' } },
    visualMap: { min: 0, max:10, inRange: { color: ['#caf0f8','#0077b6'] }, textStyle: { color: '#fff' } },
    series: [{ type: 'heatmap', data: simData }]
  })

  // K-Means 聚类
  myChart3.setOption({
    title: { text: '区域K-Means聚类', textStyle: { color: '#fff' } },
    tooltip: {
      trigger: 'item',
      formatter(p) {
        return `${p.seriesName}<br/>距离：${p.data[0]}km<br/>车费：$${p.data[1]}`
      }
    },
    legend: { data: ['热门区','普通区','冷门区'], textStyle: { color: '#fff' } },
    xAxis: { name: '平均距离', axisLabel: { color: '#fff' } },
    yAxis: { name: '平均车费', axisLabel: { color: '#fff' } },
    series: [
      { name: '热门区', type: 'scatter', data: [[5.1,23.2],[4.7,21.5]], itemStyle: { color:'#ff4d6d' } },
      { name: '普通区', type: 'scatter', data: [[2.4,11.1],[2.0,9.7]], itemStyle: { color:'#4cc9f0' } },
      { name: '冷门区', type: 'scatter', data: [[1.1,6.4],[0.7,5.1]], itemStyle: { color:'#4ade80' } }
    ]
  })
})
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 20px;
}
.chart-box {
  background: #001233;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid #023e8a;
}
.chart {
  width: 100%;
  height: 380px;
}
</style>