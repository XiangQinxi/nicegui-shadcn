<template>
  <span class="relative inline-flex shrink-0 items-center justify-center">
    <input
      :id="id"
      type="checkbox"
      class="peer size-4 shrink-0 cursor-pointer appearance-none rounded-[4px] border border-input bg-transparent shadow-xs outline-none transition-shadow focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 checked:border-primary checked:bg-primary disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30"
      :checked="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.checked)"
    >
    <svg
      class="pointer-events-none absolute inset-0 m-auto size-3 text-primary-foreground opacity-0 transition-opacity peer-checked:opacity-100"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="3"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  </span>
</template>

<script>
export default {
  name: 'ShadcnCheckbox',
  props: {
    id: { type: String, default: undefined },
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
