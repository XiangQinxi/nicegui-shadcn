<template>
  <DrawerPortal>
    <DrawerOverlay
      class="fixed inset-0 z-50 bg-black/50 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0"
    />
    <DrawerContent
      v-bind="$attrs"
      data-shadcn_drawer_content
      :class="panelClasses"
      class="fixed z-50 flex flex-col gap-4 bg-background shadow-lg transition ease-in-out data-[state=closed]:animate-out data-[state=closed]:duration-300 data-[state=open]:animate-in data-[state=open]:duration-500"
    >
      <DrawerHandle
        v-if="side === 'bottom' || side === 'top'"
        class="shrink-0 rounded-full bg-muted"
        :class="side === 'bottom' ? 'mx-auto mt-4 h-2 w-24' : 'mx-auto mb-4 h-2 w-24'"
      />
      <div :class="side === 'bottom' || side === 'top' ? 'flex flex-col gap-2 px-4 pb-4' : 'flex flex-col gap-2 p-6'">
        <DrawerTitle :class="title ? 'text-lg font-semibold text-foreground' : 'sr-only'">
          {{ title || ariaLabel }}
        </DrawerTitle>
        <DrawerDescription v-if="description" class="text-sm text-muted-foreground">
          {{ description }}
        </DrawerDescription>
        <slot />
      </div>
      <DrawerClose
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
      </DrawerClose>
    </DrawerContent>
  </DrawerPortal>
</template>

<script>
import {
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHandle,
  DrawerOverlay,
  DrawerPortal,
  DrawerTitle,
} from 'reka-ui';

const PANELS = {
  bottom: 'inset-x-0 bottom-0 max-h-[80vh] rounded-t-xl border-t',
  top: 'inset-x-0 top-0 max-h-[80vh] rounded-b-xl border-b',
  right: 'inset-y-0 right-0 h-full w-3/4 border-l sm:max-w-sm',
  left: 'inset-y-0 left-0 h-full w-3/4 border-r sm:max-w-sm',
};

export default {
  name: 'ShadcnDrawerContent',
  components: { DrawerClose, DrawerContent, DrawerDescription, DrawerHandle, DrawerOverlay, DrawerPortal, DrawerTitle },
  inheritAttrs: false,
  props: {
    title: { type: String, default: '' },
    description: { type: String, default: '' },
    ariaLabel: { type: String, default: 'Drawer' },
    side: { type: String, default: 'bottom' },
    closable: { type: Boolean, default: true },
  },
  computed: {
    panelClasses() {
      return PANELS[this.side] || PANELS.bottom;
    },
  },
};
</script>
