<script setup lang="ts">
import type { HTMLAttributes } from "vue";

import { cn } from "@/lib/utils";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  checked?: boolean;
  disabled?: boolean;
}>();

const emits = defineEmits<{
  (e: "update:checked", value: boolean): void;
  (e: "change", value: boolean): void;
}>();

const toggle = () => {
  if (props.disabled) return;
  const next = !props.checked;
  emits("update:checked", next);
  emits("change", next);
};
</script>

<template>
  <button
    type="button"
    role="checkbox"
    :aria-checked="props.checked"
    :disabled="props.disabled"
    :class="
      cn(
        'h-4 w-4 shrink-0 rounded border border-input bg-background ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        props.checked ? 'bg-primary text-primary-foreground' : '',
        props.class,
      )
    "
    @click="toggle"
  >
    <svg v-if="props.checked" viewBox="0 0 24 24" class="h-3 w-3" aria-hidden="true">
      <path
        d="M20.285 6.708a1 1 0 0 0-1.57-1.248l-8.246 10.386-4.184-4.392a1 1 0 0 0-1.43 1.4l4.986 5.235a1 1 0 0 0 1.52-.06l8.924-11.321z"
        fill="currentColor"
      />
    </svg>
  </button>
</template>
