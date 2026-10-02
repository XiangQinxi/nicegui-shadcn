<template>
  <DropdownMenuRoot>
    <DropdownMenuTrigger as-child>
      <slot />
    </DropdownMenuTrigger>
    <DropdownMenuPortal>
      <DropdownMenuContent
        :align="align"
        :side-offset="sideOffset"
        data-shadcn_dropdown_menu
        class="z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95"
      >
        <component
          :is="tagFor(item)"
          v-for="(item, index) in items"
          :key="index"
          v-bind="attrsFor(item)"
          @select="$emit('select', item.value)"
        >{{ item.label }}</component>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<script>
import {
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRoot,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from 'reka-ui';

const ITEM_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';
const DESTRUCTIVE_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive outline-none select-none focus:bg-destructive/10 focus:text-destructive data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';

export default {
  name: 'ShadcnDropdownMenu',
  components: {
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuPortal,
    DropdownMenuRoot,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  },
  // DropdownMenuRoot renders a fragment, so there is no element to receive attrs.
  inheritAttrs: false,
  props: {
    items: { type: Array, default: () => [] },
    align: { type: String, default: 'start' },
    sideOffset: { type: Number, default: 4 },
  },
  emits: ['select'],
  methods: {
    tagFor(item) {
      if (item.kind === 'label') return DropdownMenuLabel;
      if (item.kind === 'separator') return DropdownMenuSeparator;
      return DropdownMenuItem;
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
