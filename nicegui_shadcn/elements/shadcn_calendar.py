"""Calendar: a month grid that reports the picked day.

Dates cross the boundary as ISO ``YYYY-MM-DD`` strings, so Python can read and
write them without having to build `@internationalized/date` objects in Python.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from typing import Any

from nicegui.elements.mixins.value_element import ValueElement

from .base import ShadcnElement

__all__ = ['Calendar', 'calendar']


def _iso_date(value: Any) -> str:
    """Normalize a date-like value to ``YYYY-MM-DD`` (or an empty string)."""
    if value is None or value == '':
        return ''
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


class Calendar(ShadcnElement, ValueElement, component='shadcn_calendar.vue'):
    """A single-month calendar.

    :param value: the selected day, as a :class:`datetime.date` or an ISO
        ``YYYY-MM-DD`` string.
    :param min_value: the earliest selectable day.
    :param max_value: the latest selectable day.
    :param week_starts_on: ``0`` for Monday through ``6`` for Sunday; by default
        the locale decides.
    :param number_of_months: how many months to show side by side.
    :param fixed_weeks: always render six week rows so the grid does not jump
        between months.
    :param disabled: whether the whole calendar is read-only.
    :param readonly: whether days can be focused but not picked.
    :param locale: the BCP 47 locale used for month and weekday names.
    :param aria_label: the accessible name of the calendar grid.
    :param on_change: callback invoked with the value-change event when another
        day is picked; read ``e.value`` for the new ISO date string.
    """

    LOOPBACK = False

    def __init__(self,
                 value: date | datetime | str | None = None,
                 *,
                 min_value: date | datetime | str | None = None,
                 max_value: date | datetime | str | None = None,
                 week_starts_on: int | None = None,
                 number_of_months: int = 1,
                 fixed_weeks: bool = False,
                 disabled: bool = False,
                 readonly: bool = False,
                 locale: str = 'en-US',
                 aria_label: str = 'Calendar',
                 on_change: Callable[..., Any] | None = None,
                 classes: str | Iterable[str] | None = None,
                 **kwargs: Any,
                 ) -> None:
        super().__init__(value=_iso_date(value), on_value_change=on_change, classes=classes, **kwargs)
        if week_starts_on is not None and not 0 <= int(week_starts_on) <= 6:
            raise ValueError(f'week_starts_on must be between 0 and 6, got {week_starts_on}')
        self._props['minValue'] = _iso_date(min_value)
        self._props['maxValue'] = _iso_date(max_value)
        if week_starts_on is not None:
            self._props['weekStartsOn'] = int(week_starts_on)
        self._props['numberOfMonths'] = int(number_of_months)
        self._props['fixedWeeks'] = bool(fixed_weeks)
        self._props['disabled'] = bool(disabled)
        self._props['readonly'] = bool(readonly)
        self._props['locale'] = str(locale)
        self._props['ariaLabel'] = str(aria_label)

    def _value_to_model_value(self, value: Any) -> str:
        return _iso_date(value)


def calendar(value: date | datetime | str | None = None, **kwargs: Any) -> Calendar:
    """Create a :class:`Calendar`."""
    return Calendar(value, **kwargs)
