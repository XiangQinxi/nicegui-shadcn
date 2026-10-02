<template>
  <AlertDialogPortal>
    <AlertDialogOverlay
      class="fixed inset-0 z-50 bg-black/50 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
    />
    <AlertDialogContent
      v-bind="$attrs"
      data-shadcn_alert_dialog_content
      class="fixed top-1/2 left-1/2 z-50 grid w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl border bg-background p-6 shadow-lg data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 sm:max-w-lg"
    >
      <div class="flex flex-col gap-2">
        <AlertDialogTitle :class="title ? 'text-lg leading-none font-semibold' : 'sr-only'">
          {{ title || ariaLabel }}
        </AlertDialogTitle>
        <AlertDialogDescription v-if="description" class="text-sm text-muted-foreground">
          {{ description }}
        </AlertDialogDescription>
      </div>
      <slot />
    </AlertDialogContent>
  </AlertDialogPortal>
</template>

<script>
import {
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogOverlay,
  AlertDialogPortal,
  AlertDialogTitle,
} from 'reka-ui';

// Deliberately no close button: an alert dialog interrupts the user for a
// decision, so it offers only the actions and cannot be dismissed by a stray
// click. reka enforces that by always rendering it modal.
export default {
  name: 'ShadcnAlertDialogContent',
  components: {
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogOverlay,
    AlertDialogPortal,
    AlertDialogTitle,
  },
  inheritAttrs: false,
  props: {
    title: { type: String, default: '' },
    description: { type: String, default: '' },
    ariaLabel: { type: String, default: 'Alert' },
  },
};
</script>
