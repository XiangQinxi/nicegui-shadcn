<template>
  <CollapsibleRoot
    :open="modelValue"
    :disabled="disabled"
    @update:open="$emit('update:modelValue', $event)"
  >
    <slot />
  </CollapsibleRoot>
</template>

<script>
import { provide, ref } from 'vue';
import { CollapsibleRoot } from 'reka-ui';

// reka-ui 2.10.5 assigns `contentId` too late: `CollapsibleRoot` hardcodes
// `contentId: ''` and `CollapsibleContent` fills it in during its own setup,
// by which time `CollapsibleTrigger` has already rendered — so the trigger
// always ends up with the invalid `aria-controls=""`. We keep our own context
// and let the content publish the id it really mounted with.

// CollapsibleRoot renders reka's `Primitive` (a plain <div>), so the caller's
// classes reach it through ordinary attribute fallthrough — no `inheritAttrs`
// dance, exactly like `shadcn_accordion.vue`.
export default {
  name: 'ShadcnCollapsible',
  components: { CollapsibleRoot },
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    modelValue: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  provide() {
    return { shadcnCollapsible: { contentId: ref('') } };
  },
};
</script>
