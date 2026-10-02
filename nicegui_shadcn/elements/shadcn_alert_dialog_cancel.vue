<template>
  <AlertDialogCancel>
    <slot />
  </AlertDialogCancel>
</template>

<script>
import { AlertDialogCancel } from 'reka-ui';

// Like `AlertDialogAction`, but the conventional "get me out of here" button.
export default {
  name: 'ShadcnAlertDialogCancel',
  components: { AlertDialogCancel },
};
</script>
