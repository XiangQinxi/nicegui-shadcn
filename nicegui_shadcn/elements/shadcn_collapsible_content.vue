<template>
  <CollapsibleContent ref="content" force-mount v-bind="$attrs">
    <slot />
  </CollapsibleContent>
</template>

<script>
import { inject, onMounted, ref } from 'vue';
import { CollapsibleContent } from 'reka-ui';

// `force-mount` keeps the panel in the DOM so that elements created later on the
// server always have somewhere to land; reka then only sets `data-state`, so the
// hiding is done by the `data-[state=closed]:hidden` class the Python element
// contributes (see `_COLLAPSIBLE_CONTENT_CLASSES`).
export default {
  name: 'ShadcnCollapsibleContent',
  components: { CollapsibleContent },
  inheritAttrs: false,
  setup() {
    const context = inject('shadcnCollapsible', null);
    const content = ref(null);
    onMounted(() => {
      // Publish the id reka actually rendered with, so the trigger's
      // `aria-controls` points at a real element.
      const element = content.value?.$el ?? content.value;
      if (context && element?.id) context.contentId.value = element.id;
    });
    return { content };
  },
};
</script>
