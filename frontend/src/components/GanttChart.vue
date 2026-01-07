<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { createResource } from "frappe-ui"
import {
  ChevronLeft,
  ChevronRight,
  Calendar,
  Filter,
  Download,
  Cpu,
  Clock,
  AlertTriangle,
  TrendingUp,
  CheckCircle,
  Zap,
  BarChart3,
  Activity,
  Factory,
  Wrench,
  Settings,
  CircleDot,
  Brain,
  Sparkles,
  Lightbulb,
  Target,
  TrendingDown,
  X,
} from "lucide-vue-next"
import BackButton from "@/components/BackButton.vue"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card"
import { Progress } from "@/components/ui/progress"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

type RiskStatus = "ontime" | "atrisk" | "late"
type ViewMode = "quarterDay" | "halfDay" | "day" | "week" | "month" | "year"

interface Job {
  id: string
  jobCode: string
  operation: string
  machine: string
  startDay: number
  startHour: number
  durationHours: number
  status: RiskStatus
  progress: number
  priority: "low" | "medium" | "high"
  dueDate: number
  startTime?: string
  endTime?: string
  jobCard?: string
}

interface Workstation {
  id: string
  name: string
  status: string
  utilization: number
}

interface PlantFloor {
  floor: string
  description: string
  workstations: Workstation[]
}

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const plantFloors = ref<PlantFloor[]>([])
const schedulingRunInfo = ref<any>(null)
const productionPlans = ref<Array<{ label: string; value: string }>>([])
const selectedProductionPlan = ref<string>("all")

const HOURS_PER_DAY = 24
const WORK_HOURS_START = 8
const WORK_HOURS_END = 20
const HOURS_IN_SHIFT = WORK_HOURS_END - WORK_HOURS_START

const statusColors: Record<RiskStatus, string> = {
  ontime: "bg-[#22c55e] text-white",
  atrisk: "bg-[#facc15] text-foreground",
  late: "bg-[#ef4444] text-white",
}

const statusLabels = {
  ontime: { label: "On-time", color: "text-[#22c55e]" },
  atrisk: { label: "At Risk", color: "text-[#d97706]" },
  late: { label: "Late", color: "text-[#ef4444]" },
}

const priorityColors = {
  low: "bg-muted text-muted-foreground",
  medium: "bg-warning/20 text-warning",
  high: "bg-destructive/20 text-destructive",
}

interface KPIData {
  makespan: number
  lateJobs: number
  avgUtilization: number
  scheduleStability: number
}

interface AIRecommendation {
  event: string
  action: string
  impact: {
    tardiness: string
    utilization: string
  }
  confidence: number
  applied: boolean
}

const jobs = ref<Job[]>([])
const draggedJob = ref<string | null>(null)
const dragStartX = ref(0)
const dragStartDay = ref(0)
const dragStartHour = ref(0)
const viewMode = ref<ViewMode>("month")
const aiApplied = ref(false)
const chartRef = ref<HTMLDivElement | null>(null)

const viewModes: { key: ViewMode; label: string }[] = [
  { key: "quarterDay", label: "Quarter Day" },
  { key: "halfDay", label: "Half Day" },
  { key: "day", label: "Day" },
  { key: "week", label: "Week" },
  { key: "month", label: "Month" },
  { key: "year", label: "Year" },
]

const kpiData = ref<KPIData>({
  makespan: 0,
  lateJobs: 0,
  avgUtilization: 0,
  scheduleStability: 0,
})

// Resource de load production plans
const productionPlansResource = createResource({
  url: "uit_aps.scheduling.api.gantt_api.get_production_plans",
  auto: true,
  onSuccess(data: string[]) {
    productionPlans.value = data.map((pp: string) => ({ label: pp, value: pp }))
    productionPlans.value.unshift({ label: "All Production Plans", value: "all" })
    
    // Set selected production plan from route
    if (route.query.production_plan) {
      selectedProductionPlan.value = route.query.production_plan as string
    }
  },
  onError(error: any) {
    console.error("Error loading production plans:", error)
  }
})

// Resource de load gantt data
const ganttResource = createResource({
  url: "uit_aps.scheduling.api.gantt_api.get_job_cards_for_gantt",
  params: {
    scheduling_run: route.query.scheduling_run as string || null,
    production_plan: route.query.production_plan as string || null
  },
  auto: false,
  onSuccess(data: any) {
    console.log("Gantt data loaded:", data)
    
    // Convert jobs tu API sang format gantt
    const convertedJobs = data.jobs.map((job: any) => convertJobToGanttFormat(job))
    jobs.value = convertedJobs
    
    // Update KPI
    kpiData.value = data.kpi
    
    // Update workstations
    plantFloors.value = data.workstations
    
    // Update scheduling run info
    schedulingRunInfo.value = data.schedulingRun
  },
  onError(error: any) {
    console.error("Error loading gantt data:", error)
  }
})

