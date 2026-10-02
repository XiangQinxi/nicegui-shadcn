<template>
  <CalendarRoot
    v-slot="{ grid, weekDays }"
    v-bind="$attrs"
    :model-value="selectedDate"
    :min-value="minDate"
    :max-value="maxDate"
    :week-starts-on="weekStartsOn"
    :number-of-months="numberOfMonths"
    :fixed-weeks="fixedWeeks"
    :disabled="disabled"
    :readonly="readonly"
    :locale="locale"
    :calendar-label="ariaLabel"
    class="w-fit p-3"
    @update:model-value="onSelect"
  >
    <div class="flex flex-col gap-4">
      <CalendarHeader class="relative flex w-full items-center justify-center pt-1">
        <CalendarPrev
          class="absolute left-1 inline-flex size-7 items-center justify-center rounded-md border border-input bg-transparent p-0 opacity-50 transition-opacity hover:opacity-100 disabled:pointer-events-none disabled:opacity-50"
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
            <path d="m15 18-6-6 6-6" />
          </svg>
        </CalendarPrev>
        <CalendarHeading class="text-sm font-medium" />
        <CalendarNext
          class="absolute right-1 inline-flex size-7 items-center justify-center rounded-md border border-input bg-transparent p-0 opacity-50 transition-opacity hover:opacity-100 disabled:pointer-events-none disabled:opacity-50"
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
            <path d="m9 18 6-6-6-6" />
          </svg>
        </CalendarNext>
      </CalendarHeader>
      <div class="flex flex-col gap-4 sm:flex-row">
        <CalendarGrid
          v-for="month in grid"
          :key="month.value.toString()"
          class="w-full border-collapse"
        >
          <CalendarGridHead>
            <CalendarGridRow class="flex">
              <CalendarHeadCell
                v-for="day in weekDays"
                :key="day"
                class="w-8 rounded-md text-[0.8rem] font-normal text-muted-foreground"
              >
                {{ day }}
              </CalendarHeadCell>
            </CalendarGridRow>
          </CalendarGridHead>
          <CalendarGridBody>
            <CalendarGridRow
              v-for="(weekDates, index) in month.rows"
              :key="`week-${index}`"
              class="mt-2 flex w-full"
            >
              <CalendarCell
                v-for="weekDate in weekDates"
                :key="weekDate.toString()"
                :date="weekDate"
                class="relative p-0 text-center text-sm"
              >
                <CalendarCellTrigger
                  :day="weekDate"
                  :month="month.value"
                  class="inline-flex size-8 items-center justify-center rounded-md p-0 text-sm font-normal transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 data-[selected=true]:bg-primary data-[selected=true]:text-primary-foreground data-[today]:bg-accent data-[today]:text-accent-foreground data-[today]:data-[selected=true]:bg-primary data-[today]:data-[selected=true]:text-primary-foreground data-[outside-view]:text-muted-foreground data-[disabled]:text-muted-foreground data-[disabled]:opacity-50 data-[unavailable]:text-muted-foreground data-[unavailable]:line-through"
                />
              </CalendarCell>
            </CalendarGridRow>
          </CalendarGridBody>
        </CalendarGrid>
      </div>
    </div>
  </CalendarRoot>
</template>

<script>
import { CalendarCell, CalendarCellTrigger, CalendarGrid, CalendarGridBody, CalendarGridHead, CalendarGridRow, CalendarHeadCell, CalendarHeader, CalendarHeading, CalendarNext, CalendarPrev, CalendarRoot, parseDate } from 'reka-ui';

export default {
  name: 'ShadcnCalendar',
  components: {
    CalendarCell,
    CalendarCellTrigger,
    CalendarGrid,
    CalendarGridBody,
    CalendarGridHead,
    CalendarGridRow,
    CalendarHeadCell,
    CalendarHeader,
    CalendarHeading,
    CalendarNext,
    CalendarPrev,
    CalendarRoot,
  },
  inheritAttrs: false,
  props: {
    // ISO `YYYY-MM-DD` strings cross the Python boundary; reka wants CalendarDate
    // objects, so every date prop is parsed on the way in and stringified on the
    // way out.
    modelValue: { type: [String, Array], default: '' },
    minValue: { type: String, default: '' },
    maxValue: { type: String, default: '' },
    weekStartsOn: { type: Number, default: undefined },
    numberOfMonths: { type: Number, default: 1 },
    fixedWeeks: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
    readonly: { type: Boolean, default: false },
    locale: { type: String, default: 'en-US' },
    ariaLabel: { type: String, default: 'Calendar' },
    // Consumed so that NiceGUI's ValueElement internal does not fall through
    // onto the calendar as a stray DOM attribute.
    loopback: { type: [Boolean, String], default: undefined },
  },
  emits: ['update:modelValue'],
  computed: {
    selectedDate() {
      return toDate(this.modelValue);
    },
    minDate() {
      return toDate(this.minValue);
    },
    maxDate() {
      return toDate(this.maxValue);
    },
  },
  methods: {
    onSelect(value) {
      if (!value) {
        this.$emit('update:modelValue', '');
        return;
      }
      this.$emit('update:modelValue', value.toString());
    },
  },
};

function toDate(value) {
  // NiceGUI's client-side loopback (`LOOPBACK = False`) stores the emit payload as a
  // one-element array in `model-value`, so unwrap it before parsing.
  if (Array.isArray(value)) value = value[0];
  if (!value) return undefined;
  try {
    return parseDate(value);
  } catch (error) {
    return undefined;
  }
}
</script>
