<template>
  <NavigationMenuRoot v-bind="$attrs">
    <NavigationMenuList class="group flex flex-1 list-none items-center justify-center gap-1">
      <NavigationMenuItem v-for="(item, index) in items" :key="index" :value="item.value">
        <NavigationMenuLink v-if="isLink(item)" :href="item.href" :active="item.active" :class="LINK_CLASS" @select="pick(item)">{{ item.label }}</NavigationMenuLink>
        <NavigationMenuTrigger v-else :disabled="item.disabled" :class="TRIGGER_CLASS">
          {{ item.label }}
          <span class="contents" v-html="CHEVRON"></span>
        </NavigationMenuTrigger>
        <NavigationMenuContent v-if="!isLink(item)">
          <ul class="grid w-max grid-cols-1 gap-1 p-2">
            <li v-for="(child, childIndex) in item.items" :key="childIndex">
              <NavigationMenuLink :href="child.href" :class="CHILD_CLASS" @select="pick(child)">
                <span class="block text-sm font-medium leading-none">{{ child.label }}</span>
                <span v-if="child.description" class="mt-1 block text-sm leading-snug text-muted-foreground">{{ child.description }}</span>
              </NavigationMenuLink>
            </li>
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
      <NavigationMenuIndicator class="top-full z-50 flex h-2 items-end justify-center overflow-hidden">
        <span class="relative top-px h-1.5 w-2 rounded-full bg-primary"></span>
      </NavigationMenuIndicator>
    </NavigationMenuList>
    <NavigationMenuViewport class="absolute left-0 top-full z-50 flex w-max justify-center" />
  </NavigationMenuRoot>
</template>

<script>
import {
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuRoot,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from 'reka-ui';

/* Row-level classes for the repeated, data-driven entries.  The component's own
 * root classes live in Python (`_NAVIGATION_MENU_CLASSES`) so that they can be
 * displaced by `classes=`; these cannot, exactly like `ITEM_CLASS` in
 * `shadcn_dropdown_menu.vue`. */
const TRIGGER_CLASS = 'inline-flex h-9 w-max items-center justify-center gap-1 rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:bg-accent focus-visible:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0 [&[data-state=open]>svg]:rotate-180';
const LINK_CLASS = 'inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:bg-accent focus-visible:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring';
const CHILD_CLASS = 'block rounded-md p-2 leading-none no-underline transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:bg-accent focus-visible:text-accent-foreground focus-visible:outline-none';
const CHEVRON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"></path></svg>';

export default {
  name: 'ShadcnNavigationMenu',
  components: {
    NavigationMenuContent,
    NavigationMenuIndicator,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuRoot,
    NavigationMenuTrigger,
    NavigationMenuViewport,
  },
  /* ``NavigationMenuRoot`` renders ``CollectionSlot > Primitive`` — the root of
   * the fragment chain is not a real element, so VBuild's ``data-…`` marker has
   * to be forwarded onto the ``<nav>`` that ``Primitive`` finally renders. */
  inheritAttrs: false,
  props: {
    items: { type: Array, default: () => [] },
    modelValue: { type: String, default: undefined },
  },
  emits: ['select', 'update:modelValue'],
  data() {
    return { CHEVRON, TRIGGER_CLASS, LINK_CLASS, CHILD_CLASS };
  },
  methods: {
    isLink(item) {
      const children = (item && item.items) || [];
      return children.length === 0;
    },
    pick(item) {
      this.$emit('select', item.value);
    },
  },
};
</script>
