<template>
  <DialogPortal>
    <DialogOverlay
      class="fixed inset-0 z-50 bg-black/50 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
    />
    <DialogContent
      v-bind="$attrs"
      data-shadcn_dialog_content
      :class="panelClasses"
      class="fixed z-50 flex flex-col gap-4 border bg-background shadow-lg data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
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

const PANELS = {
  center: 'top-1/2 left-1/2 w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl p-6 sm:max-w-lg',
  right: 'inset-y-0 right-0 h-full w-3/4 p-6 sm:max-w-sm sm:data-[state=closed]:slide-out-to-right sm:data-[state=open]:slide-in-from-right',
  left: 'inset-y-0 left-0 h-full w-3/4 p-6 sm:max-w-sm sm:data-[state=closed]:slide-out-to-left sm:data-[state=open]:slide-in-from-left',
  top: 'inset-x-0 top-0 h-auto p-6 data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top',
  bottom: 'inset-x-0 bottom-0 h-auto p-6 data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom',
};

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
  computed: {
    panelClasses() {
      return PANELS[this.side] || PANELS.center;
    },
  },
};
</script>
