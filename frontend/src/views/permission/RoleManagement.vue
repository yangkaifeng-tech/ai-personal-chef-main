<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  assignRoleButtons,
  assignRoleMenus,
  createRole,
  deleteRole,
  fetchButtons,
  fetchMenus,
  fetchRoles,
  updateRole,
  type RolePayload,
} from '../../api/permission'
import type { ButtonInfo, MenuItem, RoleInfo } from '../../types/api'

const rows = ref<RoleInfo[]>([])
const menus = ref<MenuItem[]>([])
const buttons = ref<ButtonInfo[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const grantVisible = ref(false)
const editingId = ref<string | null>(null)
const grantingRole = ref<RoleInfo | null>(null)
const formRef = ref<FormInstance>()
const selectedMenuIds = ref<string[]>([])
const selectedButtonIds = ref<string[]>([])

const form = reactive<RolePayload>({ name: '', code: '', description: null })
const rules: FormRules<RolePayload> = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const buttonMenuMap = computed(() => {
  const map = new Map<string, string>()
  for (const menu of flattenMenus(menus.value)) {
    map.set(menu.id, menu.name)
  }
  return map
})

function flattenMenus(items: MenuItem[]): MenuItem[] {
  return items.flatMap((item) => [item, ...flattenMenus(item.children ?? [])])
}

async function loadData() {
  loading.value = true
  try {
    const [roleData, menuData, buttonData] = await Promise.all([fetchRoles(), fetchMenus(true), fetchButtons()])
    rows.value = roleData.items
    menus.value = menuData.items
    buttons.value = buttonData.items
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', code: '', description: null })
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: RoleInfo) {
  editingId.value = row.id
  Object.assign(form, { name: row.name, code: row.code, description: row.description })
  dialogVisible.value = true
}

function openGrant(row: RoleInfo) {
  grantingRole.value = row
  selectedMenuIds.value = [...row.menu_ids]
  selectedButtonIds.value = [...row.button_ids]
  grantVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  if (editingId.value) {
    await updateRole(editingId.value, form)
    ElMessage.success('角色已更新')
  } else {
    await createRole(form)
    ElMessage.success('角色已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function submitGrant() {
  if (!grantingRole.value) {
    return
  }
  await assignRoleMenus(grantingRole.value.id, selectedMenuIds.value)
  await assignRoleButtons(grantingRole.value.id, selectedButtonIds.value)
  ElMessage.success('授权已保存')
  grantVisible.value = false
  await loadData()
}

async function remove(row: RoleInfo) {
  await ElMessageBox.confirm(`确认删除角色「${row.name}」？`, '删除确认', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('角色已删除')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="muted">角色控制菜单可见性和页面按钮操作权限。</div>
      <el-button v-permission="'permission:role:create'" :icon="Plus" type="primary" @click="openCreate">新增角色</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border>
      <el-table-column prop="name" label="角色名称" min-width="140" />
      <el-table-column prop="code" label="角色编码" min-width="160" />
      <el-table-column prop="description" label="说明" min-width="220" />
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }: { row: RoleInfo }">
          <el-button v-permission="'permission:role:update'" link type="primary" @click="openGrant(row)">授权</el-button>
          <el-button v-permission="'permission:role:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'permission:role:delete'" link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑角色' : '新增角色'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="grantVisible" title="角色授权" width="760px">
      <el-tabs>
        <el-tab-pane label="菜单权限">
          <el-tree
            ref="menuTreeRef"
            :data="menus"
            node-key="id"
            show-checkbox
            default-expand-all
            :props="{ label: 'name', children: 'children' }"
            v-model:checked-keys="selectedMenuIds"
          />
        </el-tab-pane>
        <el-tab-pane label="按钮权限">
          <el-checkbox-group v-model="selectedButtonIds" class="button-grid">
            <el-checkbox v-for="button in buttons" :key="button.id" :label="button.id" border>
              {{ buttonMenuMap.get(button.menu_id) }} / {{ button.name }} / {{ button.code }}
            </el-checkbox>
          </el-checkbox-group>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="grantVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGrant">保存授权</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.button-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
</style>
