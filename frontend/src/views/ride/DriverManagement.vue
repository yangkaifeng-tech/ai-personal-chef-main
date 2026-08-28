<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createDriver, deleteDriver, fetchDrivers, updateDriver, type DriverPayload } from '../../api/ride'
import type { DriverInfo } from '../../types/api'

const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()
const rows = ref<DriverInfo[]>([])
const total = ref(0)

const query = reactive({
  keyword: '',
  status: '',
  page: 1,
  page_size: 20,
})

const form = reactive<DriverPayload>({
  name: '',
  phone: '',
  id_card: null,
  license_no: null,
  status: 'active',
  rating: 5,
  hired_at: null,
})

const rules: FormRules<DriverPayload> = {
  name: [{ required: true, message: '请输入司机姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    name: '',
    phone: '',
    id_card: null,
    license_no: null,
    status: 'active',
    rating: 5,
    hired_at: null,
  })
}

async function loadData() {
  loading.value = true
  try {
    const data = await fetchDrivers(query)
    rows.value = data.items
    total.value = data.total ?? data.items.length
  } finally {
    loading.value = false
  }
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: DriverInfo) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    phone: row.phone,
    id_card: row.id_card,
    license_no: row.license_no,
    status: row.status,
    rating: row.rating,
    hired_at: row.hired_at,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  if (editingId.value) {
    await updateDriver(editingId.value, form)
    ElMessage.success('司机已更新')
  } else {
    await createDriver(form)
    ElMessage.success('司机已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function remove(row: DriverInfo) {
  await ElMessageBox.confirm(`确认删除司机「${row.name}」？`, '删除确认', { type: 'warning' })
  await deleteDriver(row.id)
  ElMessage.success('司机已删除')
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="search-row">
        <el-input v-model="query.keyword" placeholder="姓名 / 手机号" clearable style="width: 220px" />
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
          <el-option label="在职" value="active" />
          <el-option label="停用" value="disabled" />
          <el-option label="离职" value="left" />
        </el-select>
        <el-button :icon="Search" type="primary" @click="loadData">查询</el-button>
        <el-button :icon="Refresh" @click="Object.assign(query, { keyword: '', status: '', page: 1 }); loadData()">重置</el-button>
      </div>
      <el-button v-permission="'driver:create'" :icon="Plus" type="primary" @click="openCreate">新增司机</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border>
      <el-table-column prop="name" label="司机姓名" min-width="120" />
      <el-table-column prop="phone" label="手机号" min-width="140" />
      <el-table-column prop="license_no" label="驾驶证号" min-width="160" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }: { row: DriverInfo }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rating" label="评分" width="90" />
      <el-table-column prop="hired_at" label="入职日期" width="140" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }: { row: DriverInfo }">
          <el-button v-permission="'driver:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'driver:delete'" link type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑司机' : '新增司机'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="司机姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="form.id_card" />
        </el-form-item>
        <el-form-item label="驾驶证号">
          <el-input v-model="form.license_no" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="在职" value="active" />
            <el-option label="停用" value="disabled" />
            <el-option label="离职" value="left" />
          </el-select>
        </el-form-item>
        <el-form-item label="评分">
          <el-input-number v-model="form.rating" :min="0" :max="5" :step="0.1" />
        </el-form-item>
        <el-form-item label="入职日期">
          <el-date-picker v-model="form.hired_at" value-format="YYYY-MM-DD" type="date" />
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
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
