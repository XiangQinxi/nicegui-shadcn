<template>
  <MenubarRoot>
    <MenubarMenu v-for="(menu, menuIndex) in menus" :key="menuIndex" :value="menu.value">
      <MenubarTrigger class="flex cursor-default items-center rounded-sm px-3 py-1.5 text-sm font-medium outline-none select-none focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground">
        {{ menu.label }}
      </MenubarTrigger>
      <MenubarPortal>
        <MenubarContent
          :align="align"
          :side-offset="sideOffset"
          class="z-50 min-w-[12rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95"
        >
          <component
            :is="tagFor(item)"
            v-for="(item, index) in menu.items"
            :key="index"
            v-bind="attrsFor(item)"
            @select="$emit('select', item.value)"
          >{{ item.label }}</component>
        </MenubarContent>
      </MenubarPortal>
    </MenubarMenu>
  </MenubarRoot>
</template>

<script>
import {
  MenubarContent,
  MenubarItem,
  MenubarLabel,
  MenubarMenu,
  MenubarPortal,
  MenubarRoot,
  MenubarSeparator,
  MenubarTrigger,
} from 'reka-ui';

const ITEM_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none select-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';
const DESTRUCTIVE_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive outline-none select-none focus:bg-destructive/10 focus:text-destructive data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0';

export default {
  name: 'ShadcnMenubar',
  components: {
    MenubarContent,
    MenubarItem,
    MenubarLabel,
    MenubarMenu,
    MenubarPortal,
    MenubarRoot,
    MenubarSeparator,
    MenubarTrigger,
  },
  props: {
    menus: { type: Array, default: () => [] },
    align: { type: String, default: 'start' },
    sideOffset: { type: Number, default: 8 },
  },
  emits: ['select'],
  methods: {
    tagFor(item) {
      if (item.kind === 'label') return MenubarLabel;
      if (item.kind === 'separator') return MenubarSeparator;
      return MenubarItem;
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
