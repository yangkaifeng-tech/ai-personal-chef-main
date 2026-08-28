<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createMenu, deleteMenu, fetchMenus, updateMenu, type MenuPayload } from '../../api/permission'
import type { MenuItem } from '../../types/api'

const rows = ref<MenuItem[]>([])
const flatMenus = ref<MenuItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<MenuPayload>({
  parent_id: null,
  name: '',
  path: '',
  component: '',
  icon: null,
  sort: 0,
  visible: true,
  permission_code: null,
})

const rules: FormRules<MenuPayload> = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由路径', trigger: 'blur' }],
  component: [{ required: true, message: '请输入组件标识', trigger: 'blur' }],
}

function flatten(items: MenuItem[]): MenuItem[] {
  return items.flatMap((item) => [item, ...flatten(item.children ?? [])])
}

async function loadData() {
  loading.value = true
  try {
    const treeData = await fetchMenus(true)
    rows.value = treeData.items
    flatMenus.value = flatten(treeData.items)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    parent_id: null,
    name: '',
    path: '',
    component: '',
    icon: null,
    sort: 0,
    visible: true,
    permission_code: null,
  })
}

function openCreate(parent?: MenuItem) {
  resetForm()
  if (parent) {
    form.parent_id = parent.id
  }
  dialogVisible.value = true
}

function openEdit(row: MenuItem) {
  editingId.value = row.id
  Object.assign(form, {
    parent_id: row.parent_id,
    name: row.name,
    path: row.path,
    component: row.component,
    icon: row.icon,
    sort: row.sort,
    visible: row.visible,
    permission_code: row.permission_code,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  if (editingId.value) {
    await updateMenu(editingId.value, form)
    ElMessage.success('菜单已更新')
  } else {
    await createMenu(form)
    ElMessage.success('菜单已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function remove(row: MenuItem) {
  await ElMessageBox.confirm(`确认删除菜单「${row.name}」及其子菜单？`, '删除确认', { type: 'warning' })
  await deleteMenu(row.id)
  ElMessage.success('菜单已删除')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="muted">菜单用于控制左侧导航可见性，按钮权限单独维护。</div>
      <el-button v-permission="'permission:menu:create'" :icon="Plus" type="primary" @click="openCreate()">新增菜单</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="rows"
      row-key="id"
      border
      default-expand-all
      :tree-props="{ children: 'children' }"
    >
      <el-table-column prop="name" label="菜单名称" min-width="160" />
      <el-table-column prop="path" label="路由路径" min-width="160" />
      <el-table-column prop="component" label="组件标识" min-width="180" />
      <el-table-column prop="icon" label="图标" width="120" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column prop="visible" label="可见" width="90">
        <template #default="{ row }: { row: MenuItem }">
          <el-tag :type="row.visible ? 'success' : 'info'">{{ row.visible ? '可见' : '隐藏' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }: { row: MenuItem }">
          <el-button v-permission="'permission:menu:create'" link type="primary" @click="openCreate(row)">新增子级</el-button>
          <el-button v-permission="'permission:menu:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'permission:menu:delete'" link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑菜单' : '新增菜单'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-form-item label="上级菜单">
          <el-select v-model="form.parent_id" clearable style="width: 100%">
            <el-option
              v-for="menu in flatMenus.filter((item) => item.id !== editingId)"
              :key="menu.id"
              :label="menu.name"
              :value="menu.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="form.path" placeholder="/drivers" />
        </el-form-item>
        <el-form-item label="组件标识" prop="component">
          <el-input v-model="form.component" placeholder="DriverManagement" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="Truck" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="可见">
          <el-switch v-model="form.visible" />
        </el-form-item>
        <el-form-item label="权限标识">
          <el-input v-model="form.permission_code" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
