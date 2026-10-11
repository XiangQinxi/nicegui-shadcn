<template>
  <AccordionHeader class="flex">
    <AccordionTrigger v-bind="$attrs">
      <slot />
      <svg
        class="pointer-events-none size-4 shrink-0 translate-y-0.5 text-muted-foreground transition-transform duration-200"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </AccordionTrigger>
  </AccordionHeader>
</template>

<script>
import { AccordionHeader, AccordionTrigger } from 'reka-ui';

export default {
  name: 'ShadcnAccordionTrigger',
  components: { AccordionHeader, AccordionTrigger },
  inheritAttrs: false,
};
</script>
