<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { createResource } from "frappe-ui"
import { Calendar, Package, TrendingUp, AlertTriangle, Eye, Filter } from "lucide-vue-next"
import BackButton from "@/components/BackButton.vue"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"

interface ForecastHistory {
  name: string
  run_name: string
  company: string
  model_used: string
  run_status: string
  run_start_time: string
  run_end_time: string
  total_items_forecasted: number
  successful_forecasts: number
  failed_forecasts: number
  avg_confidence_score: number
  forecast_horizon_days: number
  start_date: string
  end_date: string
}

const router = useRouter()
const histories = ref<ForecastHistory[]>([])
const total = ref(0)
const limit = ref(20)
const offset = ref(0)

// Filters
const selectedCompany = ref<string | null>(null)
const selectedModel = ref<string | null>(null)
const selectedStatus = ref<string | null>(null)
const companies = ref<string[]>([])
const models = ref<string[]>(["ARIMA", "Linear Regression", "Prophet"])

// Resource de load histories
const historiesResource = createResource({
  url: "uit_aps.forecast.api.forecast_api.get_forecast_history_list",
  params: {
    limit: limit.value,
    offset: offset.value,
    company: selectedCompany.value,
    model_used: selectedModel.value,
    status: selectedStatus.value,
  },
  auto: false,
  onSuccess(data) {
    histories.value = data.data || []
    total.value = data.total || 0
  },
})

// Resource de load companies
const companiesResource = createResource({
  url: "uit_aps.forecast.api.forecast_api.get_companies",
  auto: false,
  onSuccess(data) {
    companies.value = data || []
  },
})

// Load data
const loadHistories = () => {
  historiesResource.update({
    params: {
      limit: limit.value,
      offset: offset.value,
      company: selectedCompany.value,
      model_used: selectedModel.value,
      status: selectedStatus.value,
    },
  })
  historiesResource.fetch()
}

// Load companies
const loadCompanies = () => {
  companiesResource.fetch()
}

const loading = computed(() => historiesResource.loading)

// View dashboard
const viewDashboard = (historyName: string) => {
  router.push({
    name: "Dashboard",
    query: { history: historyName }
  })
}

// Status badge color
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    Complete: "bg-green-500/20 text-green-600",
    Running: "bg-blue-500/20 text-blue-600",
    Failed: "bg-red-500/20 text-red-600",
    Pending: "bg-gray-500/20 text-gray-600",
  }
  return colors[status] || "bg-gray-500/20 text-gray-600"
}

// Format date
const formatDate = (dateStr: string) => {
  if (!dateStr) return "-"
  return new Date(dateStr).toLocaleString("vi-VN")
}

