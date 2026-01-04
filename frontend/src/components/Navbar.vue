<script setup lang="ts">
import { Bell, Menu } from "lucide-vue-next"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface NavbarProps {
  onMenuClick?: () => void
}

const props = defineProps<NavbarProps>()
</script>

<template>
  <nav class="sticky top-0 z-50 w-full border-b border-border bg-card/80 backdrop-blur-md">
    <div class="flex h-14 items-center justify-between px-4 md:px-6">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" class="md:hidden" @click="props.onMenuClick && props.onMenuClick()">
          <Menu class="h-5 w-5" />
        </Button>

        <div class="flex items-center gap-2">
          <h1 class="text-lg font-semibold text-foreground">Gantt Chart</h1>
          <span class="text-sm text-muted-foreground hidden sm:inline">/ Project Alpha</span>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <Button variant="ghost" size="icon" class="relative h-9 w-9">
          <Bell class="h-5 w-5" />
          <span
            class="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground"
          >
            3
          </span>
        </Button>

        <Avatar class="h-8 w-8 ring-2 ring-primary/20 cursor-pointer hover:ring-primary/40 transition-all">
          <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&amp;h=100&amp;fit=crop" />
          <AvatarFallback class="bg-primary text-primary-foreground text-sm">JD</AvatarFallback>
        </Avatar>
      </div>
    </div>
  </nav>
</template>
