<template>
  <ToastRoot
    :open="modelValue"
    :duration="duration"
    data-shadcn_toast
    :class="variantClasses"
    class="group pointer-events-auto relative flex w-full items-start justify-between gap-3 overflow-hidden rounded-md border p-4 shadow-lg data-[state=closed]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:animate-in data-[state=open]:slide-in-from-bottom-full"
    @update:open="$emit('update:modelValue', $event)"
  >
    <div class="flex flex-col gap-1">
      <ToastTitle v-if="title" class="text-sm font-semibold">{{ title }}</ToastTitle>
      <ToastDescription v-if="description" class="text-sm opacity-90">{{ description }}</ToastDescription>
      <slot />
    </div>
    <ToastClose
      v-if="closable"
      class="shrink-0 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <svg
        class="size-4"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
      </svg>
      <span class="sr-only">Close</span>
    </ToastClose>
  </ToastRoot>
</template>

<script>
import { ToastClose, ToastDescription, ToastRoot, ToastTitle } from 'reka-ui';

const VARIANTS = {
  default: 'border bg-background text-foreground',
  destructive: 'border-destructive bg-destructive text-white',
  success: 'border bg-background text-foreground',
};

export default {
  name: 'ShadcnToast',
  components: { ToastClose, ToastDescription, ToastRoot, ToastTitle },
  inheritAttrs: false,
  props: {
    modelValue: { type: Boolean, default: false },
    title: { type: String, default: '' },
    description: { type: String, default: '' },
    variant: { type: String, default: 'default' },
    duration: { type: Number, default: 5000 },
    closable: { type: Boolean, default: true },
  },
  emits: ['update:modelValue'],
  computed: {
    variantClasses() {
      return VARIANTS[this.variant] || VARIANTS.default;
    },
  },
};
</script>
