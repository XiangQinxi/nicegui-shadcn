<template>
  <span class="relative inline-flex shrink-0 items-center">
    <input
      :id="id"
      type="checkbox"
      class="peer h-[1.15rem] w-8 shrink-0 cursor-pointer appearance-none rounded-full border border-transparent bg-input shadow-xs outline-none transition-colors focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 checked:bg-primary disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/80"
      :checked="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.checked)"
    >
    <span
      class="pointer-events-none absolute left-[1px] top-[1px] size-4 rounded-full bg-background shadow-sm transition-transform peer-checked:translate-x-[14px]"
    ></span>
  </span>
</template>

<script>
export default {
  name: 'ShadcnSwitch',
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    id: { type: String, default: undefined },
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
