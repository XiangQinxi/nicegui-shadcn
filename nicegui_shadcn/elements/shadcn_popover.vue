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
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