const convertJobToGanttFormat = (apiJob: any): Job => {
  // Parse start time
  const startTime = new Date(apiJob.startTime)
  const startDiff = startTime.getTime() - baseStartDate.value.getTime()
  const startDay = Math.floor(startDiff / (24 * 60 * 60 * 1000))
  const startHour = startTime.getHours()
  
  // Calculate due date (mock)
  const dueDate = startDay + Math.ceil(apiJob.durationHours / 24) + 2
  
  return {
    id: apiJob.id,
    jobCode: apiJob.jobCode,
    operation: apiJob.operation,
    machine: apiJob.machine,
    startDay: Math.max(0, startDay),
    startHour: startHour,
    durationHours: apiJob.durationHours,
    status: apiJob.status as RiskStatus,
    progress: apiJob.progress,
    priority: apiJob.priority as "low" | "medium" | "high",
    dueDate: dueDate,
    startTime: apiJob.startTime,
    endTime: apiJob.endTime,
    jobCard: apiJob.jobCard
  }
}

const loadGanttData = () => {
  ganttResource.update({
    params: {
      scheduling_run: route.query.scheduling_run as string || null,
      production_plan: route.query.production_plan as string || null
    }
  })
  ganttResource.fetch()
}

const clearProductionPlanFilter = () => {
  selectedProductionPlan.value = "all"
}

// Watch selectedProductionPlan and update router + reload data
watch(selectedProductionPlan, (newValue) => {
  // Update router query
  const query: any = { ...route.query }
  
  if (newValue === "all") {
    delete query.production_plan
  } else {
    query.production_plan = newValue
  }
  
  router.push({ query })
  
  // Reload data
  loadGanttData()
})

const aiRecommendation: AIRecommendation = {
  event: "Rush order detected",
  action: "Swap OP-20 ↔ OP-30",
  impact: {
    tardiness: "↓ 15%",
    utilization: "↑ 8%",
  },
  confidence: 68,
  applied: false,
}

const viewConfig = computed(() => {
  switch (viewMode.value) {
    case "quarterDay":
      return { daysToShow: 7, dayWidth: 240, showHours: true, hourWidth: 20 }
    case "halfDay":
      return { daysToShow: 14, dayWidth: 120, showHours: true, hourWidth: 10 }
    case "day":
      return { daysToShow: 14, dayWidth: 80, showHours: false, hourWidth: 0 }
    case "week":
      return { daysToShow: 28, dayWidth: 40, showHours: false, hourWidth: 0 }
    case "month":
      return { daysToShow: 30, dayWidth: 32, showHours: false, hourWidth: 0 }
    case "year":
      return { daysToShow: 365, dayWidth: 8, showHours: false, hourWidth: 0 }
    default:
      return { daysToShow: 30, dayWidth: 32, showHours: false, hourWidth: 0 }
  }
})

const daysToShow = computed(() => viewConfig.value.daysToShow)
const hourWidth = computed(() => viewConfig.value.hourWidth)
const dayWidth = computed(() =>
  viewConfig.value.showHours ? viewConfig.value.hourWidth * HOURS_IN_SHIFT : viewConfig.value.dayWidth,
)
const showHours = computed(() => viewConfig.value.showHours)

// Tinh baseStartDate la computed de luon cap nhat theo ngay hien tai
const baseStartDate = computed(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()
  const day = today.getDate()

  // Tao date moi tu year/month/day de tranh loi timezone
  const todayClean = new Date(year, month, day)

  // Lui 1 ngay de lam ngay bat dau
  const start = new Date(year, month, day - 1)

  return start
})

const days = computed(() => {
  const start = baseStartDate.value
  return Array.from({ length: daysToShow.value }, (_, i) => {
    // Tao date object moi cho moi ngay de tranh mutation
    const date = new Date(start.getTime())
    date.setDate(date.getDate() + i)
    return date
  })
})

const workHours = Array.from({ length: HOURS_IN_SHIFT }, (_, i) => WORK_HOURS_START + i)

const todayIndex = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayTime = today.getTime()

  // Tim index cua ngay hien tai trong days array
  for (let i = 0; i < days.value.length; i++) {
    const day = new Date(days.value[i])
    day.setHours(0, 0, 0, 0)
    if (day.getTime() === todayTime) {
      return i
    }
  }

  return -1
})

const todayHourOffset = computed(() => {
  const now = new Date()
  const hoursOffset = (now.getHours() + now.getMinutes() / 60) - WORK_HOURS_START
  return Math.max(0, Math.min(hoursOffset, HOURS_IN_SHIFT))
})

const handleApplyAI = () => {
  if (aiApplied.value) return

  kpiData.value = {
    makespan: 10,
    lateJobs: 1,
    avgUtilization: 86,
    scheduleStability: 92,
  }

  jobs.value = jobs.value.map((job) => {
    if (job.id === "4" || job.id === "8") {
      return { ...job, status: "atrisk" as RiskStatus }
    }
    return job
  })

  aiApplied.value = true
}

const handleIgnoreAI = () => {
  aiApplied.value = false
  // Reload original data
  loadGanttData()
}

onMounted(() => {
  loadGanttData()
})

const handleMouseDown = (event: MouseEvent, jobId: string, startDay: number, startHour: number) => {
  event.preventDefault()
  draggedJob.value = jobId
  dragStartX.value = event.clientX
  dragStartDay.value = startDay
  dragStartHour.value = startHour
}

