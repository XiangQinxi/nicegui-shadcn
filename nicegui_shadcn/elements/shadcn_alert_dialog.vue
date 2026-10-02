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
    modelValue: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
