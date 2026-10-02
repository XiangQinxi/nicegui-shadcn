<template>
  <textarea
    :id="id"
    :value="currentValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :readonly="readonly"
    :rows="rows"
    @input="$emit('update:modelValue', $event.target.value)"
  ></textarea>
</template>

<script>
export default {
  name: 'ShadcnTextarea',
  props: {
    id: { type: String, default: undefined },
    modelValue: { type: [String, Number, Array], default: '' },
    placeholder: { type: String, default: null },
    disabled: { type: Boolean, default: false },
    readonly: { type: Boolean, default: false },
    rows: { type: [String, Number], default: null },
  },
  emits: ['update:modelValue'],
  computed: {
    // NiceGUI's client-side loopback (`LOOPBACK = False`) stores the emit payload as a
    // one-element array in `model-value`, so unwrap it before handing it to the DOM.
    currentValue() {
      return Array.isArray(this.modelValue) ? (this.modelValue[0] ?? '') : this.modelValue;
    },
  },
};
</script>