const handleMouseMove = (event: MouseEvent) => {
  if (!draggedJob.value) return

  const deltaX = event.clientX - dragStartX.value

  if (showHours.value && hourWidth.value) {
    const hoursDelta = Math.round(deltaX / hourWidth.value)
    const totalStartHours = dragStartDay.value * HOURS_IN_SHIFT + (dragStartHour.value - WORK_HOURS_START)
    const newTotalHours = Math.max(0, totalStartHours + hoursDelta)
    const newStartDay = Math.floor(newTotalHours / HOURS_IN_SHIFT)
    const newStartHour = WORK_HOURS_START + (newTotalHours % HOURS_IN_SHIFT)

    jobs.value = jobs.value.map((job) =>
      job.id === draggedJob.value
        ? { ...job, startDay: Math.min(newStartDay, daysToShow.value - 1), startHour: newStartHour }
        : job,
    )
  } else if (!showHours.value && dayWidth.value) {
    const daysDelta = Math.round(deltaX / dayWidth.value)
    const newStartDay = Math.max(0, Math.min(daysToShow.value - 1, dragStartDay.value + daysDelta))

    jobs.value = jobs.value.map((job) =>
      job.id === draggedJob.value
        ? { ...job, startDay: newStartDay }
        : job,
    )
  }
}

const handleMouseUp = () => {
  draggedJob.value = null
}

const formatDate = (date: Date) => date.toLocaleDateString("vi-VN", { day: "numeric" })
const formatMonth = (date: Date) => date.toLocaleDateString("vi-VN", { month: "short" })
const getDayName = (date: Date) => date.toLocaleDateString("vi-VN", { weekday: "short" })
const isWeekend = (date: Date) => {
  const day = date.getDay()
  return day === 0 || day === 6
}
const formatHour = (hour: number) => `${hour.toString().padStart(2, "0")}:00`

const getJobPosition = (job: Job) => {
  if (showHours.value) {
    const dayOffset = job.startDay * dayWidth.value
    const hourOffset = (job.startHour - WORK_HOURS_START) * hourWidth.value
    return dayOffset + hourOffset
  }
  return job.startDay * dayWidth.value
}

const getJobWidth = (job: Job) => {
  if (showHours.value && hourWidth.value) {
    return Math.max(job.durationHours * hourWidth.value, hourWidth.value * 2)
  }
  return Math.max((job.durationHours / 8) * dayWidth.value - 8, 20)
}

const getJobStartDate = (job: Job) => {
  const jobStartDate = new Date(baseStartDate.value)
  jobStartDate.setDate(jobStartDate.getDate() + job.startDay)
  return jobStartDate
}

const formatFullDate = (date: Date, hour: number) =>
  `${date.toLocaleDateString("vi-VN", { weekday: "short", day: "numeric", month: "short" })} lúc ${hour
    .toString()
    .padStart(2, "0")}:00`

