<script setup lang="ts">
import type { Component } from "vue"
import type { ApexOptions } from "apexcharts"
import { computed } from "vue"
import {
  Package,
  TrendingUp,
  AlertTriangle,
  Calendar,
  Brain,
  Sparkles,
  Lightbulb,
  Target,
  BarChart3,
  TrendingDown,
} from "lucide-vue-next"
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

interface KPIItem {
  title: string
  value: string
  icon: Component
  color: string
  bgColor: string
}

interface ForecastItem {
  date: string
  qty: number
}

interface GroupAlert {
  name: string
  alerts: number
}

interface TopItem {
  item: string
  qty: number
}

interface ConfidenceItem {
  range: string
  count: number
}

interface ReorderAlertRow {
  item: string
  forecastDate: string
  forecastQty: number
  currentStock: number
  reorderQty: number
  suggestedQty: number
  coverageDays: number
}

const kpiData = {
  totalForecastQty: 10314,
  avgConfidence: 50.0,
  reorderAlerts: 2,
  avgStockCoverage: 45.7,
  forecastRuns: 1,
  periods: 1,
  items: 13,
}

const kpiCards: KPIItem[] = [
  {
    title: "Total Forecast Qty",
    value: kpiData.totalForecastQty.toLocaleString(),
    icon: Package,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    title: "Avg Confidence",
    value: `${kpiData.avgConfidence.toFixed(1)}%`,
    icon: TrendingUp,
    color: "text-green-500",
    bgColor: "bg-green-500/10",
  },
  {
    title: "Reorder Alerts",
    value: kpiData.reorderAlerts.toString(),
    icon: AlertTriangle,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10",
  },
  {
    title: "Avg Stock Coverage (days)",
    value: kpiData.avgStockCoverage.toFixed(1),
    icon: Calendar,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
  },
]

const forecastOverTimeData: ForecastItem[] = [
  { date: "2024-01", qty: 9800 },
  { date: "2024-07", qty: 9900 },
  { date: "2025-01", qty: 10100 },
  { date: "2025-07", qty: 10300 },
  { date: "2026-01", qty: 10500 },
  { date: "2026-07", qty: 10600 },
  { date: "2027-01", qty: 10700 },
  { date: "2027-07", qty: 10750 },
  { date: "2028-01", qty: 10800 },
]

const reorderAlertsByGroup: GroupAlert[] = [
  { name: "Bàn", alerts: 1 },
  { name: "Ghế", alerts: 1 },
  { name: "Kệ sách", alerts: 0 },
  { name: "Tủ", alerts: 0 },
]

const topItemsByForecast: TopItem[] = [
  { item: "TP-GVP-001", qty: 2350 },
  { item: "TP-GAN-001", qty: 1650 },
  { item: "TP-GBT-001", qty: 980 },
  { item: "TP-GN12-001", qty: 850 },
  { item: "TP-BLV-002", qty: 820 },
  { item: "TP-THS-001", qty: 780 },
  { item: "TP-BLV-001", qty: 750 },
  { item: "TP-TQA-001", qty: 620 },
  { item: "TP-GT2T-001", qty: 480 },
  { item: "TP-GN18-001", qty: 420 },
]

const confidenceScoreData: ConfidenceItem[] = [
  { range: "49.5", count: 0 },
  { range: "50.0", count: 13 },
  { range: "50.5", count: 0 },
]

const reorderAlertsTable: ReorderAlertRow[] = [
  {
    item: "TP-GAN-001",
    forecastDate: "2025-11",
    forecastQty: 1630.4,
    currentStock: 60.0,
    reorderQty: 134.93,
    suggestedQty: 282,
    coverageDays: 9.337539,
  },
  {
    item: "TP-BLV-001",
    forecastDate: "2025-11",
    forecastQty: 783.82,
    currentStock: 34.0,
    reorderQty: 76.477,
    suggestedQty: 160,
    coverageDays: 9.336065,
  },
]

