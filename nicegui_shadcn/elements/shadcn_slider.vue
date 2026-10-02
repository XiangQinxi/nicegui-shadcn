<template>
  <SliderRoot
    :model-value="[modelValue]"
    :min="min"
    :max="max"
    :step="step"
    :orientation="orientation"
    :disabled="disabled"
    @update:model-value="$emit('update:modelValue', Array.isArray($event) ? $event[0] : $event)"
  >
    <SliderTrack class="relative h-1.5 w-full grow overflow-hidden rounded-full bg-primary/20">
      <SliderRange class="absolute h-full bg-primary" />
    </SliderTrack>
    <SliderThumb class="block size-4 shrink-0 rounded-full border border-primary bg-background shadow-sm transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50" />
  </SliderRoot>
</template>

<script>
import { SliderRange, SliderRoot, SliderThumb, SliderTrack } from 'reka-ui';

export default {
  name: 'ShadcnSlider',
  components: { SliderRange, SliderRoot, SliderThumb, SliderTrack },
  props: {
    modelValue: { type: Number, default: 0 },
    min: { type: Number, default: 0 },
    max: { type: Number, default: 100 },
    step: { type: Number, default: 1 },
    orientation: { type: String, default: 'horizontal' },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
