<template>
  <ToggleGroupRoot
    :type="type"
    :model-value="modelValue"
    :orientation="orientation"
    :disabled="disabled"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <ToggleGroupItem
      v-for="option in options"
      :key="option.value"
      :value="option.value"
      :disabled="option.disabled"
      class="inline-flex items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium whitespace-nowrap text-muted-foreground transition-all hover:bg-muted hover:text-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 data-[state=on]:bg-accent data-[state=on]:text-accent-foreground"
    >{{ option.label }}</ToggleGroupItem>
  </ToggleGroupRoot>
</template>

<script>
import { ToggleGroupItem, ToggleGroupRoot } from 'reka-ui';

export default {
  name: 'ShadcnToggleGroup',
  components: { ToggleGroupItem, ToggleGroupRoot },
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: [String, Array], default: undefined },
    options: { type: Array, default: () => [] },
    type: { type: String, default: 'single' },
    orientation: { type: String, default: 'horizontal' },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
