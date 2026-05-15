<template>
  <div class="timeline-player">
    <button class="play-btn" @click="togglePlay">{{ playing ? '⏸' : '▶' }}</button>
    <input type="range" :min="0" :max="buckets.length - 1" :value="currentIndex" @input="seek(Number($event.target.value))" class="timeline-slider" />
    <span class="time-label">{{ buckets[currentIndex]?.label || '-' }}</span>
    <select v-model="speed" class="speed-select">
      <option :value="1">1x</option>
      <option :value="2">2x</option>
      <option :value="4">4x</option>
    </select>
    <select :value="granularity" @change="$emit('update:granularity', $event.target.value)" class="speed-select">
      <option value="monthly">按月</option>
      <option value="hourly">按小时</option>
      <option value="weekly">按周</option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  buckets: { type: Array, default: () => [] },
  granularity: String,
})
const emit = defineEmits(['update:granularity', 'index-change'])

const playing = ref(false)
const speed = ref(1)
const currentIndex = ref(0)
let timer = null

const togglePlay = () => {
  playing.value = !playing.value
  if (playing.value) startTimer()
  else clearInterval(timer)
}

const startTimer = () => {
  clearInterval(timer)
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % props.buckets.length
    emit('index-change', currentIndex.value)
  }, 1500 / speed.value)
}

const seek = (idx) => { currentIndex.value = idx; emit('index-change', idx) }

watch(speed, () => { if (playing.value) startTimer() })
watch(() => props.buckets, () => { currentIndex.value = 0 })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.timeline-player {
  background: rgba(15,23,42,0.6); backdrop-filter: blur(8px);
  border-radius: 48px; padding: 10px 24px;
  margin-bottom: 24px; display: flex; align-items: center;
  gap: 16px; border: 1px solid rgba(59,130,246,0.2);
}
.play-btn {
  background: #3B82F6; border: none; width: 36px; height: 36px;
  border-radius: 50%; color: white; font-size: 16px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.timeline-slider { flex: 1; accent-color: #3B82F6; }
.time-label { color: #F3F4F6; font-weight: 600; font-size: 14px; min-width: 80px; text-align: center; }
.speed-select {
  background: #1E293B; border: 1px solid #334155;
  padding: 6px 12px; border-radius: 20px; color: #F3F4F6;
  font-size: 13px; outline: none; cursor: pointer;
}
</style>
