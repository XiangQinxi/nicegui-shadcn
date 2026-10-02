<template>
  <RadioGroupRoot
    :model-value="modelValue"
    :orientation="orientation"
    :disabled="disabled"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-for="option in options" :key="option.value" class="flex items-center gap-2">
      <RadioGroupItem
        :id="groupName + '-' + option.value"
        :value="option.value"
        :disabled="option.disabled"
        class="aspect-square size-4 shrink-0 cursor-pointer rounded-full border border-input text-primary shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:border-primary dark:bg-input/30"
      >
        <RadioGroupIndicator class="relative flex items-center justify-center">
          <svg
            class="size-2 fill-primary"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
          </svg>
        </RadioGroupIndicator>
      </RadioGroupItem>
      <label :for="groupName + '-' + option.value" class="cursor-pointer text-sm leading-none select-none">
        {{ option.label }}
      </label>
    </div>
  </RadioGroupRoot>
</template>

<script>
import { RadioGroupIndicator, RadioGroupItem, RadioGroupRoot } from 'reka-ui';

export default {
  name: 'ShadcnRadioGroup',
  components: { RadioGroupIndicator, RadioGroupItem, RadioGroupRoot },
  props: {
    // Declared so that NiceGUI's `loopback` prop does not fall through into the DOM as an
    // attribute; it only tells the client whether to echo the value back locally.
    loopback: { type: [Boolean, String], default: undefined },
    id: { type: String, default: 'shadcn-radio' },
    modelValue: { type: String, default: undefined },
    options: { type: Array, default: () => [] },
    orientation: { type: String, default: 'vertical' },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  computed: {
    groupName() {
      return this.id || 'shadcn-radio';
    },
  },
};
</script>
