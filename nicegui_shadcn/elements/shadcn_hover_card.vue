<template>
  <HoverCardRoot
    :open="modelValue"
    :open-delay="openDelay"
    :close-delay="closeDelay"
    @update:open="$emit('update:modelValue', $event)"
  >
    <slot />
  </HoverCardRoot>
</template>

<script>
import { HoverCardRoot } from 'reka-ui';

export default {
  name: 'ShadcnHoverCard',
  components: { HoverCardRoot },
  // HoverCardRoot renders a fragment, so there is no element to receive attrs.
  inheritAttrs: false,
  props: {
    modelValue: { type: Boolean, default: undefined },
    openDelay: { type: Number, default: 200 },
    closeDelay: { type: Number, default: 150 },
  },
  emits: ['update:modelValue'],
};
</script>
