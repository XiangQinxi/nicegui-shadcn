<template>
  <ContextMenuTrigger :as="as" :as-child="asChild">
    <slot />
  </ContextMenuTrigger>
</template>

<script>
import { ContextMenuTrigger } from 'reka-ui';

export default {
  name: 'ShadcnContextMenuTrigger',
  components: { ContextMenuTrigger },
  props: {
    as: { type: String, default: 'div' },
    asChild: { type: Boolean, default: false },
  },
};
</script>
