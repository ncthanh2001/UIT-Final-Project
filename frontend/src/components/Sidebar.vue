<script setup lang="ts">
import type { Component } from "vue"
import {
  LayoutDashboard,
  CalendarDays,
  Users,
  FolderKanban,
  CheckSquare,
  BarChart3,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  Inbox,
  Star,
  Clock,
  Database,
} from "lucide-vue-next"
import { useRouter, useRoute } from "vue-router"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

interface NavItem {
  icon: Component
  label: string
  href: string
  badge?: number
}

const props = defineProps<SidebarProps>()

const mainNavItems: NavItem[] = [
  { icon: Database, label: "Data Collection", href: "/data-collection" },
  { icon: CalendarDays, label: "Gantt Chart", href: "/gantt" },
  { icon: LayoutDashboard, label: "Forecast History", href: "/forecast-history" },
  { icon: Inbox, label: "Inbox", href: "/inbox", badge: 5 },
  { icon: FolderKanban, label: "Kanban Board", href: "/kanban" },
  { icon: CheckSquare, label: "Tasks", href: "/tasks", badge: 12 },
  { icon: Clock, label: "Timeline", href: "/timeline" },
]

const secondaryNavItems: NavItem[] = [
  { icon: Users, label: "Team", href: "/team" },
  { icon: BarChart3, label: "Reports", href: "/reports" },
  { icon: Star, label: "Favorites", href: "/favorites" },
]

const bottomNavItems: NavItem[] = [
  { icon: Settings, label: "Settings", href: "/settings" },
  { icon: HelpCircle, label: "Help & Support", href: "/help" },
]

const router = useRouter()
const route = useRoute()

const navigate = (href: string) => {
  if (route.path !== href) {
    router.push(href)
  }
}
</script>

<template>
  <aside
    :class="cn(
      'flex flex-col h-full bg-card border-r border-border transition-all duration-300 ease-in-out',
      props.collapsed ? 'w-16' : 'w-64',
    )"
  >
    <div
      :class="cn(
        'flex items-center h-16 px-4 border-b border-border',
        props.collapsed ? 'justify-center' : 'gap-3',
      )"
    >
      <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary flex-shrink-0">
        <CalendarDays class="h-5 w-5 text-primary-foreground" />
      </div>
      <span v-if="!props.collapsed" class="text-xl font-bold text-foreground animate-fade-in">Planify</span>
    </div>

    <div class="flex-1 overflow-y-auto scrollbar-thin py-4 px-3">
      <div class="space-y-1">
        <p
          v-if="!props.collapsed"
          class="px-3 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Main
        </p>
        <button
          v-for="item in mainNavItems"
          :key="item.label"
          @click="navigate(item.href)"
          :class="cn(
            'w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
            route.path === item.href
              ? 'bg-primary text-primary-foreground shadow-md'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground',
          )"
        >
          <component
            :is="item.icon"
            :class="cn(
              'h-5 w-5 flex-shrink-0 transition-transform',
              route.path !== item.href && 'group-hover:scale-110',
            )"
          />

          <template v-if="!props.collapsed">
            <span class="flex-1 text-sm font-medium truncate">{{ item.label }}</span>
            <Badge
              v-if="item.badge"
              :variant="route.path === item.href ? 'secondary' : 'default'"
              :class="cn(
                'h-5 min-w-5 px-1.5 text-[10px] font-semibold',
                route.path === item.href && 'bg-primary-foreground/20 text-primary-foreground',
              )"
            >
              {{ item.badge }}
            </Badge>
          </template>

          <div
            v-else
            class="absolute left-full ml-2 px-2 py-1 bg-foreground text-background text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50"
          >
            {{ item.label }}
            <template v-if="item.badge"> ({{ item.badge }}) </template>
          </div>
        </button>
      </div>

      <Separator class="my-4" />

      <div class="space-y-1">
        <p
          v-if="!props.collapsed"
          class="px-3 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider"
        >
          Workspace
        </p>
        <button
          v-for="item in secondaryNavItems"
          :key="item.label"
          @click="navigate(item.href)"
          :class="cn(
            'w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
            route.path === item.href
              ? 'bg-primary text-primary-foreground shadow-md'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground',
          )"
        >
          <component
            :is="item.icon"
            :class="cn(
              'h-5 w-5 flex-shrink-0 transition-transform',
              route.path !== item.href && 'group-hover:scale-110',
            )"
          />

          <template v-if="!props.collapsed">
            <span class="flex-1 text-sm font-medium truncate">{{ item.label }}</span>
            <Badge
              v-if="item.badge"
              :variant="route.path === item.href ? 'secondary' : 'default'"
              :class="cn(
                'h-5 min-w-5 px-1.5 text-[10px] font-semibold',
                route.path === item.href && 'bg-primary-foreground/20 text-primary-foreground',
              )"
            >
              {{ item.badge }}
            </Badge>
          </template>

          <div
            v-else
            class="absolute left-full ml-2 px-2 py-1 bg-foreground text-background text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50"
          >
            {{ item.label }}
          </div>
        </button>
      </div>
    </div>

    <div class="mt-auto border-t border-border py-4 px-3 space-y-1">
      <button
        v-for="item in bottomNavItems"
        :key="item.label"
        @click="navigate(item.href)"
        :class="cn(
          'w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
          route.path === item.href
            ? 'bg-primary text-primary-foreground shadow-md'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground',
        )"
      >
        <component
          :is="item.icon"
          :class="cn(
            'h-5 w-5 flex-shrink-0 transition-transform',
            route.path !== item.href && 'group-hover:scale-110',
          )"
        />

        <template v-if="!props.collapsed">
          <span class="flex-1 text-sm font-medium truncate">{{ item.label }}</span>
        </template>
        <div
          v-else
          class="absolute left-full ml-2 px-2 py-1 bg-foreground text-background text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50"
        >
          {{ item.label }}
        </div>
      </button>
    </div>

    <div class="p-3 border-t border-border">
      <Button
        variant="ghost"
        size="sm"
        @click="props.onToggle"
        :class="cn('w-full justify-center text-muted-foreground hover:text-foreground', !props.collapsed && 'justify-start gap-2')"
      >
        <template v-if="props.collapsed">
          <ChevronRight class="h-4 w-4" />
        </template>
        <template v-else>
          <ChevronLeft class="h-4 w-4" />
          <span>Collapse</span>
        </template>
      </Button>
    </div>
  </aside>
</template>
