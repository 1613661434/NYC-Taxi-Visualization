<template>
  <div class="header">
    <div class="title-box">
      <h1>纽约出租车数据驾驶舱</h1>
      <p>2018年 {{ startMonth }}-{{ endMonth }}月 · NYC TLC开放数据 · 黄色出租车 vs 绿色出租车</p>
    </div>
    <div class="date-box">
      <div class="date">{{ currentDate }}</div>
      <div class="time">{{ currentTime }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({ startMonth: Number, endMonth: Number })

const currentDate = ref('')
const currentTime = ref('')
let timer = null

const updateDateTime = () => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

onMounted(() => { updateDateTime(); timer = setInterval(updateDateTime, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
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
  color: transparent; letter-spacing: -0.5px;
}
.title-box p { color: #6B7280; font-size: 13px; margin-top: 6px; }
.date-box {
  background: rgba(255,255,255,0.05);
  padding: 8px 20px;
  border-radius: 40px;
  backdrop-filter: blur(4px);
  text-align: right;
}
.date { font-size: 14px; color: #9CA3AF; }
.time { font-size: 20px; font-weight: 600; color: #F3F4F6; }
</style>
