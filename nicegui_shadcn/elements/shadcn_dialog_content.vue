<template>
  <DialogPortal>
    <DialogOverlay
      class="fixed inset-0 z-50 bg-black/50 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
    />
    <!-- The panel's classes come from Python (`DialogContent.default_classes`
         plus the geometry variant); see the note in shadcn_select.vue. -->
    <DialogContent
      v-bind="$attrs"
      data-shadcn_dialog_content
    >
      <div class="flex flex-col gap-2">
        <DialogTitle :class="title ? 'text-lg leading-none font-semibold' : 'sr-only'">
          {{ title || ariaLabel }}
        </DialogTitle>
        <DialogDescription v-if="description" class="text-sm text-muted-foreground">
          {{ description }}
        </DialogDescription>
      </div>
      <slot />
      <DialogClose
        v-if="closable"
        class="absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
      >
        <svg
          class="size-4"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M18 6 6 18" />
          <path d="m6 6 12 12" />
        </svg>
        <span class="sr-only">Close</span>
      </DialogClose>
    </DialogContent>
  </DialogPortal>
</template>

<script>
import { DialogClose, DialogContent, DialogDescription, DialogOverlay, DialogPortal, DialogTitle } from 'reka-ui';

export default {
  name: 'ShadcnDialogContent',
  components: { DialogClose, DialogContent, DialogDescription, DialogOverlay, DialogPortal, DialogTitle },
  inheritAttrs: false,
  props: {
    title: { type: String, default: '' },
    description: { type: String, default: '' },
    ariaLabel: { type: String, default: 'Dialog' },
    side: { type: String, default: 'center' },
    closable: { type: Boolean, default: true },
  },
};
</script>
