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
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: [String, Array], default: undefined },
    type: { type: String, default: 'single' },
    collapsible: { type: Boolean, default: true },
    orientation: { type: String, default: 'vertical' },
  },
  emits: ['update:modelValue'],
};
</script>
