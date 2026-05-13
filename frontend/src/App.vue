<template>
  <div class="app">
    <h1>🚕 NYC 出租车数据可视化（Vue + Python）</h1>
    <div class="charts">
      <!-- 1. 公司订单对比 -->
      <div class="chart" ref="chart1"></div>
      <!-- 2. 24小时趋势 -->
      <div class="chart" ref="chart2"></div>
      <!-- 3. 行政区TOP -->
      <div class="chart" ref="chart3"></div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  setup() {
    const chart1 = ref(null)
    const chart2 = ref(null)
    const chart3 = ref(null)

    onMounted(async () => {
      // 请求后端数据
      const res = await axios.get("http://127.0.0.1:8000/api/taxi-data")
      const data = res.data

      // 图表1：公司对比
      const c1 = echarts.init(chart1.value)
      c1.setOption({
        title: { text: "Green vs Yellow 订单量" },
        xAxis: { data: ["Green", "Yellow"] },
        yAxis: {},
        series: [{ 
          data: [data.company_count.Green, data.company_count.Yellow],
          type: "bar" 
        }]
      })

      // 图表2：24小时趋势
      const c2 = echarts.init(chart2.value)
      c2.setOption({
        title: { text: "24小时出行高峰" },
        xAxis: { data: [...Array(24).keys()] },
        yAxis: {},
        series: [{ data: data.hour_trend, type: "line" }]
      })

      // 图表3：行政区TOP
      const c3 = echarts.init(chart3.value)
      c3.setOption({
        title: { text: "行政区上车量TOP6" },
        xAxis: { data: Object.keys(data.borough_top) },
        yAxis: {},
        series: [{ data: Object.values(data.borough_top), type: "bar" }]
      })
    })

    return { chart1, chart2, chart3 }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.app { padding: 40px; }
h1 { text-align: center; margin-bottom: 30px; }
.charts { display: flex; gap: 20px; flex-wrap: wrap; justify-content: center; }
.chart { width: 400px; height: 350px; border: 1px solid #eee; padding: 10px; }
</style>