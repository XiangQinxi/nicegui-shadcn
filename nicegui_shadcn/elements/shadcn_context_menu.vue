<template>
  <ContextMenuRoot>
    <slot />
  </ContextMenuRoot>
</template>

<script>
import { ContextMenuRoot } from 'reka-ui';

export default {
  name: 'ShadcnContextMenu',
  components: { ContextMenuRoot },
  // ContextMenuRoot renders a fragment, so there is no element to receive attrs.
  inheritAttrs: false,
};
</script>
