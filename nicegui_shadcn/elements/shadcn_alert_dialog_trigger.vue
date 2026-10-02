<template>
  <AlertDialogTrigger :as-child="asChild">
    <slot />
  </AlertDialogTrigger>
</template>

<script>
import { AlertDialogTrigger } from 'reka-ui';

export default {
  name: 'ShadcnAlertDialogTrigger',
  components: { AlertDialogTrigger },
  props: {
    asChild: { type: Boolean, default: false },
  },
};
</script>
