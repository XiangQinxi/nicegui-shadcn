<template>
  <HoverCardPortal>
    <HoverCardContent
      v-bind="$attrs"
      data-shadcn_hover_card_content
      :side="side"
      :align="align"
      :side-offset="4"
      class="z-50 w-64 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95"
    >
      <slot />
    </HoverCardContent>
  </HoverCardPortal>
</template>

<script>
import { HoverCardContent, HoverCardPortal } from 'reka-ui';

export default {
  name: 'ShadcnHoverCardContent',
  components: { HoverCardContent, HoverCardPortal },
  inheritAttrs: false,
  props: {
    side: { type: String, default: 'bottom' },
    align: { type: String, default: 'center' },
  },
};
</script>
