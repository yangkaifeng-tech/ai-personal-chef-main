<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChatDotRound,
  DataBoard,
  Key,
  Lock,
  Menu as MenuIcon,
  Operation,
  Setting,
  SwitchButton,
  Guide,
  User,
  Van,
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import type { MenuItem } from '../types/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const iconMap = {
  DataBoard,
  Truck: Guide,
  Van,
  Operation,
  ChatDotRound,
  Lock,
  User,
  Key,
  MenuIcon,
  Setting,
}

type IconName = keyof typeof iconMap

const activeMenu = computed(() => route.path)
const menus = computed(() => authStore.menus)
const displayName = computed(() => authStore.user?.name || authStore.user?.username || '用户')

function resolveIcon(name: string | null) {
  if (name && name in iconMap) {
    return iconMap[name as IconName]
  }
  return MenuIcon
}

function logout() {
  authStore.logout()
  router.replace('/login')
}

function renderableChildren(menu: MenuItem) {
  return menu.children?.filter((item) => item.visible) ?? []
}
</script>

<template>
  <el-container class="admin-shell">
    <el-aside width="232px" class="admin-aside">
      <div class="brand">
        <div class="brand-mark">网</div>
        <div>
          <div class="brand-title">网约车管理系统123</div>
          <div class="brand-subtitle">Ride Ops Console</div>
        </div>
      </div>

      <el-menu :default-active="activeMenu" router class="admin-menu">
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>工作台</span>
        </el-menu-item>

        <template v-for="menu in menus" :key="menu.id">
          <el-sub-menu v-if="renderableChildren(menu).length" :index="menu.path">
            <template #title>
              <el-icon><component :is="resolveIcon(menu.icon)" /></el-icon>
              <span>{{ menu.name }}</span>
            </template>
            <el-menu-item
              v-for="child in renderableChildren(menu)"
              :key="child.id"
              :index="child.path"
            >
              <el-icon><component :is="resolveIcon(child.icon)" /></el-icon>
              <span>{{ child.name }}</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item v-else-if="menu.visible" :index="menu.path">
            <el-icon><component :is="resolveIcon(menu.icon)" /></el-icon>
            <span>{{ menu.name }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div>
          <div class="header-title">运营后台</div>
          <div class="header-subtitle">司机、权限与 AI 管家统一管理</div>
        </div>
        <div class="header-actions">
          <el-tag type="info">{{ displayName }}</el-tag>
          <el-button :icon="SwitchButton" @click="logout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="admin-main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
}

.admin-aside {
  background: #0f172a;
  color: #e2e8f0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 64px;
  padding: 0 18px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.12);
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 700;
}

.brand-title {
  font-size: 15px;
  font-weight: 700;
}

.brand-subtitle {
  margin-top: 2px;
  color: #94a3b8;
  font-size: 12px;
}

.admin-menu {
  border-right: 0;
  background: transparent;
}

.admin-menu :deep(.el-menu-item),
.admin-menu :deep(.el-sub-menu__title) {
  color: #cbd5e1;
}

.admin-menu :deep(.el-menu-item.is-active) {
  background: rgba(37, 99, 235, 0.18);
  color: #fff;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  border-bottom: 1px solid #e2e8f0;
  background: #fff;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
}

.header-subtitle {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-main {
  background: #f8fafc;
  padding: 20px;
}
</style>