const forecastChartOptions = computed<ApexOptions>(() => ({
  chart: {
    toolbar: { show: false },
    foreColor: "hsl(var(--muted-foreground))",
    fontFamily: "var(--font-sans)",
  },
  stroke: { width: 2, curve: "smooth" },
  colors: ["#7c3aed"],
  grid: { borderColor: "hsl(var(--border))", strokeDashArray: 4 },
  xaxis: {
    categories: forecastOverTimeData.map((item) => item.date),
    labels: { rotate: 0 },
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  yaxis: {
    labels: {
      formatter: (val: number) => val.toLocaleString(),
    },
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  tooltip: {
    theme: "dark",
    y: { formatter: (val: number) => `${val.toLocaleString()} Qty` },
  },
}))

const forecastSeries = computed(() => [
  {
    name: "Qty",
    data: forecastOverTimeData.map((item) => item.qty),
  },
])

const reorderChartOptions = computed<ApexOptions>(() => ({
  chart: {
    type: "bar",
    toolbar: { show: false },
    foreColor: "hsl(var(--muted-foreground))",
    fontFamily: "var(--font-sans)",
  },
  grid: { borderColor: "hsl(var(--border))", strokeDashArray: 4 },
  xaxis: {
    categories: reorderAlertsByGroup.map((item) => item.name),
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  yaxis: {
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
    labels: { formatter: (val: number) => `${val}` },
  },
  dataLabels: { enabled: false },
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: "40%",
    },
  },
  colors: ["#22c55e"],
}))

const reorderChartSeries = computed(() => [
  {
    name: "# Alerts",
    data: reorderAlertsByGroup.map((item) => item.alerts),
  },
])

const topItemsChartOptions = computed<ApexOptions>(() => ({
  chart: {
    type: "bar",
    toolbar: { show: false },
    foreColor: "hsl(var(--muted-foreground))",
    fontFamily: "var(--font-sans)",
  },
  plotOptions: {
    bar: {
      horizontal: true,
      borderRadius: 4,
      barHeight: "60%",
    },
  },
  grid: { borderColor: "hsl(var(--border))", strokeDashArray: 4 },
  xaxis: {
    categories: topItemsByForecast.map((item) => item.item),
    labels: {
      formatter: (val: number) => val.toLocaleString(),
    },
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  dataLabels: { enabled: false },
  colors: ["#0ea5e9"],
}))

const topItemsSeries = computed(() => [
  {
    name: "Qty",
    data: topItemsByForecast.map((item) => item.qty),
  },
])

const confidenceChartOptions = computed<ApexOptions>(() => ({
  chart: {
    type: "bar",
    toolbar: { show: false },
    foreColor: "hsl(var(--muted-foreground))",
    fontFamily: "var(--font-sans)",
  },
  grid: { borderColor: "hsl(var(--border))", strokeDashArray: 4 },
  xaxis: {
    categories: confidenceScoreData.map((item) => item.range),
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  yaxis: {
    axisBorder: { color: "hsl(var(--border))" },
    axisTicks: { color: "hsl(var(--border))" },
  },
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: "50%",
    },
  },
  dataLabels: { enabled: false },
  colors: ["#f97316"],
}))

const confidenceChartSeries = computed(() => [
  {
    name: "Count",
    data: confidenceScoreData.map((item) => item.count),
  },
])

const recommendations = [
  {
    title: "Điều chỉnh Model Dự đoán",
    description: "Xem xét sử dụng phương pháp khác hoặc kết hợp với các mô hình dự đoán khác để tăng độ tin cậy.",
    icon: Target,
    badge: "High Priority",
    badgeColor: "bg-violet-500/20 text-violet-600",
    impact: "+15% accuracy",
  },
  {
    title: "Quản lý Slow Moving Items",
    description: "Theo dõi 9 items slow moving để lập kế hoạch nhập hàng phù hợp, tránh tồn kho.",
    icon: TrendingDown,
    badge: "Medium Priority",
    badgeColor: "bg-purple-500/20 text-purple-600",
    impact: "-20% inventory cost",
  },
  {
    title: "Phát triển Fast Moving Items",
    description: "Duy trì và mở rộng 4 items fast moving để gia tăng doanh thu.",
    icon: TrendingUp,
    badge: "Quick Win",
    badgeColor: "bg-pink-500/20 text-pink-600",
    impact: "+12% revenue",
  },
  {
    title: "Phân tích Thị trường Định kỳ",
    description: "Cập nhật dữ liệu thị trường định kỳ để tối ưu kế hoạch nhập hàng và phân phối.",
    icon: BarChart3,
    badge: "Strategic",
    badgeColor: "bg-indigo-500/20 text-indigo-600",
    impact: "Long-term growth",
  },
]
</script>

<template>
  <div class="flex-1 overflow-auto p-6 space-y-6">
    <BackButton to="/" label="Quay lại" />

    <div class="space-y-1">
      <h1 class="text-2xl font-bold text-foreground">APS Forecast Dashboard</h1>
      <p class="text-sm text-muted-foreground">
        Forecast Runs: {{ kpiData.forecastRuns }} | Periods: {{ kpiData.periods }} | Items: {{ kpiData.items }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card
        v-for="(kpi, index) in kpiCards"
        :key="index"
        class="border border-border"
      >
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground font-medium">{{ kpi.title }}</p>
              <p class="text-2xl font-bold text-foreground mt-1">{{ kpi.value }}</p>
            </div>
            <div class="p-3 rounded-lg" :class="kpi.bgColor">
              <component :is="kpi.icon" class="h-6 w-6" :class="kpi.color" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card class="border border-border">
        <CardHeader class="pb-2">
          <CardTitle class="text-base font-semibold">Forecast Quantity theo thời gian (tổng)</CardTitle>
        </CardHeader>
        <CardContent>
          <apexchart type="line" height="260" :options="forecastChartOptions" :series="forecastSeries" />
        </CardContent>
      </Card>

      <Card class="border border-border">
        <CardHeader class="pb-2">
          <CardTitle class="text-base font-semibold">Reorder Alerts theo Item Group (Top)</CardTitle>
        </CardHeader>
        <CardContent>
          <apexchart type="bar" height="260" :options="reorderChartOptions" :series="reorderChartSeries" />
        </CardContent>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card class="border border-border">
        <CardHeader class="pb-2">
          <CardTitle class="text-base font-semibold">Top Items theo Forecast Qty</CardTitle>
        </CardHeader>
        <CardContent>
          <apexchart type="bar" height="320" :options="topItemsChartOptions" :series="topItemsSeries" />
        </CardContent>
      </Card>

      <div class="space-y-6">
        <Card class="border border-border">
          <CardHeader class="pb-2">
            <CardTitle class="text-base font-semibold">Confidence Score</CardTitle>
          </CardHeader>
          <CardContent>
            <apexchart type="bar" height="320" :options="confidenceChartOptions" :series="confidenceChartSeries" />
          </CardContent>
        </Card>

        <Card class="border border-border">
          <CardHeader class="pb-2">
            <CardTitle class="text-base font-semibold">Reorder Alerts (Chi tiết)</CardTitle>
          </CardHeader>
          <CardContent class="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Forecast</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Reorder Qty</TableHead>
                  <TableHead>Suggested</TableHead>
                  <TableHead>Coverage (days)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow
                  v-for="row in reorderAlertsTable"
                  :key="row.item"
                >
                  <TableCell class="font-medium text-foreground">{{ row.item }}</TableCell>
                  <TableCell>{{ row.forecastDate }}</TableCell>
                  <TableCell>{{ row.currentStock }}</TableCell>
                  <TableCell>{{ row.reorderQty }}</TableCell>
                  <TableCell>{{ row.suggestedQty }}</TableCell>
                  <TableCell>{{ row.coverageDays.toFixed(2) }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>

    <Card class="border border-border">
      <CardHeader class="pb-2">
        <CardTitle class="text-base font-semibold">📊 PHÂN TÍCH TỔNG THỂ LẦN CHẠY DỰ BÁO</CardTitle>
      </CardHeader>
      <CardContent class="space-y-4 text-sm text-foreground">
        <div>
          <h4 class="font-semibold text-muted-foreground mb-1">📋 TÓM TẮT TỔNG QUAN:</h4>
          <p class="text-muted-foreground">
            Lần chạy dự báo "Linear Regression - 2025-12-22" đã hoàn thành với tổng số 13 items dự báo, trong đó tất cả đều thành công. Độ tin cậy trung bình của model là 50.0%, cho thấy cần có những phân tích sau để cải thiện kết quả.
          </p>
        </div>
        <div>
          <h4 class="font-semibold text-success mb-1">✅ HIỆU QUẢ MODEL:</h4>
          <p class="text-muted-foreground">
            Model Linear Regression đã thực hiện tốt khi không có item nào thất bại, tuy nhiên độ tin cậy 50.0% cho thấy có khả năng dự đoán chưa cao, cần cân nhắc đến việc thu thập và phân tích dữ liệu để tăng cường độ chính xác.
          </p>
        </div>
        <div>
          <h4 class="font-semibold text-primary mb-1">📈 XU HƯỚNG CHUNG:</h4>
          <p class="text-muted-foreground">
            Tổng nhu cầu dự báo là 10314.1 đơn vị, cho thấy nhu cầu thị trường có xu hướng khá cao. Phân loại movement cho thấy có 9 items slow moving và 4 items fast moving, cho biết rằng cần có kế hoạch nhập hàng phù hợp. Ngoài ra, phân loại trend cho thấy 12 items được xem là stable và 1 item có xu hướng downward.
          </p>
        </div>
        <div>
          <h4 class="font-semibold text-warning mb-1">⚠️ CẢNH BÁO VÀ ƯU TIÊN:</h4>
          <p class="text-muted-foreground">
            Cần chú ý đến 2 items cần đặt hàng, vì điều này có thể ảnh hưởng đến khan hiếm hàng. Các items slow moving cần được quan tâm để không bị tồn lượng tồn kho.
          </p>
        </div>
      </CardContent>
    </Card>

    <Card class="border-0 bg-gradient-to-br from-violet-500/10 via-purple-500/10 to-fuchsia-500/10 relative overflow-hidden">
      <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-500/20 to-transparent rounded-full blur-2xl" />
      <div class="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-fuchsia-500/20 to-transparent rounded-full blur-2xl" />
      <CardHeader class="pb-3 relative">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg shadow-violet-500/25">
            <Brain class="h-5 w-5 text-white" />
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <CardTitle class="text-lg font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                AI KHUYẾN NGHỊ CHIẾN LƯỢC
              </CardTitle>
              <Sparkles class="h-4 w-4 text-violet-500 animate-pulse" />
            </div>
            <p class="text-xs text-muted-foreground mt-0.5">Powered by Machine Learning • Confidence: 68%</p>
          </div>
        </div>
      </CardHeader>
      <CardContent class="space-y-4 relative">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(rec, index) in recommendations"
            :key="index"
            class="group p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-border/40 hover:border-border transition-all duration-300 hover:shadow-lg"
          >
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-lg bg-muted/40 group-hover:bg-muted/60 transition-colors">
                <component :is="rec.icon" class="h-4 w-4 text-foreground" />
              </div>
              <div class="flex-1">
                <h5 class="font-semibold text-sm text-foreground mb-1">{{ rec.title }}</h5>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  {{ rec.description }}
                </p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="text-[10px] px-2 py-0.5 rounded-full font-medium" :class="rec.badgeColor">
                    {{ rec.badge }}
                  </span>
                  <span class="text-[10px] text-muted-foreground">{{ rec.impact }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-border/50">
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <Lightbulb class="h-3.5 w-3.5 text-amber-500" />
            <span>AI phân tích dựa trên dữ liệu 13 items và 1 forecast run</span>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="ghost" size="sm" class="text-xs h-8 text-muted-foreground hover:text-foreground">
              Bỏ qua
            </Button>
            <Button size="sm" class="text-xs h-8 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white shadow-lg shadow-violet-500/25">
              Áp dụng tất cả
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
