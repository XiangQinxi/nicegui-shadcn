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
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
