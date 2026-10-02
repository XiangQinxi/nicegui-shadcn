<template>
  <div
    v-bind="$attrs"
    class="relative flex items-center gap-2 has-disabled:opacity-50"
  >
    <!--
      One invisible native input carries the whole value. Letting the browser own
      the text field buys us real key handling, paste, autofill, the mobile
      keyboard and `autocomplete="one-time-code"` for free; the slots below are
      pure presentation driven by `modelValue`.
    -->
    <input
      ref="input"
      class="absolute inset-0 z-20 h-full w-full cursor-text bg-transparent opacity-0 outline-none disabled:cursor-not-allowed"
      type="text"
      :inputmode="inputmode"
      autocomplete="one-time-code"
      autocorrect="off"
      spellcheck="false"
      :disabled="disabled"
      :aria-label="ariaLabel"
      :maxlength="length"
      :value="currentValue"
      @input="onInput"
      @focus="focused = true"
      @blur="focused = false"
    />
    <div
      v-for="(group, groupIndex) in resolvedGroups"
      :key="groupIndex"
      class="flex items-center gap-2"
    >
      <div
        v-if="groupIndex > 0"
        class="flex items-center"
        data-slot="input-otp-separator"
        role="separator"
        aria-hidden="true"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="size-4"
        >
          <path d="M5 12h14" />
        </svg>
      </div>
      <div class="flex items-center">
        <div
          v-for="index in group"
          :key="index"
          class="relative flex size-9 items-center justify-center border-y border-r border-input text-sm shadow-xs transition-all outline-none first:rounded-l-md first:border-l last:rounded-r-md data-[active=true]:z-10 data-[active=true]:border-ring data-[active=true]:ring-[3px] data-[active=true]:ring-ring/50"
          data-slot="input-otp-slot"
          :data-active="index === activeIndex"
        >
          <span v-if="displayChar(index)">{{ displayChar(index) }}</span>
          <div
            v-if="index === activeIndex"
            class="pointer-events-none absolute inset-0 flex items-center justify-center"
          >
            <div class="animate-caret-blink h-4 w-px bg-foreground duration-1000" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShadcnInputOtp',
  inheritAttrs: false,
  props: {
    modelValue: { type: [String, Array], default: '' },
    // How many characters the field accepts in total.
    length: { type: Number, default: 6 },
    // Optional run lengths, e.g. [3, 3]. Anything that does not add up to
    // `length` is ignored and the field is rendered as a single run.
    groups: { type: Array, default: () => [] },
    // Per-character regular expression source, e.g. '^\\d+$'. Empty accepts
    // every character.
    pattern: { type: String, default: '' },
    masked: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    inputmode: { type: String, default: 'numeric' },
    ariaLabel: { type: String, default: 'One-time password' },
    // Consumed so that NiceGUI's ValueElement internal does not fall through
    // onto the root element as a stray DOM attribute.
    loopback: { type: [Boolean, String], default: undefined },
  },
  emits: ['update:modelValue'],
  data() {
    return { focused: false };
  },
  computed: {
    // NiceGUI's client-side loopback (`LOOPBACK = False`) stores the emit payload as a
    // one-element array in `model-value`; every read goes through this normalised view.
    currentValue() {
      const value = this.modelValue;
      return Array.isArray(value) ? (value[0] ?? '') : (value ?? '');
    },
    resolvedGroups() {
      const sizes = (Array.isArray(this.groups) ? this.groups : [])
        .map((size) => Number(size))
        .filter((size) => Number.isInteger(size) && size > 0);
      const total = sizes.reduce((sum, size) => sum + size, 0);
      if (sizes.length === 0 || total !== this.length) {
        return [Array.from({ length: this.length }, (_, index) => index)];
      }
      const runs = [];
      let cursor = 0;
      for (const size of sizes) {
        runs.push(Array.from({ length: size }, (_, offset) => cursor + offset));
        cursor += size;
      }
      return runs;
    },
    activeIndex() {
      if (!this.focused || this.disabled) return -1;
      return Math.min(this.currentValue.length, this.length - 1);
    },
  },
  watch: {
    modelValue() {
      this.syncInput();
    },
  },
  mounted() {
    this.syncInput();
  },
  methods: {
    displayChar(index) {
      const char = this.currentValue[index];
      if (!char) return '';
      return this.masked ? '\u2022' : char;
    },
    filterValue(raw) {
      const regex = this.pattern ? new RegExp(this.pattern) : null;
      let out = '';
      for (const char of String(raw)) {
        if (out.length >= this.length) break;
        if (regex && !regex.test(char)) continue;
        out += char;
      }
      return out;
    },
    onInput(event) {
      const next = this.filterValue(event.target.value);
      // Keep the DOM and the model in step even when we rejected characters:
      // the prop only comes back after NiceGUI's local loopback round trip.
      if (event.target.value !== next) event.target.value = next;
      if (next !== this.currentValue) this.$emit('update:modelValue', next);
    },
    syncInput() {
      const input = this.$refs.input;
      if (input && input.value !== this.currentValue) input.value = this.currentValue;
    },
  },
};
</script>
