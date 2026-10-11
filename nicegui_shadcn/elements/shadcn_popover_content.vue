<template>
  <PopoverPortal>
    <PopoverContent
      v-bind="$attrs"
      data-shadcn_popover_content
      :side="side"
      :align="align"
      :side-offset="4"
    >
      <slot />
    </PopoverContent>
  </PopoverPortal>
</template>

<script>
import { PopoverContent, PopoverPortal } from 'reka-ui';

export default {
  name: 'ShadcnPopoverContent',
  components: { PopoverContent, PopoverPortal },
  inheritAttrs: false,
  props: {
    side: { type: String, default: 'bottom' },
    align: { type: String, default: 'center' },
  },
};
</script>
