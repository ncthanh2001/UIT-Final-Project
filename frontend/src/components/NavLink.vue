<script setup lang="ts">
import { RouterLink, useLink } from "vue-router"
import { computed, useAttrs } from "vue"
import { cn } from "@/lib/utils"

interface NavLinkProps {
  to: string | Record<string, unknown>
  class?: string
  activeClass?: string
  pendingClass?: string
}

const props = withDefaults(defineProps<NavLinkProps>(), {
  class: "",
  activeClass: "",
  pendingClass: "",
})

const attrs = useAttrs()
const link = useLink({ to: computed(() => props.to) })

const classes = computed(() => {
  const isActive = link.isActive.value || link.isExactActive.value
  const isPending = link.isExactActive.value && !link.isActive.value
  return cn(props.class, isActive && props.activeClass, isPending && props.pendingClass)
})
</script>

<template>
  <RouterLink
    v-slot="{ href, navigate }"
    v-bind="attrs"
    :to="props.to"
    custom
  >
    <a
      :href="href"
      :class="classes"
      @click="navigate"
    >
      <slot />
    </a>
  </RouterLink>
</template>
