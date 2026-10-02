<template>
  <TabsContent :value="value" force-mount>
    <slot />
  </TabsContent>
</template>

<script>
import { TabsContent } from 'reka-ui';

export default {
  name: 'ShadcnTabsContent',
  components: { TabsContent },
  props: {
    value: { type: [String, Number], required: true },
  },
};
</script>
