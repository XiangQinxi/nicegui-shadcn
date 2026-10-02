<template>
  <DialogRoot :open="modelValue" @update:open="$emit('update:modelValue', $event)">
    <slot />
  </DialogRoot>
</template>

<script>
import { DialogRoot } from 'reka-ui';

export default {
  name: 'ShadcnDialog',
  components: { DialogRoot },
  // DialogRoot renders a fragment, so there is no single element for Vue to put
  // fallthrough attributes on -- without this Vue warns about extraneous attrs.
  inheritAttrs: false,
  props: {
    modelValue: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
};
</script>
