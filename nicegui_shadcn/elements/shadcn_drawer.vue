<template>
  <DrawerRoot
    :open="modelValue"
    :modal="modal"
    :snap-points="snapPoints"
    :snap-point="snapPoint"
    @update:open="$emit('update:modelValue', $event)"
    @update:snap-point="$emit('update:snapPoint', $event)"
  >
    <slot />
  </DrawerRoot>
</template>

<script>
import { DrawerRoot } from 'reka-ui';

export default {
  name: 'ShadcnDrawer',
  components: { DrawerRoot },
  // DrawerRoot renders a fragment, so there is no element to receive attrs.
  inheritAttrs: false,
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: Boolean, default: false },
    modal: { type: Boolean, default: true },
    snapPoints: { type: Array, default: null },
    snapPoint: { type: [String, Number], default: null },
  },
  emits: ['update:modelValue', 'update:snapPoint'],
};
</script>
