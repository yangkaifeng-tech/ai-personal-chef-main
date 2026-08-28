<script setup lang="ts">
import { ChatDotRound, Guide, Key, TrendCharts } from '@element-plus/icons-vue'
</script>

<template>
  <div class="dashboard">
    <div class="overview">
      <el-card shadow="never" class="metric-card">
        <el-icon><Guide /></el-icon>
        <div>
          <div class="metric-value">司机管理</div>
          <div class="muted">维护司机档案、状态与证件信息</div>
        </div>
      </el-card>
      <el-card shadow="never" class="metric-card">
        <el-icon><Key /></el-icon>
        <div>
          <div class="metric-value">权限管理</div>
          <div class="muted">人员、角色、菜单、按钮权限</div>
        </div>
      </el-card>
      <el-card shadow="never" class="metric-card">
        <el-icon><ChatDotRound /></el-icon>
        <div>
          <div class="metric-value">AI 管家</div>
          <div class="muted">保留原私厨管家流式对话能力</div>
        </div>
      </el-card>
    </div>

    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          当前实现范围
        </div>
      </template>
      <el-alert
        title="当前提供司机管理、权限管理和 AI 管家功能。"
        type="info"
        show-icon
        :closable="false"
      />
    </el-card>
  </div>
</template>

<style scoped>
.overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 18px;
}

.metric-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 14px;
}

.metric-card .el-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 22px;
}

.metric-value {
  margin-bottom: 4px;
  font-size: 18px;
  font-weight: 700;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}
</style>
