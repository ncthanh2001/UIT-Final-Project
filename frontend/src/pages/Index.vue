<script setup lang="ts">
import { computed } from "vue"
import { useRoute } from "vue-router"
import GanttChart from "@/components/GanttChart.vue"
import Dashboard from "@/pages/Dashboard.vue" 
const route = useRoute()

const currentComponent = computed(() => {
  switch (route.path) {
    case "/dashboard":
      return Dashboard 
    case "/":
    default:
      return GanttChart
  }
})
</script>

<template>
  <main class="min-h-screen bg-background">
    <component :is="currentComponent" />
  </main>
</template>
