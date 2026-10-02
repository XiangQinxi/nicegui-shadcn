<template>
  <ScrollAreaRoot
    :type="type"
    :scroll-hide-delay="scrollHideDelay"
    class="relative overflow-hidden"
  >
    <ScrollAreaViewport class="size-full rounded-[inherit] outline-none">
      <slot />
    </ScrollAreaViewport>
    <ScrollAreaScrollbar
      orientation="vertical"
      class="flex w-2.5 touch-none p-px select-none transition-colors duration-150"
    >
      <ScrollAreaThumb class="relative flex-1 rounded-full bg-border" />
    </ScrollAreaScrollbar>
    <ScrollAreaScrollbar
      orientation="horizontal"
      class="flex h-2.5 touch-none flex-col p-px select-none transition-colors duration-150"
    >
      <ScrollAreaThumb class="relative flex-1 rounded-full bg-border" />
    </ScrollAreaScrollbar>
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>

<script>
import {
  ScrollAreaCorner,
  ScrollAreaRoot,
  ScrollAreaScrollbar,
  ScrollAreaThumb,
  ScrollAreaViewport,
} from 'reka-ui';

// The whole structure lives in one template because the parts only work as
// siblings under the root: the viewport has to be the scrolling box and the
// scrollbars have to be its siblings, not its children. Nesting the caller's
// elements would break that, so everything the user adds goes into the viewport.
export default {
  name: 'ShadcnScrollArea',
  components: { ScrollAreaCorner, ScrollAreaRoot, ScrollAreaScrollbar, ScrollAreaThumb, ScrollAreaViewport },
  props: {
    type: { type: String, default: 'hover' },
    scrollHideDelay: { type: Number, default: 600 },
  },
};
</script>
