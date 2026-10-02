<template>
  <Toggle
    :model-value="modelValue"
    :disabled="disabled"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <slot />
  </Toggle>
</template>

<script>
import { Toggle } from 'reka-ui';

export default {
  name: 'ShadcnToggle',
  components: { Toggle },
  props: {
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
