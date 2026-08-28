<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createUser, deleteUser, fetchRoles, fetchUsers, updateUser, type UserPayload } from '../../api/permission'
import type { RoleInfo, UserInfo } from '../../types/api'

type UserForm = UserPayload & { password: string }

const rows = ref<UserInfo[]>([])
const roles = ref<RoleInfo[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()
const total = ref(0)

const query = reactive({ keyword: '', status: '', page: 1, page_size: 20 })
const form = reactive<UserForm>({
  username: '',
  password: '',
  name: null,
  status: 'enabled',
  role_ids: [],
})

const rules: FormRules<UserForm> = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '新增用户必须设置密码', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    const [userData, roleData] = await Promise.all([fetchUsers(query), fetchRoles()])
    rows.value = userData.items
    total.value = userData.total ?? userData.items.length
    roles.value = roleData.items
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { username: '', password: '', name: null, status: 'enabled', role_ids: [] })
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: UserInfo) {
  editingId.value = row.id
  Object.assign(form, {
    username: row.username,
    password: '',
    name: row.name,
    status: row.status,
    role_ids: [...row.role_ids],
  })
  dialogVisible.value = true
}

async function submit() {
  if (!editingId.value && !form.password) {
    await formRef.value?.validate()
    return
  }
  const valid = await formRef.value?.validateField(['username'])
  if (!valid) {
    return
  }
  if (editingId.value) {
    const payload: UserPayload = { ...form }
    if (!form.password) {
      delete payload.password
    }
    await updateUser(editingId.value, payload)
    ElMessage.success('人员已更新')
  } else {
    await createUser({ ...form, password: form.password })
    ElMessage.success('人员已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function remove(row: UserInfo) {
  await ElMessageBox.confirm(`确认删除用户「${row.username}」？`, '删除确认', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('人员已删除')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="search-row">
        <el-input v-model="query.keyword" placeholder="用户名 / 姓名" clearable style="width: 220px" />
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
          <el-option label="启用" value="enabled" />
          <el-option label="停用" value="disabled" />
        </el-select>
        <el-button :icon="Search" type="primary" @click="loadData">查询</el-button>
        <el-button :icon="Refresh" @click="Object.assign(query, { keyword: '', status: '', page: 1 }); loadData()">重置</el-button>
      </div>
      <el-button v-permission="'permission:user:create'" :icon="Plus" type="primary" @click="openCreate">新增人员</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border>
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="name" label="姓名" min-width="120" />
      <el-table-column label="角色" min-width="220">
        <template #default="{ row }: { row: UserInfo }">
          <el-tag v-for="roleId in row.role_ids" :key="roleId" class="tag-gap">
            {{ roles.find((role) => role.id === roleId)?.name ?? roleId }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }: { row: UserInfo }">
          <el-button v-permission="'permission:user:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'permission:user:delete'" link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑人员' : '新增人员'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item :label="editingId ? '新密码' : '密码'" :prop="editingId ? undefined : 'password'">
          <el-input v-model="form.password" type="password" show-password placeholder="编辑时留空表示不修改" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="enabled" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple clearable style="width: 100%">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.tag-gap {
  margin-right: 6px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
