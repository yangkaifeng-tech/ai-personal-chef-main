<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123',
})

const rules: FormRules<typeof form> = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  loading.value = true
  try {
    await authStore.login(form)
    ElMessage.success('登录成功')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.replace(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="login-copy">
        <div class="system-tag">Ride Ops Console</div>
        <h1>网约车管理系统</h1>
        <p>统一管理司机、车辆、角色权限，并保留 AI 管家能力。</p>
      </div>

      <el-card class="login-card" shadow="never">
        <template #header>
          <div>
            <div class="card-title">账号登录</div>
            <div class="card-subtitle">默认管理员：admin / admin123</div>
          </div>
        </template>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" :prefix-icon="User" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              :prefix-icon="Lock"
              placeholder="请输入密码"
              show-password
              type="password"
            />
          </el-form-item>
          <el-button type="primary" size="large" class="login-button" :loading="loading" @click="submit">
            登录系统
          </el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background:
    radial-gradient(circle at 18% 20%, rgba(37, 99, 235, 0.22), transparent 28%),
    linear-gradient(135deg, #0f172a 0%, #172554 50%, #f8fafc 50%, #eef2ff 100%);
}

.login-panel {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 56px;
  width: min(960px, calc(100vw - 80px));
  align-items: center;
}

.login-copy {
  color: #fff;
}

.system-tag {
  display: inline-flex;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  color: #bfdbfe;
  font-size: 13px;
}

h1 {
  margin: 22px 0 12px;
  font-size: 42px;
}

p {
  max-width: 440px;
  color: #cbd5e1;
  font-size: 16px;
  line-height: 1.7;
}

.login-card {
  border: 1px solid #dbe4f0;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
}

.card-subtitle {
  margin-top: 6px;
  color: #64748b;
  font-size: 13px;
}

.login-button {
  width: 100%;
  margin-top: 8px;
}
</style>
