<template>
  <PopoverTrigger :as-child="asChild">
    <slot />
  </PopoverTrigger>
</template>

<script>
import { PopoverTrigger } from 'reka-ui';

export default {
  name: 'ShadcnPopoverTrigger',
  components: { PopoverTrigger },
  props: {
    asChild: { type: Boolean, default: false },
  },
};
</script>
