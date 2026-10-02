"""Date Picker: a button that opens a :class:`~nicegui_shadcn.elements.shadcn_calendar.Calendar`.

This is a Python composition of :class:`~nicegui_shadcn.elements.shadcn_overlay.Popover`
and :class:`~nicegui_shadcn.elements.shadcn_calendar.Calendar` -- exactly how upstream
shadcn/ui ships its date picker -- so there is only ever one calendar implementation.

```python
picker = shadcn.date_picker(value=date(2026, 3, 15),
                            on_date_change=lambda e: ui.notify(e.date))
ui.label().bind_text_from(picker, 'date')
```
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from typing import Any

from .shadcn_calendar import Calendar, _iso_date
from .shadcn_overlay import Popover, PopoverContent, PopoverTrigger

__all__ = ['DatePicker', 'date_picker']


def _format_date(value: str) -> str:
    """Render an ISO date as ``March 15, 2026`` (falling back to the raw string)."""
    try:
        parsed = datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        return value
    return f'{parsed.strftime("%B")} {parsed.day}, {parsed.year}'


class DatePicker(Popover):
    """A button that opens a calendar panel and reports the chosen day.

    :param value: the selected day, as a :class:`datetime.date` or an ISO
        ``YYYY-MM-DD`` string.
    :param min_value: the earliest selectable day.
    :param max_value: the latest selectable day.
    :param placeholder: label of the button while no day is selected.
    :param week_starts_on: ``0`` for Monday through ``6`` for Sunday.
    :param locale: the BCP 47 locale used for month and weekday names.
    :param disabled: whether the whole picker is read-only.
    :param on_date_change: callback invoked with the value-change event whenever a
        day is picked; read ``e.value`` for the new ISO date string.
    """

    def __init__(self,
                 value: date | datetime | str | None = None,
                 *,
                 min_value: date | datetime | str | None = None,
                 max_value: date | datetime | str | None = None,
                 placeholder: str = 'Pick a date',
                 week_starts_on: int | None = None,
                 locale: str = 'en-US',
                 aria_label: str = 'Calendar',
                 disabled: bool = False,
                 format_date: Callable[[str], str] = _format_date,
                 on_date_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=False, classes=classes, **kwargs)
        self._placeholder = placeholder
        self._format_date = format_date
        self._date_change_handlers: list[Callable[..., Any]] = []
        with self:
            self._trigger = PopoverTrigger(self._label_for(_iso_date(value)),
                                           classes='w-[200px] justify-start text-left font-normal')
            with PopoverContent():
                self._calendar = Calendar(value,
                                          min_value=min_value,
                                          max_value=max_value,
                                          week_starts_on=week_starts_on,
                                          locale=locale,
                                          aria_label=aria_label,
                                          disabled=disabled,
                                          on_change=self._handle_date_change)
        if on_date_change is not None:
            self.on_date_change(on_date_change)

    def _label_for(self, value: str) -> str:
        return self._format_date(value) if value else self._placeholder

    def _handle_date_change(self, event: Any) -> None:
        self._trigger.text = self._label_for(_iso_date(event.value))
        self.close()
        for handler in list(self._date_change_handlers):
            handler(event)

    def on_date_change(self, callback: Callable[..., Any] | None) -> None:
        """Register a callback invoked when a day is picked."""
        if callback is not None:
            self._date_change_handlers.append(callback)

    @property
    def date(self) -> str:
        """The selected day as an ISO ``YYYY-MM-DD`` string (``''`` when unset)."""
        return _iso_date(self._calendar.value)

    @date.setter
    def date(self, value: date | datetime | str | None) -> None:
        self._calendar.set_value(_iso_date(value))
        self._trigger.text = self._label_for(_iso_date(value))

    @property
    def calendar(self) -> Calendar:
        """The underlying :class:`Calendar`."""
        return self._calendar

    @property
    def trigger(self) -> PopoverTrigger:
        """The underlying button that opens the calendar."""
        return self._trigger


def date_picker(value: date | datetime | str | None = None, **kwargs: Any) -> DatePicker:
    """Create a :class:`DatePicker`."""
    return DatePicker(value, **kwargs)
