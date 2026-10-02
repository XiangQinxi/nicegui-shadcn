<template>
  <div>
    <div class="flex h-9 items-center gap-2 border-b px-3">
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
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
      </svg>
      <input
        ref="search"
        type="text"
        role="combobox"
        autocomplete="off"
        autocorrect="off"
        spellcheck="false"
        aria-autocomplete="list"
        :aria-expanded="true"
        :aria-controls="listId"
        :aria-activedescendant="activeDescendant"
        :aria-label="ariaLabel"
        :value="search"
        :placeholder="placeholder"
        :disabled="disabled"
        class="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
        @input="onInput"
        @keydown="onKeydown"
      >
    </div>
    <div
      :id="listId"
      role="listbox"
      :aria-label="ariaLabel"
      class="max-h-[300px] scroll-py-1 overflow-x-hidden overflow-y-auto"
    >
      <div v-if="selectable.length === 0" class="py-6 text-center text-sm">{{ emptyText }}</div>
      <div
        v-for="(group, groupIndex) in groups"
        :key="groupIndex"
        role="presentation"
        class="overflow-hidden p-1 text-foreground"
      >
        <div v-if="group.title" class="px-2 py-1.5 text-xs font-medium text-muted-foreground">
          {{ group.title }}
        </div>
        <div v-if="group.separator" class="-mx-1 my-1 h-px bg-border"></div>
        <div
          v-for="entry in group.entries"
          :key="entry.item.value"
          :id="optionId(entry.index)"
          role="option"
          :aria-selected="entry.index === activeIndex"
          :aria-disabled="entry.item.disabled ? 'true' : undefined"
          :data-selected="entry.index === activeIndex ? 'true' : undefined"
          :data-disabled="entry.item.disabled ? 'true' : undefined"
          :class="itemClass"
          @click="choose(entry)"
          @mousemove="activate(entry.index)"
        >
          <span class="truncate">{{ entry.item.label }}</span>
          <span
            v-if="entry.item.shortcut"
            class="ml-auto text-xs tracking-widest text-muted-foreground"
          >{{ entry.item.shortcut }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const ITEM_CLASS = 'relative flex cursor-default items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none select-none data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground';

let uidCounter = 0;

export default {
  name: 'ShadcnCommand',
  props: {
    // `LOOPBACK = False` on the Python side means NiceGUI replaces this with the
    // emit payload array, so it is normalised by `currentValue` below.
    modelValue: { type: [String, Array], default: '' },
    items: { type: Array, default: () => [] },
    placeholder: { type: String, default: 'Type a command or search...' },
    emptyText: { type: String, default: 'No results found.' },
    ariaLabel: { type: String, default: 'Command menu' },
    // Filter the items on the client as the user types. Turn it off to filter on
    // the server and listen to the `search` event instead.
    filter: { type: Boolean, default: true },
    disabled: { type: Boolean, default: false },
    autofocus: { type: Boolean, default: false },
    // Consumed so that NiceGUI's ValueElement internal does not fall through
    // onto the root element as a stray DOM attribute.
    loopback: { type: [Boolean, String], default: undefined },
  },
  emits: ['update:modelValue', 'select', 'search'],
  data() {
    return {
      uid: `shadcn-command-${++uidCounter}`,
      search: '',
      activeIndex: 0,
      itemClass: ITEM_CLASS,
    };
  },
  computed: {
    currentValue() {
      const value = this.modelValue;
      return Array.isArray(value) ? (value[0] ?? '') : (value ?? '');
    },
    listId() {
      return `${this.uid}-list`;
    },
    activeDescendant() {
      return this.selectable.length ? this.optionId(this.activeIndex) : undefined;
    },
    visible() {
      const items = Array.isArray(this.items) ? this.items : [];
      const query = this.filter ? this.search.trim().toLowerCase() : '';
      const out = [];
      for (const item of items) {
        if (item.kind === 'separator') {
          if (!query) out.push(item);
          continue;
        }
        if (!query) {
          out.push(item);
          continue;
        }
        const keywords = Array.isArray(item.keywords) ? item.keywords : [];
        const haystack = [item.label, item.value].concat(keywords).join(' ').toLowerCase();
        if (haystack.includes(query)) out.push(item);
      }
      return out;
    },
    selectable() {
      return this.visible.filter((item) => item.kind !== 'separator');
    },
    groups() {
      const groups = [];
      let index = 0;
      for (const item of this.visible) {
        if (item.kind === 'separator') {
          groups.push({ title: '', separator: true, entries: [] });
          continue;
        }
        const title = item.group || '';
        let group = groups.length ? groups[groups.length - 1] : null;
        if (!group || group.separator || group.title !== title) {
          group = { title, entries: [] };
          groups.push(group);
        }
        group.entries.push({ item, index });
        index += 1;
      }
      return groups;
    },
  },
  watch: {
    selectable() {
      const count = this.selectable.length;
      if (count === 0) this.activeIndex = 0;
      else if (this.activeIndex > count - 1) this.activeIndex = count - 1;
    },
  },
  mounted() {
    if (this.autofocus) this.$refs.search.focus();
  },
  methods: {
    optionId(index) {
      return `${this.uid}-option-${index}`;
    },
    onInput(event) {
      this.search = event.target.value;
      this.activeIndex = 0;
      this.$emit('search', this.search);
    },
    onKeydown(event) {
      const count = this.selectable.length;
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.move(1);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.move(-1);
      } else if (event.key === 'Home') {
        event.preventDefault();
        this.activate(0);
      } else if (event.key === 'End') {
        event.preventDefault();
        this.activate(count - 1);
      } else if (event.key === 'Enter') {
        event.preventDefault();
        if (count) this.choose({ item: this.selectable[this.activeIndex] });
      } else if (event.key === 'Escape') {
        this.search = '';
        this.activeIndex = 0;
      }
    },
    move(delta) {
      const count = this.selectable.length;
      if (!count) return;
      let index = this.activeIndex;
      for (let step = 0; step < count; step += 1) {
        index = (index + delta + count) % count;
        if (!this.selectable[index].disabled) break;
      }
      this.activate(index);
    },
    activate(index) {
      const count = this.selectable.length;
      if (!count) return;
      this.activeIndex = Math.min(Math.max(index, 0), count - 1);
      const option = document.getElementById(this.optionId(this.activeIndex));
      if (option && option.scrollIntoView) option.scrollIntoView({ block: 'nearest' });
    },
    choose(entry) {
      if (!entry || !entry.item || entry.item.disabled) return;
      this.$emit('update:modelValue', entry.item.value);
      this.$emit('select', entry.item.value);
    },
  },
};
</script>
