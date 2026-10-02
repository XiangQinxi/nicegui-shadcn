<template>
  <ToastProvider :duration="duration" :swipe-direction="swipeDirection">
    <slot />
    <ToastViewport :class="viewportClasses" />
  </ToastProvider>
</template>

<script>
import { ToastProvider, ToastViewport } from 'reka-ui';

// ToastRoot teleports itself into whichever ToastViewport is registered on the
// provider context, so the viewport only has to be a positioned container --
// the toasts themselves can be declared anywhere inside the provider's slot.
const POSITIONS = {
  'top-left': 'top-0 left-0 flex-col',
  'top-center': 'top-0 left-1/2 -translate-x-1/2 flex-col',
  'top-right': 'top-0 right-0 flex-col',
  'bottom-left': 'bottom-0 left-0 flex-col-reverse',
  'bottom-center': 'bottom-0 left-1/2 -translate-x-1/2 flex-col-reverse',
  'bottom-right': 'bottom-0 right-0 flex-col-reverse',
};

export default {
  name: 'ShadcnToastProvider',
  components: { ToastProvider, ToastViewport },
  inheritAttrs: false,
  props: {
    duration: { type: Number, default: 5000 },
    swipeDirection: { type: String, default: 'right' },
    position: { type: String, default: 'bottom-right' },
  },
  computed: {
    viewportClasses() {
      const placement = POSITIONS[this.position] || POSITIONS['bottom-right'];
      return `fixed z-50 flex max-h-screen w-[380px] max-w-[calc(100vw-2rem)] list-none gap-2 p-4 outline-none ${placement}`;
    },
  },
};
</script>
