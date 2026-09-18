<script setup>
import { onMounted, ref } from 'vue'
import { delJSON, getJSON, postJSON } from '../api'
import TierLadder from '../components/TierLadder.vue'
import SegmentTable from '../components/SegmentTable.vue'
const accounts = ref([])
const accountId = ref(null)
const kwh = ref(220)
const peak = ref(false)
const result = ref(null)
const summary = ref(null)
const blankForm = () => { kwh.value = null; peak.value = false }
const fetchSummary = async () => {
  const r = await getJSON(`/api/accounts/${accountId.value}/last-success`)
  summary.value = r.summary
  return r.summary
}
const onAccountChange = async () => {
  result.value = null
  summary.value = null
  if (accountId.value == null) return
  const s = await fetchSummary()
  if (s) {
    kwh.value = s.kwh
    peak.value = s.peak
  } else {
    blankForm()
  }
}
const run = async () => {
  result.value = await postJSON('/api/bill', { account_id: accountId.value, kwh: kwh.value, peak: peak.value, persist: true })
  if (accountId.value != null) await fetchSummary()
}
const clearSummary = async () => {
  if (accountId.value == null) return
  await delJSON(`/api/accounts/${accountId.value}/last-success`)
  summary.value = null
  result.value = null
  blankForm()
}
onMounted(async () => { accounts.value = (await getJSON('/api/accounts')).items })
</script>
<template>
  <div class="page work">
    <h1>测算工作台</h1>
    <div class="panel form-row">
      <label>户号
        <select v-model="accountId" @change="onAccountChange">
          <option :value="null">不关联户号</option>
          <option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}（{{ a.meter_no }}）</option>
        </select>
      </label>
      <label>电量(kWh) <input type="number" v-model.number="kwh" min="0" step="1" /></label>
      <label><input type="checkbox" v-model="peak" /> 尖峰系数</label>
      <button @click="run" :disabled="kwh === null || kwh === '' || kwh < 0">计算并入库</button>
    </div>
    <div v-if="summary" class="panel summary-row">
      <span>上次成功：{{ summary.success_at }} · 运行 #{{ summary.run_id }} · 合计 ¥{{ summary.total }}</span>
      <button @click="clearSummary">清除摘要</button>
    </div>
    <div v-if="result" class="panel">
      <p>合计 ¥{{ result.total }} <span class="muted">记录#{{ result.run_id }}</span></p>
      <TierLadder :segments="result.segments" />
      <SegmentTable :rows="result.segments" />
    </div>
  </div>
</template>
<style scoped>
.form-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; }
input[type=number] { width: 6rem; margin-left: 0.35rem; }
select { margin-left: 0.35rem; }
.summary-row { display: flex; gap: 1rem; align-items: center; justify-content: space-between; }
</style>
