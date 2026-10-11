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
