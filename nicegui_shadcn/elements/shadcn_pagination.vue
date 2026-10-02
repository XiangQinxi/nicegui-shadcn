<template>
  <nav role="navigation" aria-label="Pagination" class="mx-auto flex w-full justify-center">
    <ul class="flex flex-row flex-wrap items-center gap-1">
      <li>
        <button
          type="button"
          data-shadcn_pagination_previous
          aria-label="Go to previous page"
          :disabled="safePage <= 1"
          :class="LINK_CLASS"
          @click="go(safePage - 1)"
        >
          <svg
            class="size-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
          ><path d="m15 18-6-6 6-6" /></svg>
          <span class="sr-only">Previous</span>
        </button>
      </li>
      <li v-for="(item, index) in items" :key="`${item}-${index}`">
        <span v-if="item === 'ellipsis'" aria-hidden="true" :class="ELLIPSIS_CLASS">
          <svg
            class="size-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          ><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /><circle cx="5" cy="12" r="1" /></svg>
          <span class="sr-only">More pages</span>
        </span>
        <button
          v-else
          type="button"
          :aria-label="`Go to page ${item}`"
          :aria-current="item === safePage ? 'page' : undefined"
          :class="item === safePage ? `${LINK_CLASS} ${ACTIVE_CLASS}` : LINK_CLASS"
          @click="go(item)"
        >{{ item }}</button>
      </li>
      <li>
        <button
          type="button"
          data-shadcn_pagination_next
          aria-label="Go to next page"
          :disabled="safePage >= safeTotal"
          :class="LINK_CLASS"
          @click="go(safePage + 1)"
        >
          <span class="sr-only">Next</span>
          <svg
            class="size-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
          ><path d="m9 18 6-6-6-6" /></svg>
        </button>
      </li>
    </ul>
  </nav>
</template>

<script>
const LINK_CLASS = 'inline-flex size-9 items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50';
const ACTIVE_CLASS = 'border bg-background shadow-xs';
const ELLIPSIS_CLASS = 'flex size-9 items-center justify-center';

export default {
  name: 'ShadcnPagination',
  props: {
    modelValue: { type: Number, default: 1 },
    total: { type: Number, default: 1 },
    siblings: { type: Number, default: 1 },
  },
  emits: ['update:modelValue'],
  data() {
    return { LINK_CLASS, ACTIVE_CLASS, ELLIPSIS_CLASS };
  },
  computed: {
    safeTotal() {
      return Math.max(1, Number(this.total) || 1);
    },
    safePage() {
      return Math.min(Math.max(1, Number(this.modelValue) || 1), this.safeTotal);
    },
    /**
     * The page numbers to render, with `'ellipsis'` placeholders where pages
     * were skipped. While the whole range fits it is simply 1..total.
     */
    items() {
      const total = this.safeTotal;
      const current = this.safePage;
      const window = Math.max(0, Number(this.siblings) || 0);
      if (total <= window * 2 + 5) {
        return Array.from({ length: total }, (_, index) => index + 1);
      }
      const left = Math.max(current - window, 2);
      const right = Math.min(current + window, total - 1);
      const items = [1];
      if (left > 2) items.push('ellipsis');
      for (let page = left; page <= right; page += 1) items.push(page);
      if (right < total - 1) items.push('ellipsis');
      items.push(total);
      return items;
    },
  },
  methods: {
    go(page) {
      if (page < 1 || page > this.safeTotal || page === this.safePage) return;
      this.$emit('update:modelValue', page);
    },
  },
};
</script>
