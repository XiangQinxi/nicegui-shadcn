<template>
  <TooltipProvider :delay-duration="delay">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          v-bind="$attrs"
          :side="side"
          :side-offset="6"
          class="z-50 w-fit rounded-md bg-primary px-3 py-1.5 text-xs text-balance text-primary-foreground data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95"
        >
          {{ text }}
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<script>
import { TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger } from 'reka-ui';

export default {
  name: 'ShadcnTooltip',
  components: { TooltipContent, TooltipPortal, TooltipProvider, TooltipRoot, TooltipTrigger },
  // TooltipProvider renders a fragment; the caller's classes belong on the bubble.
  inheritAttrs: false,
  props: {
    text: { type: String, required: true },
    side: { type: String, default: 'top' },
    delay: { type: Number, default: 200 },
  },
};
</script>
