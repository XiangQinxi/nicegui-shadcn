<template>
  <CollapsibleTrigger :as-child="asChild" :aria-controls="contentId || null">
    <slot />
  </CollapsibleTrigger>
</template>

<script>
import { inject, ref } from 'vue';
import { CollapsibleTrigger } from 'reka-ui';

// `disabled` is deliberately not forwarded: reka reads it from the root's
// context, and any `disabled` we bound ourselves would land in `$attrs` and
// clobber that value with our default `false`.
export default {
  name: 'ShadcnCollapsibleTrigger',
  components: { CollapsibleTrigger },
  props: {
    asChild: { type: Boolean, default: false },
  },
  setup() {
    // See `shadcn_collapsible.vue`: reka hands us an empty `aria-controls`,
    // so we point it at the panel this collapsible actually rendered.
    const context = inject('shadcnCollapsible', null);
    return { contentId: context ? context.contentId : ref('') };
  },
};
</script>
