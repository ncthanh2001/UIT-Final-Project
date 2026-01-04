<script setup lang="ts">
import { ArrowLeft, Home } from "lucide-vue-next"
import { useRouter } from "vue-router"
import { Button } from "@/components/ui/button"
import logo from "@/assets/logo.png"

interface BackButtonProps {
  to?: string
  label?: string
  showHome?: boolean
}

const props = withDefaults(defineProps<BackButtonProps>(), {
  label: "Quay lại",
  showHome: true,
})

const router = useRouter()

function handleBack() {
  if (props.to) {
    router.push(props.to)
  } else {
    router.back()
  }
}

function handleHome() {
  router.push("/")
}
</script>

<template>
  <div class="flex items-center gap-3">
    <img :src="logo" alt="Logo" class="h-8 w-auto" />
    <Button
      variant="ghost"
      size="sm"
      @click="handleBack"
      class="gap-2 text-muted-foreground hover:text-foreground"
    >
      <ArrowLeft class="h-4 w-4" />
      {{ props.label }}
    </Button>
    <Button
      v-if="props.showHome"
      variant="ghost"
      size="icon"
      @click="handleHome"
      class="text-muted-foreground hover:text-foreground"
      title="Về trang chủ"
    >
      <Home class="h-4 w-4" />
    </Button>
  </div>
</template>
