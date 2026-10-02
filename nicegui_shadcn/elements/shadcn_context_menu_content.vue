<template>
  <ContextMenuPortal>
    <ContextMenuContent
      data-shadcn_context_menu
      class="z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95"
    >
      <component
        :is="tagFor(item)"
        v-for="(item, index) in items"
        :key="index"
        v-bind="attrsFor(item)"
        @select="$emit('select', item.value)"
      >{{ item.label }}</component>
    </ContextMenuContent>
  </ContextMenuPortal>
</template>

<script>
import {
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuPortal,
  ContextMenuSeparator,
} from 'reka-ui';

const ITEM_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';
const DESTRUCTIVE_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive outline-none select-none focus:bg-destructive/10 focus:text-destructive data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';

export default {
  name: 'ShadcnContextMenuContent',
  components: { ContextMenuContent, ContextMenuItem, ContextMenuLabel, ContextMenuPortal, ContextMenuSeparator },
  // The panel lives in a portal, so the caller's classes have to be forwarded
  // explicitly -- there is no element on the component root to catch them.
  inheritAttrs: false,
  props: {
    items: { type: Array, default: () => [] },
  },
  emits: ['select'],
  methods: {
    tagFor(item) {
      if (item.kind === 'label') return ContextMenuLabel;
      if (item.kind === 'separator') return ContextMenuSeparator;
      return ContextMenuItem;
    },
    attrsFor(item) {
      if (item.kind === 'label') return { class: 'px-2 py-1.5 text-xs font-medium text-muted-foreground' };
      if (item.kind === 'separator') return { class: '-mx-1 my-1 h-px bg-border' };
      return {
        class: item.variant === 'destructive' ? DESTRUCTIVE_CLASS : ITEM_CLASS,
        disabled: Boolean(item.disabled),
      };
    },
  },
};
</script>
