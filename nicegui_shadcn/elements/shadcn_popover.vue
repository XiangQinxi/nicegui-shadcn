<template>
  <PopoverRoot :open="modelValue" @update:open="$emit('update:modelValue', $event)">
    <slot />
  </PopoverRoot>
</template>

<script>
import { PopoverRoot } from 'reka-ui';

export default {
  name: 'ShadcnPopover',
  components: { PopoverRoot },
  // PopoverRoot renders a fragment, so there is no element to receive attrs.
  inheritAttrs: false,
  props: {
    modelValue: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
