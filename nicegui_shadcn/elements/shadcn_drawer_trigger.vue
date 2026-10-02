<template>
  <DrawerTrigger :as-child="asChild">
    <slot />
  </DrawerTrigger>
</template>

<script>
import { DrawerTrigger } from 'reka-ui';

export default {
  name: 'ShadcnDrawerTrigger',
  components: { DrawerTrigger },
  props: {
    asChild: { type: Boolean, default: false },
  },
};
</script>
