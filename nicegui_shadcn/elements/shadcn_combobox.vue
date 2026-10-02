<template>
  <div>
    <button
      ref="trigger"
      type="button"
      role="combobox"
      :aria-expanded="open ? 'true' : 'false'"
      :aria-controls="listId"
      :aria-label="ariaLabel"
      :disabled="disabled"
      :data-state="open ? 'open' : 'closed'"
      :class="triggerClass"
      @click="toggle"
      @keydown.down.prevent="openPanel"
    >
      <span class="truncate">{{ selectedLabel }}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="size-4 shrink-0 opacity-50"
        aria-hidden="true"
      >
        <path d="m7 15 5 5 5-5" />
        <path d="m7 9 5-5 5 5" />
      </svg>
    </button>
    <div v-if="open" :id="listId" role="listbox" :aria-label="ariaLabel" :class="contentClass">
      <div class="flex items-center border-b px-3">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="mr-2 size-4 shrink-0 opacity-50"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          ref="search"
          type="text"
          autocomplete="off"
          autocorrect="off"
          spellcheck="false"
          :value="search"
          :placeholder="searchPlaceholder"
          class="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground"
          @input="onInput"
          @keydown="onKeydown"
        >
      </div>
      <div class="max-h-60 scroll-py-1 overflow-x-hidden overflow-y-auto p-1">
        <div v-if="filtered.length === 0" class="py-6 text-center text-sm">{{ emptyText }}</div>
        <div
          v-for="(option, index) in filtered"
          :id="optionId(index)"
          :key="option.value"
          role="option"
          :aria-selected="String(option.value) === currentValue"
          :aria-disabled="option.disabled ? 'true' : undefined"
          :data-selected="String(option.value) === currentValue ? 'true' : undefined"
          :data-disabled="option.disabled ? 'true' : undefined"
          :data-active="index === activeIndex ? 'true' : undefined"
          :class="itemClass"
          @click="choose(option)"
          @mousemove="activeIndex = index"
        >
          <svg
            v-if="String(option.value) === currentValue"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="pointer-events-none absolute right-2 size-4"
            aria-hidden="true"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
          <span class="truncate">{{ option.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const TRIGGER_CLASS = 'flex h-9 w-full items-center justify-between gap-2 rounded-md border border-input bg-transparent px-3 py-2 text-sm whitespace-nowrap shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50';
const CONTENT_CLASS = 'absolute z-50 mt-1 w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md';
const ITEM_CLASS = 'relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-none select-none data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 data-[active=true]:bg-accent data-[active=true]:text-accent-foreground data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground';

let uidCounter = 0;

export default {
  name: 'ShadcnCombobox',
  props: {
    // `LOOPBACK = False` on the Python side means NiceGUI replaces this with the
    // emit payload array, so it is normalised by `currentValue` below.
    modelValue: { type: [String, Number, Array], default: '' },
    options: { type: Array, default: () => [] },
    placeholder: { type: String, default: 'Select an option...' },
    searchPlaceholder: { type: String, default: 'Search...' },
    emptyText: { type: String, default: 'No results found.' },
    ariaLabel: { type: String, default: 'Combobox' },
    filter: { type: Boolean, default: true },
    disabled: { type: Boolean, default: false },
    // Consumed so that NiceGUI's ValueElement internal does not fall through
    // onto the root element as a stray DOM attribute.
    loopback: { type: [Boolean, String], default: undefined },
  },
  emits: ['update:modelValue', 'select'],
  data() {
    return {
      uid: `shadcn-combobox-${++uidCounter}`,
      open: false,
      search: '',
      activeIndex: 0,
      triggerClass: TRIGGER_CLASS,
      contentClass: CONTENT_CLASS,
      itemClass: ITEM_CLASS,
    };
  },
  computed: {
    currentValue() {
      const value = Array.isArray(this.modelValue) ? this.modelValue[0] : this.modelValue;
      return value === null || value === undefined ? '' : String(value);
    },
    listId() {
      return `${this.uid}-list`;
    },
    selectedLabel() {
      const options = Array.isArray(this.options) ? this.options : [];
      const found = options.find((option) => String(option.value) === this.currentValue);
      return found ? found.label : this.placeholder;
    },
    filtered() {
      const options = Array.isArray(this.options) ? this.options : [];
      const query = this.filter ? this.search.trim().toLowerCase() : '';
      if (!query) return options;
      return options.filter((option) => {
        const keywords = Array.isArray(option.keywords) ? option.keywords : [];
        return [option.label, option.value].concat(keywords).join(' ').toLowerCase().includes(query);
      });
    },
  },
  watch: {
    filtered() {
      const count = this.filtered.length;
      if (count === 0) this.activeIndex = 0;
      else if (this.activeIndex > count - 1) this.activeIndex = count - 1;
    },
  },
  mounted() {
    document.addEventListener('mousedown', this.onDocumentMousedown);
  },
  unmounted() {
    document.removeEventListener('mousedown', this.onDocumentMousedown);
  },
  methods: {
    optionId(index) {
      return `${this.uid}-option-${index}`;
    },
    onDocumentMousedown(event) {
      if (this.open && this.$el && !this.$el.contains(event.target)) this.close();
    },
    toggle() {
      if (this.disabled) return;
      if (this.open) this.close();
      else this.openPanel();
    },
    openPanel() {
      if (this.disabled) return;
      this.open = true;
      this.search = '';
      this.activeIndex = 0;
      this.$nextTick(() => {
        const input = this.$refs.search;
        if (input) input.focus();
      });
    },
    close() {
      this.open = false;
      this.search = '';
    },
    onInput(event) {
      this.search = event.target.value;
      this.activeIndex = 0;
    },
    onKeydown(event) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.move(1);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.move(-1);
      } else if (event.key === 'Enter') {
        event.preventDefault();
        this.choose(this.filtered[this.activeIndex]);
      } else if (event.key === 'Escape') {
        event.preventDefault();
        this.close();
      }
    },
    move(delta) {
      const count = this.filtered.length;
      if (!count) return;
      let index = this.activeIndex;
      for (let step = 0; step < count; step += 1) {
        index = (index + delta + count) % count;
        if (!this.filtered[index].disabled) break;
      }
      this.activeIndex = index;
      const option = document.getElementById(this.optionId(index));
      if (option && option.scrollIntoView) option.scrollIntoView({ block: 'nearest' });
    },
    choose(option) {
      if (!option || option.disabled) return;
      this.$emit('update:modelValue', option.value);
      this.$emit('select', option.value);
      this.close();
    },
  },
};
</script>
