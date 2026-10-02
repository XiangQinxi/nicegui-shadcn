<template>
  <DialogTrigger :as-child="asChild">
    <slot />
  </DialogTrigger>
</template>

<script>
import { DialogTrigger } from 'reka-ui';

export default {
  name: 'ShadcnDialogTrigger',
  components: { DialogTrigger },
  props: {
    asChild: { type: Boolean, default: false },
  },
};
</script>
