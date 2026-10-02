<template>
  <TabsList :orientation="orientation">
    <TabsTrigger
      v-for="tab in tabs"
      :key="tab.value"
      :value="tab.value"
      :disabled="Boolean(tab.disabled)"
      :class="triggerClasses"
    >{{ tab.label }}</TabsTrigger>
  </TabsList>
</template>

<script>
import { TabsList, TabsTrigger } from 'reka-ui';

export default {
  name: 'ShadcnTabsList',
  components: { TabsList, TabsTrigger },
  props: {
    tabs: { type: Array, default: () => [] },
    orientation: { type: String, default: 'horizontal' },
    triggerClasses: { type: String, default: '' },
  },
};
</script>
