import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../layout/AdminLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/dashboard/DashboardView.vue') },
      { path: 'ride/drivers', name: 'drivers', component: () => import('../views/ride/DriverManagement.vue') },
      { path: 'ai/chef', name: 'ai-chef', component: () => import('../views/ai/ChefHousekeeper.vue') },
      { path: 'permissions/users', name: 'permission-users', component: () => import('../views/permission/UserManagement.vue') },
      { path: 'permissions/roles', name: 'permission-roles', component: () => import('../views/permission/RoleManagement.vue') },
      { path: 'permissions/menus', name: 'permission-menus', component: () => import('../views/permission/MenuManagement.vue') },
      { path: 'permissions/buttons', name: 'permission-buttons', component: () => import('../views/permission/ButtonManagement.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (to.meta.public) {
    return true
  }
  if (!authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (!authStore.user) {
    await authStore.refresh()
  }
  return true
})
