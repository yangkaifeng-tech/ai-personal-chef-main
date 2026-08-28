<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createButton, deleteButton, fetchButtons, fetchMenus, updateButton, type ButtonPayload } from '../../api/permission'
import type { ButtonInfo, MenuItem } from '../../types/api'

const rows = ref<ButtonInfo[]>([])
const menus = ref<MenuItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<ButtonPayload>({
  menu_id: '',
  name: '',
  code: '',
  description: null,
})

const rules: FormRules<ButtonPayload> = {
  menu_id: [{ required: true, message: '请选择所属菜单', trigger: 'change' }],
  name: [{ required: true, message: '请输入按钮名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
}

const flatMenus = computed(() => flattenMenus(menus.value))
const menuNameMap = computed(() => {
  const map = new Map<string, string>()
  for (const menu of flatMenus.value) {
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
    const [buttonData, menuData] = await Promise.all([fetchButtons(), fetchMenus(true)])
    rows.value = buttonData.items
    menus.value = menuData.items
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { menu_id: '', name: '', code: '', description: null })
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: ButtonInfo) {
  editingId.value = row.id
  Object.assign(form, {
    menu_id: row.menu_id,
    name: row.name,
    code: row.code,
    description: row.description,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  if (editingId.value) {
    await updateButton(editingId.value, form)
    ElMessage.success('按钮已更新')
  } else {
    await createButton(form)
    ElMessage.success('按钮已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function remove(row: ButtonInfo) {
  await ElMessageBox.confirm(`确认删除按钮权限「${row.code}」？`, '删除确认', { type: 'warning' })
  await deleteButton(row.id)
  ElMessage.success('按钮已删除')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="muted">按钮权限用于控制页面内新增、编辑、删除等操作。</div>
      <el-button v-permission="'permission:button:create'" :icon="Plus" type="primary" @click="openCreate">新增按钮</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border>
      <el-table-column label="所属菜单" min-width="140">
        <template #default="{ row }: { row: ButtonInfo }">
          {{ menuNameMap.get(row.menu_id) ?? row.menu_id }}
        </template>
      </el-table-column>
      <el-table-column prop="name" label="按钮名称" min-width="120" />
      <el-table-column prop="code" label="权限编码" min-width="220" />
      <el-table-column prop="description" label="说明" min-width="220" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }: { row: ButtonInfo }">
          <el-button v-permission="'permission:button:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'permission:button:delete'" link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑按钮' : '新增按钮'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-form-item label="所属菜单" prop="menu_id">
          <el-select v-model="form.menu_id" filterable style="width: 100%">
            <el-option v-for="menu in flatMenus" :key="menu.id" :label="menu.name" :value="menu.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="按钮名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="form.code" placeholder="driver:create" />
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
  </div>
</template>
