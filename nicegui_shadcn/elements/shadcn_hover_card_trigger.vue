<template>
  <HoverCardTrigger :as-child="asChild">
    <slot />
  </HoverCardTrigger>
</template>

<script>
import { HoverCardTrigger } from 'reka-ui';

export default {
  name: 'ShadcnHoverCardTrigger',
  components: { HoverCardTrigger },
  // A hover card almost always hangs off an element the caller already has --
  // a link or a button -- so the default is to hand the trigger's attributes to
  // that element rather than to wrap it in an anchor of our own.
  props: {
    asChild: { type: Boolean, default: true },
  },
};
</script>
