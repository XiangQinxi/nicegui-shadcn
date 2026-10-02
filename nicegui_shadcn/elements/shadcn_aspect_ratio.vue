<template>
  <AspectRatio :ratio="ratio">
    <slot />
  </AspectRatio>
</template>

<script>
import { AspectRatio } from 'reka-ui';

// reka-ui ships this one, so the ratio is enforced with the same `padding-bottom`
// technique Radix uses rather than the newer `aspect-ratio` property — which
// means it works in every browser NiceGUI supports.
export default {
  name: 'ShadcnAspectRatio',
  components: { AspectRatio },
  props: {
    ratio: { type: Number, default: 1 },
  },
};
</script>
