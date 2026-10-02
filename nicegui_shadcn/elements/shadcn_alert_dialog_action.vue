<template>
  <AlertDialogAction>
    <slot />
  </AlertDialogAction>
</template>

<script>
import { AlertDialogAction } from 'reka-ui';

// reka renders this as a <button> wired to the dialog's close action, which is
// what makes "Delete" both run the handler and dismiss the dialog.
export default {
  name: 'ShadcnAlertDialogAction',
  components: { AlertDialogAction },
};
</script>
