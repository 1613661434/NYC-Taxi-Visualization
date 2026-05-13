# NYC-Taxi-Visualization

NYC 出租车数据可视化分析项目，基于 **Python FastAPI 后端 + Vue3 前端** 实现前后端分离，包含**完整版数据清洗**+**交互式可视化图表**，小白可一键部署运行。

## 技术栈

- **后端**：Python 3.9+、FastAPI、Uvicorn、Pandas

- **前端**：Vue3、Vite4、ECharts、Axios

- **数据**：Parquet 原始数据、CSV 区域映射表

## 项目结构

```shell
NYC-Taxi-Visualization/       
├── data/                     # 原始数据目录
│   ├── green/                # Green 出租车 parquet 数据
│   ├── yellow/               # Yellow 出租车 parquet 数据
│   └── taxi_zone_lookup.csv  # 区域映射表
├── backend/         		  # Python FastAPI 后端服务
├── frontend/        		  # Vue3 前端可视化项目
└── README.md                 # 项目说明文档
```

## 环境准备

1. 安装 **Python 3.9+**

2. 安装 **Node.js 18.x**（兼容项目前端，一键安装：[https://nodejs.org/](https://nodejs.org/)）

---

## 一、激活 Python 虚拟环境（如果是虚拟环境）

```bash
..venv\Scripts\activate
```

---

## 二、安装项目依赖

### 1. 后端依赖（backend 目录）

```bash
cd backend
pip install fastapi uvicorn pandas pyarrow
```

### 2. 前端依赖（frontend 目录）

```bash
cd frontend
npm install
```

---

## 三、本地启动项目（开发模式）

需要**打开两个独立终端**，同时启动前后端服务

### 终端 1：启动 Python 后端

```bash
cd backend
uvicorn main:app --reload
```

✅ 后端启动成功：`http://127.0.0.1:8000`

### 终端 2：启动 Vue 前端

```bash
cd frontend
npm run dev
```

✅ 前端启动成功：`http://localhost:5173`

---

## 四、项目部署（本地部署）

### 部署前提

已完成：前后端依赖安装

### 1. 后端部署（稳定运行）

关闭热重载，开启稳定服务：

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 前端部署（打包 + 本地预览）

```bash
cd frontend
# 第一步：打包前端项目（生成静态文件）
npm run build
# 第二步：本地部署预览
npm run preview
```

### 3. 部署完成，访问项目

- 前端可视化页面：`http://localhost:5173`

- 后端数据接口：`http://127.0.0.1:8000`

### 4. 关闭项目

前后端终端分别按 `Ctrl + C`，即可停止服务

---

## 五、核心功能

1. **完整版数据清洗**（无效数据 / 异常值 / 重复数据过滤）

2. Green \&amp; Yellow 出租车订单量对比

3. 24 小时出行高峰趋势分析

4. 纽约行政区上车量 TOP6 统计

5. 交互式 ECharts 可视化图表

---

## 六、数据清洗规则

1. 剔除行程距离≤0、总费用≤0 的无效行程

2. 过滤非 2018 年的异常时间数据

3. 删除重复行程记录

4. 关联区域表，剔除缺失行政区的空值数据

5. 标准化时间格式，提取小时维度用于分析

---

## 七、注意事项

1. 必须**同时开启前后端终端**，项目才能正常运行

2. 等待后端启动成功后，再打开前端页面

3. 数据已做采样处理，避免电脑内存溢出

4. 所有命令可直接复制粘贴，无需修改