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
    modelValue: { type: [String, Number], default: undefined },
    orientation: { type: String, default: 'horizontal' },
  },
  emits: ['update:modelValue'],
};
</script>
