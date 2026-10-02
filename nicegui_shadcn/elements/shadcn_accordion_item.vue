<template>
  <AccordionItem :value="value" :disabled="disabled">
    <slot />
  </AccordionItem>
</template>

<script>
import { AccordionItem } from 'reka-ui';

export default {
  name: 'ShadcnAccordionItem',
  components: { AccordionItem },
  props: {
    value: { type: String, required: true },
    disabled: { type: Boolean, default: false },
  },
};
</script>
