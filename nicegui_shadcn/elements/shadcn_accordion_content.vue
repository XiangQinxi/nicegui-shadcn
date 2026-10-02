<template>
  <AccordionContent force-mount v-bind="$attrs">
    <div class="pt-0 pb-4">
      <slot />
    </div>
  </AccordionContent>
</template>

<script>
import { AccordionContent } from 'reka-ui';

export default {
  name: 'ShadcnAccordionContent',
  components: { AccordionContent },
  inheritAttrs: false,
};
</script>
