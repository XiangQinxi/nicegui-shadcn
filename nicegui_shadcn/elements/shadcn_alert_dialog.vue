<template>
  <AlertDialogRoot :open="modelValue" @update:open="$emit('update:modelValue', $event)">
    <slot />
  </AlertDialogRoot>
</template>

<script>
import { AlertDialogRoot } from 'reka-ui';

export default {
  name: 'ShadcnAlertDialog',
  components: { AlertDialogRoot },
  // AlertDialogRoot only renders its slot, so there is no element for Vue to put
  // fallthrough attributes on -- without this Vue warns about extraneous attrs.
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