// Computed stats
const stats = computed(() => {
  const complete = histories.value.filter(h => h.run_status === "Complete").length
  const running = histories.value.filter(h => h.run_status === "Running").length
  const failed = histories.value.filter(h => h.run_status === "Failed").length
  const totalItems = histories.value.reduce((sum, h) => sum + (h.total_items_forecasted || 0), 0)
  
  return [
    {
      title: "Tong so lan chay",
      value: total.value.toString(),
      icon: Calendar,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      title: "Thanh cong",
      value: complete.toString(),
      icon: TrendingUp,
      color: "text-green-500",
      bgColor: "bg-green-500/10",
    },
    {
      title: "That bai",
      value: failed.toString(),
      icon: AlertTriangle,
      color: "text-red-500",
      bgColor: "bg-red-500/10",
    },
    {
      title: "Tong items du doan",
      value: totalItems.toString(),
      icon: Package,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
  ]
})

// Apply filters
const applyFilters = () => {
  offset.value = 0
  // Convert 'all' to null
  const company = selectedCompany.value === 'all' ? null : selectedCompany.value
  const model = selectedModel.value === 'all' ? null : selectedModel.value
  const status = selectedStatus.value === 'all' ? null : selectedStatus.value
  
  historiesResource.update({
    params: {
      limit: limit.value,
      offset: offset.value,
      company: company,
      model_used: model,
      status: status,
    },
  })
  historiesResource.fetch()
}

// Clear filters
const clearFilters = () => {
  selectedCompany.value = null
  selectedModel.value = null
  selectedStatus.value = null
  offset.value = 0
  loadHistories()
}

onMounted(() => {
  loadCompanies()
  loadHistories()
})
</script>

<template>
  <div class="flex-1 overflow-auto p-6 space-y-6">
    <BackButton to="/" label="Quay lai" />

    <div class="space-y-1">
      <h1 class="text-2xl font-bold text-foreground">Lich su Du doan</h1>
      <p class="text-sm text-muted-foreground">
        Quan ly va xem ket qua cac lan chay du doan
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card
        v-for="(stat, index) in stats"
        :key="index"
        class="border border-border"
      >
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground font-medium">{{ stat.title }}</p>
              <p class="text-2xl font-bold text-foreground mt-1">{{ stat.value }}</p>
            </div>
            <div class="p-3 rounded-lg" :class="stat.bgColor">
              <component :is="stat.icon" class="h-6 w-6" :class="stat.color" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card class="border border-border">
      <CardHeader class="pb-3">
        <div class="flex items-center justify-between">
          <CardTitle class="text-base font-semibold flex items-center gap-2">
            <Filter class="h-4 w-4" />
            Bo loc
          </CardTitle>
          <Button variant="ghost" size="sm" @click="clearFilters">
            Xoa bo loc
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="text-sm font-medium mb-2 block">Company</label>
            <Select v-model="selectedCompany">
              <SelectTrigger>
                <SelectValue placeholder="Chon company" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tat ca</SelectItem>
                <SelectItem v-for="company in companies" :key="company" :value="company">
                  {{ company }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label class="text-sm font-medium mb-2 block">Model</label>
            <Select v-model="selectedModel">
              <SelectTrigger>
                <SelectValue placeholder="Chon model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tat ca</SelectItem>
                <SelectItem v-for="model in models" :key="model" :value="model">
                  {{ model }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label class="text-sm font-medium mb-2 block">Trang thai</label>
            <Select v-model="selectedStatus">
              <SelectTrigger>
                <SelectValue placeholder="Chon trang thai" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tat ca</SelectItem>
                <SelectItem value="Complete">Complete</SelectItem>
                <SelectItem value="Running">Running</SelectItem>
                <SelectItem value="Failed">Failed</SelectItem>
                <SelectItem value="Pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex items-end">
            <Button @click="applyFilters" class="w-full">
              Ap dung
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- History Table -->
    <Card class="border border-border">
      <CardHeader class="pb-3">
        <CardTitle class="text-base font-semibold">Danh sach lich su</CardTitle>
      </CardHeader>
      <CardContent class="p-0">
        <div v-if="loading" class="p-8 text-center text-muted-foreground">
          Dang tai...
        </div>
        <div v-else-if="histories.length === 0" class="p-8 text-center text-muted-foreground">
          Khong co du lieu
        </div>
        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead>Ten lan chay</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Trang thai</TableHead>
              <TableHead>Items</TableHead>
              <TableHead>Thanh cong / That bai</TableHead>
              <TableHead>Do tin cay TB</TableHead>
              <TableHead>Thoi gian</TableHead>
              <TableHead>Hanh dong</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
              v-for="history in histories"
              :key="history.name"
            >
              <TableCell class="font-medium">{{ history.run_name }}</TableCell>
              <TableCell>{{ history.company || "-" }}</TableCell>
              <TableCell>
                <Badge variant="outline">{{ history.model_used }}</Badge>
              </TableCell>
              <TableCell>
                <Badge :class="getStatusColor(history.run_status)">
                  {{ history.run_status }}
                </Badge>
              </TableCell>
              <TableCell>{{ history.total_items_forecasted || 0 }}</TableCell>
              <TableCell>
                <span class="text-green-600">{{ history.successful_forecasts || 0 }}</span>
                /
                <span class="text-red-600">{{ history.failed_forecasts || 0 }}</span>
              </TableCell>
              <TableCell>
                {{ history.avg_confidence_score ? history.avg_confidence_score.toFixed(1) + '%' : '-' }}
              </TableCell>
              <TableCell class="text-xs">
                {{ formatDate(history.run_start_time) }}
              </TableCell>
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  @click="viewDashboard(history.name)"
                  :disabled="history.run_status !== 'Complete'"
                >
                  <Eye class="h-4 w-4 mr-1" />
                  Coi ket qua
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>

    <!-- Pagination -->
    <div v-if="total > limit" class="flex items-center justify-between">
      <p class="text-sm text-muted-foreground">
        Hien thi {{ offset + 1 }} - {{ Math.min(offset + limit, total) }} trong tong {{ total }} ket qua
      </p>
      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          :disabled="offset === 0"
          @click="() => { offset = Math.max(0, offset - limit); loadHistories() }"
        >
          Trang truoc
        </Button>
        <Button
          variant="outline"
          size="sm"
          :disabled="offset + limit >= total"
          @click="() => { offset = offset + limit; loadHistories() }"
        >
          Trang sau
        </Button>
      </div>
    </div>
  </div>
</template>

