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
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: Boolean, default: undefined },
    openDelay: { type: Number, default: 200 },
    closeDelay: { type: Number, default: 150 },
  },
  emits: ['update:modelValue'],
};
</script>
