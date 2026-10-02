<template>
  <AccordionHeader class="flex">
    <AccordionTrigger
      v-bind="$attrs"
      class="flex flex-1 items-start justify-between gap-4 rounded-md py-4 text-left text-sm font-medium outline-none transition-all hover:underline focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 [&[data-state=open]>svg]:rotate-180"
    >
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
