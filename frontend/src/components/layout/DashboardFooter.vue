<template>
  <div class="footer">
    <div class="footer-line"></div>
    <div class="footer-text">
      <span>数据来源：NYC Taxi & Limousine Commission (TLC) 2018年 Trip Record Data</span>
      <span>清洗说明：剔除距离≤0、费用≤0、时长异常、乘客数>6、区域缺失等记录</span>
      <span>可视化设计：数据可视化期末大作业</span>
    </div>
  </div>
</template>

<style scoped>
.footer { margin-top: 32px; }
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
</style>