const priorityLabels = {
  low: { label: "Thấp", color: "text-muted-foreground" },
  medium: { label: "Trung bình", color: "text-warning" },
  high: { label: "Cao", color: "text-destructive" },
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="px-6 py-3 border-b border-border bg-card">
      <div class="flex items-center justify-between">
        <BackButton to="/" label="Quay lai" />
        <div class="flex items-center gap-4 text-sm text-muted-foreground">
          <div v-if="schedulingRunInfo">
            Scheduling Run: <span class="font-medium text-foreground">{{ schedulingRunInfo.name }}</span>
          </div>
          <div v-if="route.query.production_plan">
            Production Plan: <span class="font-medium text-foreground">{{ route.query.production_plan }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="px-6 py-3 border-b border-border bg-card">
      <div class="grid grid-cols-4 gap-4">
        <Card class="bg-white border-border">
          <CardContent class="p-3 flex items-center gap-3">
            <div class="p-2 rounded-lg bg-blue-100">
              <BarChart3 class="h-[22px] w-[22px] text-blue-600" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Makespan</p>
              <p class="text-xl font-bold text-foreground">{{ kpiData.makespan }} days</p>
            </div>
          </CardContent>
        </Card>

        <Card class="bg-white border-border">
          <CardContent class="p-3 flex items-center gap-3">
            <div class="p-2 rounded-lg bg-destructive/10">
              <AlertTriangle class="h-[22px] w-[22px] text-destructive" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Late Jobs</p>
              <p class="text-xl font-bold text-foreground">{{ kpiData.lateJobs }}</p>
            </div>
          </CardContent>
        </Card>

        <Card class="bg-white border-border">
          <CardContent class="p-3 flex items-center gap-3">
            <div class="p-2 rounded-lg bg-green-100">
              <Activity class="h-[22px] w-[22px] text-green-600" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Avg Utilization</p>
              <p class="text-xl font-bold text-foreground">{{ kpiData.avgUtilization }}%</p>
            </div>
          </CardContent>
        </Card>

        <Card class="bg-white border-border">
          <CardContent class="p-3 flex items-center gap-3">
            <div class="p-2 rounded-lg bg-sky-100">
              <CheckCircle class="h-[22px] w-[22px] text-sky-600" />
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Schedule Stability</p>
              <p class="text-xl font-bold text-foreground">{{ kpiData.scheduleStability }}%</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <div class="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
      <div class="flex items-center gap-4">
        <h2 class="text-lg font-semibold text-foreground">
          {{ schedulingRunInfo ? 'Scheduled Production' : 'Production Schedule' }}
        </h2>
        <Badge variant="secondary" class="font-normal">
          {{ jobs.length }} Jobs
        </Badge>
        <Badge v-if="ganttResource.loading" variant="outline" class="animate-pulse">
          Loading...
        </Badge>
      </div>

      <div class="flex items-center gap-2">
        <div class="flex items-center gap-2 mr-2">
          <Select v-model="selectedProductionPlan">
            <SelectTrigger class="w-[240px] h-9">
              <Filter class="h-4 w-4 mr-2" />
              <SelectValue placeholder="Chọn Production Plan" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="plan in productionPlans" :key="plan.value" :value="plan.value">
                {{ plan.label }}
              </SelectItem>
            </SelectContent>
          </Select>
          <Button 
            v-if="selectedProductionPlan !== 'all'" 
            variant="ghost" 
            size="icon" 
            class="h-9 w-9"
            @click="clearProductionPlanFilter"
          >
            <X class="h-4 w-4" />
          </Button>
        </div>

        <div class="flex items-center gap-1 bg-muted rounded-lg p-1">
          <Button v-for="mode in viewModes" :key="mode.key" :variant="viewMode === mode.key ? 'default' : 'ghost'"
            size="sm" class="h-7 px-2 text-xs" @click="viewMode = mode.key">
            {{ mode.label }}
          </Button>
        </div>

        <Button variant="outline" size="sm" class="gap-2">
          <Download class="h-4 w-4" />
          Xuất
        </Button>
        <div class="flex items-center gap-1 ml-2">
          <Button variant="ghost" size="icon" class="h-8 w-8">
            <ChevronLeft class="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" class="gap-2">
            <Calendar class="h-4 w-4" />
            Hôm nay
          </Button>
          <Button variant="ghost" size="icon" class="h-8 w-8">
            <ChevronRight class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div class="flex flex-1 overflow-hidden" @mousemove="handleMouseMove" @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp">
        <div class="w-72 flex-shrink-0 border-r border-border bg-card">
          <div :class="cn('border-b border-border px-4 flex items-center', showHours ? 'h-20' : 'h-16')">
            <span class="text-sm font-medium text-muted-foreground">Job / Operation / Machine</span>
          </div>

          <div class="overflow-y-auto scrollbar-thin"
            :style="{ height: showHours ? 'calc(100% - 80px)' : 'calc(100% - 64px)' }">
            <div v-for="(job, index) in jobs" :key="job.id"
              class="h-14 px-4 flex items-center gap-3 border-b border-border hover:bg-muted/50 transition-colors animate-fade-in"
              :style="{ animationDelay: `${index * 50}ms` }">
              <div :class="cn('w-2 h-2 rounded-full flex-shrink-0', statusColors[job.status])" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-foreground truncate">
                  Job {{ job.jobCode }} / {{ job.operation }}
                </p>
                <p class="text-xs text-muted-foreground">Machine {{ job.machine }}</p>
              </div>
              <Badge variant="secondary"
                :class="cn('text-[10px] px-1.5 py-0 flex-shrink-0', priorityColors[job.priority])">
                {{ job.priority === 'high' ? 'Cao' : job.priority === 'medium' ? 'TB' : 'Thấp' }}
              </Badge>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-x-auto scrollbar-thin" ref="chartRef">
          <div :style="{ minWidth: `${daysToShow * dayWidth}px` }">
            <div v-if="showHours" class="border-b border-border sticky top-0 bg-card z-10">
              <div class="flex h-10 border-b border-border">
                <div v-for="(date, i) in days" :key="`day-${i}`" :class="cn(
                  'flex-shrink-0 flex items-center justify-center border-r border-border font-medium',
                  isWeekend(date) && 'bg-gantt-weekend',
                  i === todayIndex && 'bg-primary/10',
                )" :style="{ width: `${dayWidth}px` }">
                  <span :class="cn('text-sm', i === todayIndex ? 'text-primary' : 'text-foreground')">
                    {{ getDayName(date) }} {{ formatDate(date) }} {{ formatMonth(date) }}
                  </span>
                </div>
              </div>

              <div class="flex h-10">
                <div v-for="(date, dayIndex) in days" :key="`hours-${dayIndex}`"
                  :class="cn('flex-shrink-0 flex border-r border-border', isWeekend(date) && 'bg-gantt-weekend')"
                  :style="{ width: `${dayWidth}px` }">
                  <div v-for="(hour, hourIndex) in workHours" :key="`hour-${dayIndex}-${hour}`" :class="cn(
                    'flex items-center justify-center border-r border-border/50 text-[10px] text-muted-foreground',
                    dayIndex === todayIndex && 'bg-primary/5',
                  )" :style="{ width: `${hourWidth}px` }">
                    <span v-if="hourIndex % 2 === 0">{{ formatHour(hour) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="viewMode === 'month'" class="h-12 border-b border-border flex sticky top-0 bg-card z-10">
              <div v-for="(date, i) in days" :key="i" :class="cn(
                'flex-shrink-0 flex flex-col items-center justify-center border-r border-border',
                isWeekend(date) && 'bg-gantt-weekend',
                i === todayIndex && 'bg-primary/10',
              )" :style="{ width: `${dayWidth}px` }">
                <span
                  :class="cn('text-[9px] font-medium uppercase', i === todayIndex ? 'text-primary' : 'text-muted-foreground')">
                  {{ getDayName(date).charAt(0) }}
                </span>
                <span :class="cn('text-xs font-semibold', i === todayIndex ? 'text-primary' : 'text-foreground')">
                  {{ formatDate(date) }}
                </span>
              </div>
            </div>
            <div v-else class="h-16 border-b border-border flex sticky top-0 bg-card z-10">
              <div v-for="(date, i) in days" :key="i" :class="cn(
                'flex-shrink-0 flex flex-col items-center justify-center border-r border-border',
                isWeekend(date) && 'bg-gantt-weekend',
                i === todayIndex && 'bg-primary/10',
              )" :style="{ width: `${dayWidth}px` }">
                <span
                  :class="cn('text-[10px] font-medium uppercase', i === todayIndex ? 'text-primary' : 'text-muted-foreground')">
                  {{ getDayName(date) }}
                </span>
                <span :class="cn('text-sm font-semibold', i === todayIndex ? 'text-primary' : 'text-foreground')">
                  {{ formatDate(date) }}
                </span>
                <span class="text-[10px] text-muted-foreground">
                  {{ formatMonth(date) }}
                </span>
              </div>
            </div>

            <div class="relative">
              <div class="absolute inset-0 flex pointer-events-none">
                <template v-if="showHours">
                  <div v-for="(date, dayIndex) in days" :key="`grid-day-${dayIndex}`"
                    :class="cn('flex-shrink-0 flex', isWeekend(date) && 'bg-gantt-weekend/50')"
                    :style="{ width: `${dayWidth}px` }">
                    <div v-for="hour in workHours" :key="`grid-${dayIndex}-${hour}`"
                      :class="cn('border-r border-border/30', dayIndex === todayIndex && 'bg-primary/5')"
                      :style="{ width: `${hourWidth}px` }" />
                    <div class="border-r border-border" />
                  </div>
                </template>
                <template v-else>
                  <div v-for="(date, i) in days" :key="`grid-${i}`" :class="cn(
                    'flex-shrink-0 border-r border-border',
                    isWeekend(date) && 'bg-gantt-weekend/50',
                    i === todayIndex && 'bg-primary/5',
                  )" :style="{ width: `${dayWidth}px` }" />
                </template>
              </div>

              <div v-if="todayIndex >= 0" class="absolute top-0 bottom-0 w-0.5 bg-primary z-20 pointer-events-none"
                :style="{
                  left: showHours
                    ? `${todayIndex * dayWidth + todayHourOffset * hourWidth}px`
                    : `${todayIndex * dayWidth + dayWidth / 2}px`,
                }">
                <div class="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-primary" />
              </div>

              <div v-for="(job, index) in jobs" :key="job.id" class="h-14 relative flex items-center">
                <HoverCard :open-delay="200" :close-delay="100">
                  <HoverCardTrigger as-child>
                    <div :class="cn(
                      'gantt-task absolute h-9 flex items-center px-3 text-white text-xs font-medium',
                      statusColors[job.status],
                      draggedJob === job.id && 'dragging z-30',
                    )" :style="{
                      left: `${getJobPosition(job) + 4}px`,
                      width: `${getJobWidth(job)}px`,
                      animationDelay: `${index * 50}ms`,
                    }" @mousedown="handleMouseDown($event, job.id, job.startDay, job.startHour)">
                      <div class="absolute inset-0 bg-black/20 rounded-md"
                        :style="{ clipPath: 'inset(0 ' + (100 - job.progress) + '% 0 0 round 6px)' }" />

                      <span class="relative z-10 truncate">
                        {{ getJobWidth(job) > 80 ? job.operation : '' }}
                      </span>

                      <span v-if="job.progress > 0 && getJobWidth(job) > 60"
                        class="relative z-10 ml-auto text-[10px] opacity-80">
                        {{ job.progress }}%
                      </span>

                      <div class="absolute left-0 top-0 bottom-0 w-2 cursor-ew-resize hover:bg-white/20 rounded-l-md" />
                      <div
                        class="absolute right-0 top-0 bottom-0 w-2 cursor-ew-resize hover:bg-white/20 rounded-r-md" />
                    </div>
                  </HoverCardTrigger>

                  <HoverCardContent class="w-72 p-0 overflow-hidden shadow-xl border-border" side="top" align="start"
                    :side-offset="8">
                    <div :class="cn('px-4 py-3', statusColors[job.status])">
                      <h4 class="font-semibold text-white">Job {{ job.jobCode }} / {{ job.operation }}</h4>
                    </div>

                    <div class="p-4 space-y-3 bg-card">
                      <div class="flex items-center gap-3">
                        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                          <Cpu class="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div>
                          <p class="text-xs text-muted-foreground">Machine</p>
                          <p class="text-sm font-medium text-foreground">{{ job.machine }}</p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3">
                        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                          <Clock class="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div>
                          <p class="text-xs text-muted-foreground">Thời gian</p>
                          <p class="text-sm font-medium text-foreground">
                            {{ formatFullDate(getJobStartDate(job), job.startHour) }}
                          </p>
                          <p class="text-xs text-muted-foreground">
                            Duration: {{ job.durationHours }} hours
                          </p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3">
                        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                          <AlertTriangle class="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div>
                          <p class="text-xs text-muted-foreground">Status</p>
                          <p :class="cn('text-sm font-medium', statusLabels[job.status].color)">
                            {{ statusLabels[job.status].label }}
                          </p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3">
                        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                          <TrendingUp class="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center justify-between mb-1">
                            <p class="text-xs text-muted-foreground">Progress</p>
                            <p class="text-xs font-medium text-foreground">{{ job.progress }}%</p>
                          </div>
                          <Progress :value="job.progress" class="h-2" />
                        </div>
                      </div>
                    </div>
                  </HoverCardContent>
                </HoverCard>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="w-72 flex-shrink-0 border-l border-border bg-card p-4">
        <Card class="border-blue-200 bg-blue-50">
          <CardHeader class="pb-2">
            <CardTitle class="text-sm flex items-center gap-2 text-foreground">
              <Zap class="h-4 w-4 text-primary" />
              AI Recommendation
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <p class="text-xs text-muted-foreground">Event</p>
              <p class="text-sm font-medium text-foreground">{{ aiRecommendation.event }}</p>
            </div>

            <div>
              <p class="text-xs text-muted-foreground">Action</p>
              <p class="text-sm font-medium text-primary">{{ aiRecommendation.action }}</p>
            </div>

            <div>
              <p class="text-xs text-muted-foreground mb-1">Expected Impact</p>
              <div class="space-y-1">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted-foreground">Tardiness</span>
                  <span class="text-success font-medium">{{ aiRecommendation.impact.tardiness }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-muted-foreground">Utilization</span>
                  <span class="text-success font-medium">{{ aiRecommendation.impact.utilization }}</span>
                </div>
              </div>
            </div>

            <div>
              <p class="text-xs text-muted-foreground mb-1">Confidence</p>
              <div class="flex items-center gap-2">
                <Progress :value="aiRecommendation.confidence" class="h-2 flex-1" />
                <span class="text-sm font-medium text-foreground">{{ aiRecommendation.confidence }}%</span>
              </div>
            </div>

            <div class="flex gap-2 pt-2">
              <Button size="sm" class="flex-1" :disabled="aiApplied" @click="handleApplyAI">
                {{ aiApplied ? 'Applied' : 'Apply' }}
              </Button>
              <Button size="sm" variant="outline" class="flex-1" @click="handleIgnoreAI">
                {{ aiApplied ? 'Reset' : 'Ignore' }}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div class="mt-4 p-3 rounded-lg bg-muted/50">
          <p class="text-xs font-medium text-muted-foreground mb-2">Risk Legend</p>
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-[#22c55e]" />
              <span class="text-xs text-foreground">On-time</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-[#facc15]" />
              <span class="text-xs text-foreground">At Risk (low slack)</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-[#ef4444]" />
              <span class="text-xs text-foreground">Late / High Priority</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="border-t border-border bg-card p-4">
      <div class="flex items-center gap-2 mb-4">
        <Factory class="h-5 w-5 text-primary" />
        <h3 class="text-sm font-semibold text-foreground">Workstations by Plant Floor</h3>
      </div>

      <div v-if="plantFloors.length === 0" class="text-center py-8 text-muted-foreground">
        No plant floors or workstations configured
      </div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card v-for="(floor, floorIndex) in plantFloors" :key="floor.floor" class="border-border">
          <CardHeader class="pb-2 pt-3 px-4">
            <CardTitle class="text-xs font-semibold flex items-center gap-2">
              <div :class="cn(
                'w-2 h-2 rounded-full',
                floorIndex === 0 ? 'bg-primary' : floorIndex === 1 ? 'bg-warning' : 'bg-info'
              )" />
              {{ floor.floor }}
            </CardTitle>
            <p v-if="floor.description" class="text-[10px] text-muted-foreground mt-1">
              {{ floor.description }}
            </p>
          </CardHeader>
          <CardContent class="px-4 pb-3 space-y-2">
            <div v-if="floor.workstations.length === 0" class="text-xs text-muted-foreground text-center py-2">
              No workstations
            </div>
            <div v-else v-for="ws in floor.workstations" :key="ws.id" 
              class="flex items-center justify-between p-2 rounded-md bg-muted/50">
              <div class="flex items-center gap-2">
                <Cpu class="h-3.5 w-3.5 text-muted-foreground" />
                <div>
                  <p class="text-xs font-medium text-foreground">{{ ws.id }}</p>
                  <p class="text-[10px] text-muted-foreground">{{ ws.name }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <div :class="cn(
                  'w-1.5 h-1.5 rounded-full',
                  ws.status === 'Production' ? 'bg-success' : 
                  ws.status === 'Maintenance' ? 'bg-warning' : 
                  'bg-muted-foreground'
                )" />
                <span class="text-[10px] text-muted-foreground">
                  {{ ws.status === 'Maintenance' ? 'Maint.' : `${Math.round(ws.utilization)}%` }}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="flex items-center gap-6 mt-4 pt-3 border-t border-border">
        <div class="flex items-center gap-2">
          <CircleDot class="h-3 w-3 text-success" />
          <span class="text-xs text-muted-foreground">Production</span>
        </div>
        <div class="flex items-center gap-2">
          <CircleDot class="h-3 w-3 text-muted-foreground" />
          <span class="text-xs text-muted-foreground">Idle / Stopped</span>
        </div>
        <div class="flex items-center gap-2">
          <CircleDot class="h-3 w-3 text-warning" />
          <span class="text-xs text-muted-foreground">Maintenance</span>
        </div>
      </div>
    </div>

    <Card
      class="mt-6 border-0 bg-gradient-to-br from-violet-500/10 via-purple-500/10 to-fuchsia-500/10 relative overflow-hidden">
      <div
        class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-500/20 to-transparent rounded-full blur-2xl" />
      <div
        class="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-fuchsia-500/20 to-transparent rounded-full blur-2xl" />

      <CardHeader class="pb-3 relative">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg shadow-violet-500/25">
            <Brain class="h-5 w-5 text-white" />
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <CardTitle
                class="text-lg font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                📊 PHÂN TÍCH TỔNG THỂ LẦN CHẠY DỰ BÁO
              </CardTitle>
              <Sparkles class="h-4 w-4 text-violet-500 animate-pulse" />
            </div>
            <p class="text-xs text-muted-foreground mt-0.5">Powered by Machine Learning • Confidence: 68%</p>
          </div>
        </div>
      </CardHeader>

      <CardContent class="space-y-5 relative">
        <div class="p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-violet-500/20">
          <div class="flex items-start gap-3">
            <div class="p-2 rounded-lg bg-violet-500/10">
              <BarChart3 class="h-4 w-4 text-violet-500" />
            </div>
            <div class="flex-1">
              <h5 class="font-semibold text-sm text-foreground mb-1">📋 TÓM TẮT TỔNG QUAN</h5>
              <p class="text-xs text-muted-foreground leading-relaxed">
                Lần chạy dự báo "Linear Regression - 2025-12-22" đã hoàn thành với tổng số 13 items dự báo, trong đó tất
                cả
                đều thành công. Độ tin cậy trung bình của model là 50.0%, cho thấy cần có những phân tích sau để cải
                thiện
                kết quả.
              </p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            class="group p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-emerald-500/20 hover:border-emerald-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10">
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-lg bg-emerald-500/10 group-hover:bg-emerald-500/20 transition-colors">
                <CheckCircle class="h-4 w-4 text-emerald-500" />
              </div>
              <div class="flex-1">
                <h5 class="font-semibold text-sm text-foreground mb-1">✅ HIỆU QUẢ MODEL</h5>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  Model Linear Regression đã thực hiện tốt khi không có item nào thất bại, tuy nhiên độ tin cậy 50.0%
                  cho
                  thấy có khả năng dự đoán chưa cao, cần cân nhắc đến việc thu thập và phân tích dữ liệu để tăng cường
                  độ
                  chính xác.
                </p>
              </div>
            </div>
          </div>

          <div
            class="group p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-blue-500/20 hover:border-blue-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-lg bg-blue-500/10 group-hover:bg-blue-500/20 transition-colors">
                <TrendingUp class="h-4 w-4 text-blue-500" />
              </div>
              <div class="flex-1">
                <h5 class="font-semibold text-sm text-foreground mb-1">📈 XU HƯỚNG CHUNG</h5>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  Tổng nhu cầu dự báo là 10314.1 đơn vị, cho thấy nhu cầu thị trường có xu hướng khá cao. Phân loại
                  movement
                  cho thấy có 9 items slow moving và 4 items fast moving. Phân loại trend cho thấy 12 items stable và 1
                  item
                  có xu hướng downward.
                </p>
              </div>
            </div>
          </div>

          <div
            class="group p-4 rounded-xl bg-card/50 backdrop-blur-sm border border-amber-500/20 hover:border-amber-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-amber-500/10">
            <div class="flex items-start gap-3">
              <div class="p-2 rounded-lg bg-amber-500/10 group-hover:bg-amber-500/20 transition-colors">
                <AlertTriangle class="h-4 w-4 text-amber-500" />
              </div>
              <div class="flex-1">
                <h5 class="font-semibold text-sm text-foreground mb-1">⚠️ CẢNH BÁO VÀ ƯU TIÊN</h5>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  Cần chú ý đến 2 items cần đặt hàng, vì điều này có thể ảnh hưởng đến khan hiếm hàng. Các items slow
                  moving
                  cần được quan tâm để không bị tồn tồn lượng tồn kho.
                </p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-600 font-medium">High
                    Priority</span>
                  <span class="text-[10px] text-muted-foreground">2 items cần đặt hàng</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-4 rounded-xl bg-gradient-to-r from-violet-500/5 to-purple-500/5 border border-violet-500/30">
          <div class="flex items-center gap-2 mb-3">
            <Target class="h-4 w-4 text-violet-500" />
            <h5 class="font-semibold text-sm text-foreground">🎯 KHUYẾN NGHỊ CHIẾN LƯỢC</h5>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div v-for="(rec, idx) in [
              {
                title: 'Điều chỉnh Model',
                desc: 'Xem xét điều chỉnh model dự đoán để tăng độ tin cậy, có thể sử dụng phương pháp khác hoặc kết hợp với các mô hình dự đoán khác.',
                icon: Target,
                color: 'violet',
                priority: 'High Priority',
                impact: '+15% accuracy',
              },
              {
                title: 'Quản lý Slow Moving',
                desc: 'Tính toán và theo dõi các items slow moving để có kế hoạch nhập hàng phù hợp, tránh tồn kho.',
                icon: TrendingDown,
                color: 'purple',
                priority: 'Medium Priority',
                impact: '-20% inventory',
              },
              {
                title: 'Phát triển Fast Moving',
                desc: 'Duy trì và phát triển các item fast moving, có thể cạnh tranh và đẩy nhanh khoảng cung.',
                icon: TrendingUp,
                color: 'fuchsia',
                priority: 'Quick Win',
                impact: '+12% revenue',
              },
              {
                title: 'Phân tích Thị trường',
                desc: 'Thực hiện phân tích thị trường định kỳ để có dữ liệu cập nhật, từ đó có kế hoạch nhập hàng và phân phối hiệu quả.',
                icon: BarChart3,
                color: 'indigo',
                priority: 'Strategic',
                impact: 'Long-term growth',
              },
            ]" :key="idx" :class="cn(
              'group p-3 rounded-lg bg-card/50 border transition-all duration-300 hover:shadow-lg',
              rec.color === 'violet' && 'border-violet-500/20 hover:border-violet-500/40 hover:shadow-violet-500/10',
              rec.color === 'purple' && 'border-purple-500/20 hover:border-purple-500/40 hover:shadow-purple-500/10',
              rec.color === 'fuchsia' && 'border-fuchsia-500/20 hover:border-fuchsia-500/40 hover:shadow-fuchsia-500/10',
              rec.color === 'indigo' && 'border-indigo-500/20 hover:border-indigo-500/40 hover:shadow-indigo-500/10',
            )">
              <div class="flex items-start gap-2">
                <div :class="cn(
                  'p-1.5 rounded-md transition-colors',
                  rec.color === 'violet' && 'bg-violet-500/10 group-hover:bg-violet-500/20',
                  rec.color === 'purple' && 'bg-purple-500/10 group-hover:bg-purple-500/20',
                  rec.color === 'fuchsia' && 'bg-fuchsia-500/10 group-hover:bg-fuchsia-500/20',
                  rec.color === 'indigo' && 'bg-indigo-500/10 group-hover:bg-indigo-500/20',
                )">
                  <component :is="rec.icon" :class="cn(
                    'h-3.5 w-3.5',
                    rec.color === 'violet' && 'text-violet-500',
                    rec.color === 'purple' && 'text-purple-500',
                    rec.color === 'fuchsia' && 'text-fuchsia-500',
                    rec.color === 'indigo' && 'text-indigo-500',
                  )" />
                </div>
                <div class="flex-1">
                  <h6 class="font-medium text-xs text-foreground">{{ rec.title }}</h6>
                  <p class="text-[10px] text-muted-foreground leading-relaxed mt-0.5">{{ rec.desc }}</p>
                  <div class="flex items-center gap-2 mt-1.5">
                    <span :class="cn(
                      'text-[9px] px-1.5 py-0.5 rounded-full font-medium',
                      rec.color === 'violet' && 'bg-violet-500/20 text-violet-600',
                      rec.color === 'purple' && 'bg-purple-500/20 text-purple-600',
                      rec.color === 'fuchsia' && 'bg-fuchsia-500/20 text-fuchsia-600',
                      rec.color === 'indigo' && 'bg-indigo-500/20 text-indigo-600',
                    )">
                      {{ rec.priority }}
                    </span>
                    <span class="text-[9px] text-muted-foreground">{{ rec.impact }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between pt-3 border-t border-border/50">
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <Lightbulb class="h-3.5 w-3.5 text-amber-500" />
            <span>AI phân tích dựa trên dữ liệu 13 items và 1 forecast run 📦📈</span>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="ghost" size="sm" class="text-xs h-8 text-muted-foreground hover:text-foreground">
              Bỏ qua
            </Button>
            <Button size="sm"
              class="text-xs h-8 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white shadow-lg shadow-violet-500/25">
              Áp dụng tất cả
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
