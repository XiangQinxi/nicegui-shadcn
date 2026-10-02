<template>
  <TabsRoot
    :model-value="modelValue"
    :orientation="orientation"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <slot />
  </TabsRoot>
</template>

<script>
import { TabsRoot } from 'reka-ui';

export default {
  name: 'ShadcnTabs',
  components: { TabsRoot },
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: [String, Number], default: undefined },
    orientation: { type: String, default: 'horizontal' },
  },
  emits: ['update:modelValue'],
};
</script>
