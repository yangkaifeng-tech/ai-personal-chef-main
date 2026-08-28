<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import {
  createVehicle,
  deleteVehicle,
  fetchDrivers,
  fetchVehicles,
  updateVehicle,
  type VehiclePayload,
} from '../../api/ride'
import type { DriverInfo, VehicleInfo } from '../../types/api'

const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref<FormInstance>()
const rows = ref<VehicleInfo[]>([])
const drivers = ref<DriverInfo[]>([])
const total = ref(0)

const query = reactive({
  keyword: '',
  status: '',
  driver_id: '',
  page: 1,
  page_size: 20,
})

const form = reactive<VehiclePayload>({
  plate_no: '',
  brand: '',
  model: '',
  color: null,
  status: 'idle',
  seat_count: 5,
  driver_id: null,
  registered_at: null,
})

const rules: FormRules<VehiclePayload> = {
  plate_no: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入车型', trigger: 'blur' }],
}

function resetForm() {
  editingId.value = null
  Object.assign(form, {
    plate_no: '',
    brand: '',
    model: '',
    color: null,
    status: 'idle',
    seat_count: 5,
    driver_id: null,
    registered_at: null,
  })
}

async function loadDrivers() {
  const data = await fetchDrivers({ page: 1, page_size: 100 })
  drivers.value = data.items
}

async function loadData() {
  loading.value = true
  try {
    const data = await fetchVehicles(query)
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

function openEdit(row: VehicleInfo) {
  editingId.value = row.id
  Object.assign(form, {
    plate_no: row.plate_no,
    brand: row.brand,
    model: row.model,
    color: row.color,
    status: row.status,
    seat_count: row.seat_count,
    driver_id: row.driver_id,
    registered_at: row.registered_at,
  })
  dialogVisible.value = true
}

async function submit() {
  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }
  if (editingId.value) {
    await updateVehicle(editingId.value, form)
    ElMessage.success('车辆已更新')
  } else {
    await createVehicle(form)
    ElMessage.success('车辆已新增')
  }
  dialogVisible.value = false
  await loadData()
}

async function remove(row: VehicleInfo) {
  await ElMessageBox.confirm(`确认删除车辆「${row.plate_no}」？`, '删除确认', { type: 'warning' })
  await deleteVehicle(row.id)
  ElMessage.success('车辆已删除')
  await loadData()
}

onMounted(async () => {
  await Promise.all([loadDrivers(), loadData()])
})
</script>

<template>
  <div class="page-card">
    <div class="toolbar">
      <div class="search-row">
        <el-input v-model="query.keyword" placeholder="车牌 / 品牌 / 车型" clearable style="width: 220px" />
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
          <el-option label="空闲" value="idle" />
          <el-option label="运营中" value="running" />
          <el-option label="维修中" value="repair" />
          <el-option label="停用" value="disabled" />
        </el-select>
        <el-select v-model="query.driver_id" placeholder="绑定司机" clearable style="width: 180px">
          <el-option v-for="driver in drivers" :key="driver.id" :label="driver.name" :value="driver.id" />
        </el-select>
        <el-button :icon="Search" type="primary" @click="loadData">查询</el-button>
        <el-button
          :icon="Refresh"
          @click="Object.assign(query, { keyword: '', status: '', driver_id: '', page: 1 }); loadData()"
        >
          重置
        </el-button>
      </div>
      <el-button v-permission="'vehicle:create'" :icon="Plus" type="primary" @click="openCreate">新增车辆</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border>
      <el-table-column prop="plate_no" label="车牌号" min-width="120" />
      <el-table-column prop="brand" label="品牌" min-width="120" />
      <el-table-column prop="model" label="车型" min-width="120" />
      <el-table-column prop="color" label="颜色" width="100" />
      <el-table-column prop="seat_count" label="座位数" width="90" />
      <el-table-column prop="driver_name" label="绑定司机" min-width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }: { row: VehicleInfo }">
          <el-tag :type="row.status === 'idle' ? 'success' : 'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="registered_at" label="注册日期" width="140" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }: { row: VehicleInfo }">
          <el-button v-permission="'vehicle:update'" link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-permission="'vehicle:delete'" link type="danger" @click="remove(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑车辆' : '新增车辆'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="车牌号" prop="plate_no">
          <el-input v-model="form.plate_no" />
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="form.brand" />
        </el-form-item>
        <el-form-item label="车型" prop="model">
          <el-input v-model="form.model" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-input v-model="form.color" />
        </el-form-item>
        <el-form-item label="座位数">
          <el-input-number v-model="form.seat_count" :min="1" :max="9" />
        </el-form-item>
        <el-form-item label="绑定司机">
          <el-select v-model="form.driver_id" clearable style="width: 100%">
            <el-option v-for="driver in drivers" :key="driver.id" :label="driver.name" :value="driver.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="空闲" value="idle" />
            <el-option label="运营中" value="running" />
            <el-option label="维修中" value="repair" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="注册日期">
          <el-date-picker v-model="form.registered_at" value-format="YYYY-MM-DD" type="date" />
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
