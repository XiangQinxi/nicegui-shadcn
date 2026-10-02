<template>
  <AccordionRoot
    :type="type"
    :collapsible="collapsible"
    :model-value="modelValue"
    :orientation="orientation"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <slot />
  </AccordionRoot>
</template>

<script>
import { AccordionRoot } from 'reka-ui';

export default {
  name: 'ShadcnAccordion',
  components: { AccordionRoot },
  props: {
    modelValue: { type: [String, Array], default: undefined },
    type: { type: String, default: 'single' },
    collapsible: { type: Boolean, default: true },
    orientation: { type: String, default: 'vertical' },
  },
  emits: ['update:modelValue'],
};
</script>
