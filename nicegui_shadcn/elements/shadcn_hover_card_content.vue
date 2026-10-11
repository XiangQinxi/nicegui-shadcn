<template>
  <HoverCardPortal>
    <HoverCardContent
      v-bind="$attrs"
      data-shadcn_hover_card_content
      :side="side"
      :align="align"
      :side-offset="4"
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
