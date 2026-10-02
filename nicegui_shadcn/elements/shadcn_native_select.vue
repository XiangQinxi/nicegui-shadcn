<template>
  <div>
    <select
      ref="select"
      class="border-input placeholder:text-muted-foreground dark:bg-input/30 flex h-9 w-full min-w-0 appearance-none rounded-md border bg-transparent px-3 py-1 pr-8 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option
        v-for="item in items"
        :key="item.value"
        :value="item.value"
        :disabled="item.disabled || undefined"
      >{{ item.label }}</option>
    </select>
    <svg
      class="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-muted-foreground select-none"
      xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
    ><path d="m6 9 6 6 6-6" /></svg>
  </div>
</template>

<script>
export default {
  name: 'ShadcnNativeSelect',
  props: {
    modelValue: { type: [String, Number], default: '' },
    items: { type: Array, default: () => [] },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  watch: {
    // ``<select>`` needs its options to exist before a value can be assigned, and
    // Vue patches props before children, so the value is written one tick later.
    modelValue: { immediate: true, handler() { this.sync(); } },
    items() { this.sync(); },
  },
  methods: {
    sync() {
      this.$nextTick(() => {
        const element = this.$refs.select;
        if (element) element.value = String(this.modelValue ?? '');
      });
    },
  },
};
</script>
