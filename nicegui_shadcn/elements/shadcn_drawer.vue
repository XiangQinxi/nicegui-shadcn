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
    modelValue: { type: Boolean, default: false },
    modal: { type: Boolean, default: true },
    snapPoints: { type: Array, default: null },
    snapPoint: { type: [String, Number], default: null },
  },
  emits: ['update:modelValue', 'update:snapPoint'],
};
</script>
