# A class that contains the data to generate a csv file with one line per week
# with birthdays, events, moon phases among others.
#
# Birthday file: one birthday per line.
#   line = "yyyy-mm-dd,person", where yyyy is the birth year.
#   If the birthday year is unknow, write 0000 as year.
# Nameday file: one nameday (or other event) per line.
#   line = "i,mm-dd,person", where i is either 0 to avoid inclusion or 1.
# Moon file: one moon phase per line.
#   line = "yyyy-mm-dd,moon_phase".
#   The text `moon_phase` will be copied as is.
#   You can use unicode characters for the moon phases:
#   - ●
#   - ◐
#   - ○
#   - ◑
#   or
#   - u+e38d, Moon new, 
#   - u+e394, Moon First quarter, 
#   - u+e39b, Moon full, 
#   - u+e3a2, Moon last quarter, 
# Event file: one event per line.
#   line = "yyyy-mm-dd,event".
# Holiday file: one holiday per line.
#   line = "yyyy-mm-dd,holiday".
#   with 0000 for unknown birthday year.

import copy
import datetime
from typing import Any,Dict,List,Union
import warnings

__all__ = ['Calendar']

g_months = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
        ]

g_weekdays = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
        ]


def str_for_csv(l: Any, join: str = ', '):
    """Add double quotes (and join if list).

    Parameters
    ----------

    - l: Object with member __str__.
    - join: joining string.

    """
    if l is None:
        return '""'
    elif isinstance(l, list):
        return '"' + join.join([str(v) for v in l]) + '"'
    else:
        return '"' + str(l) + '"'


class Event:
    def __init__(self, datestr: str, name: str):
        """
        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd.
        - name: name of the birthday person.

        """
        self.year = int(datestr[:4])
        self.month = int(datestr[5:7])
        self.day = int(datestr[8:10])
        self.name = name

    @property
    def celebration_date(self):
        return datetime.date(self.year, self.month, self.day)

    def __str__(self):
        return self.name


# TODO: handle 02-29
class Birthday:
    def __init__(self, datestr: str, name: str):
        """
        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd.
        - name: name of the birthday person.

        """
        self.year = int(datestr[:4])
        if not self.year:
            # Minimum year for datetime.date is 1.
            self.year = 1
        self.month = int(datestr[5:7])
        self.day = int(datestr[8:10])
        self.date = datetime.date(self.year, self.month, self.day)
        self.name = name
        # True whether the celebration must be on the next day (for birthdays
        # on Feb. 29th).
        self.on_next_day = False

        self.celebration_year = datetime.date.today().year

    @property
    def celebration_date(self):
        try:
            date = datetime.date(self.celebration_year, self.month, self.day)
        except ValueError:
            self.on_next_day = True
            return datetime.date(self.celebration_year, 3, 1)
        return date

    def __str__(self):
        comment = ''
        join_str = ''
        if self.year != 1:
            comment += str(self.celebration_year - self.year)
            join_str = ', '
        if self.on_next_day:
            comment += join_str + '02-29'
        if comment:
            return self.name + ' (' + comment + ')'
        else:
            return self.name


class Nameday:
    def __init__(self, datestr: str, name: str):
        """
        Parameters
        ----------

        - datestr: date in format mm-dd.
        - name: name of the birthday person.

        """
        self.month = int(datestr[:2])
        self.day = int(datestr[3:5])
        self.name = name

        self.celebration_year = datetime.date.today().year

    @property
    def celebration_date(self):
        return datetime.date(self.celebration_year, self.month, self.day)

    def __str__(self):
        return self.name


class Day:
    def __init__(self, date: datetime.date):
        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.birthdays: List[Birthday] = []
        self.namedays: List[Nameday] = []
        self.events: List[Event] = []
        self.moon = None
        self.holiday = None

    @property
    def holiday(self):
        return self.__dict__['holiday']

    @holiday.setter
    def holiday(self, value: Event):
        if (value is not None) and not self.valid_date(value):
            warnings.warn('Holiday not at the correct date, ignoring')
        self.__dict__['holiday'] = value

    @property
    def moon(self):
        return self.__dict__['moon']

    @moon.setter
    def moon(self, value: Event):
        if (value is not None) and (not self.valid_date(value)):
            warnings.warn('Moon not at the correct date, ignoring')
        self.__dict__['moon'] = value

    def valid_date(self, event: Union[Birthday,Event,Nameday]):
        if (hasattr(event, 'year') and (event.year != 1) and
                (event.celebration_date.year != self.date.year)):
            return False
        if event.month != self.date.month:
            return False
        if event.day != self.date.day:
            return False
        return True

    def add_birthday(self, birthday: Birthday):
        if self.valid_date(birthday):
            self.birthdays.append(birthday)
        else:
            warnings.warn('Birthday not at the correct date, ignoring')

    def add_nameday(self, nameday: Nameday):
        if self.valid_date(nameday):
            self.namedays.append(nameday)
        else:
            warnings.warn('Nameday not at the correct date, ignoring')

    def add_event(self, event: Event):
        if self.valid_date(event):
            self.events.append(event)
        else:
            warnings.warn('Event not at the correct date, ignoring')


class Week:
    def __init__(self,
            monday: datetime.date,
            left_page: int,
            months: List[str]):
        """
        Parameters
        ----------
        - monday: a datetime.date object.

        """
        if monday.isoweekday() != 1:
            raise ValueError('First argument must be on Monday')
        self._monday = monday
        self._months = months
        self._left_page = left_page
        self._right_page = left_page + 1
        self.days: List[datetime.date] = []
        for delta in range(7):
            self.days.append(Day(monday + datetime.timedelta(delta)))

    def __str__(self):
        # This must correspond to the content of self.header.
        days_data: List[str] = []
        for day in self.days:
            days_data.append(day.day)
            days_data.append(str_for_csv(day.birthdays))
            days_data.append(str_for_csv(day.namedays))
            days_data.append(str_for_csv(day.events))
            days_data.append(str_for_csv(day.moon))
            days_data.append(str_for_csv(day.holiday))

        data = [self.code, self.number,
                '{:03}'.format(self._left_page),
                '{:03}'.format(self._right_page),
                self.month_str]
        data += days_data
        return ','.join([str(d) for d in data])

    @property
    def header(self):
        """Return the csv header line"""
        # This must correspond to the content of self.__str___.
        header = ['"code"', '"number"', '"page_left"', '"page_right"',
                '"month"']
        for d in range(7):
            header.append(str_for_csv(g_weekdays[d]))
            header.append(str_for_csv('birthdays_' + g_weekdays[d]))
            header.append(str_for_csv('namedays_' + g_weekdays[d]))
            header.append(str_for_csv('events_' + g_weekdays[d]))
            header.append(str_for_csv('moon_' + g_weekdays[d]))
            header.append(str_for_csv('holiday_' + g_weekdays[d]))
        header_str = ','.join(header)
        return header_str

    @property
    def month_str(self) -> str:
        """Return e.g. 'Jan' or 'Jan - Feb'.

        'Jan' would be replaced by the translated month.

        """
        month_monday = self.monday.month - 1
        month_sunday = self.sunday.month - 1
        if month_monday == month_sunday:
            return self._months[month_monday]
        else:
            return (self._months[month_monday] + ' - ' +
                    self._months[month_sunday])

    @property
    def monday(self) -> datetime.date:
        return self.days[0]

    @property
    def tuesday(self) -> datetime.date:
        return self.days[1]

    @property
    def wednesday(self) -> datetime.date:
        return self.days[2]

    @property
    def thursday(self) -> datetime.date:
        return self.days[3]

    @property
    def friday(self) -> datetime.date:
        return self.days[4]

    @property
    def saturday(self) -> datetime.date:
        return self.days[5]

    @property
    def sunday(self) -> datetime.date:
        return self.days[6]

    @property
    def number(self) -> int:
        """The number of the calendar week, according to ISO 8601."""
        return self._monday.isocalendar()[1]

    @property
    def code(self) -> str:
        """Return e.g. 2022-04 for the 4th week in 2022."""
        return '{}-{:02}'.format(self.monday.year, self._monday.isocalendar()[1])

    def add_birthday(self, birthday: Birthday):
        delta = (birthday.celebration_date - self._monday).days
        self.days[delta].add_birthday(birthday)

    def add_nameday(self, nameday: Nameday):
        delta = (nameday.celebration_date - self._monday).days
        self.days[delta].add_nameday(nameday)

    def add_event(self, event: Event):
        delta = (event.celebration_date - self._monday).days
        self.days[delta].add_event(event)

    def add_moon(self, moon: Event):
        delta = (moon.celebration_date - self._monday).days
        self.days[delta].moon = moon

    def add_holiday(self, holiday: Event):
        delta = (holiday.celebration_date - self._monday).days
        self.days[delta].holiday = holiday


class Calendar:
    def __init__(self,
            year: int,
            extra_weeks: int,
            start_page: int = 2,
            months: List[str] = g_months):
        """

        Parameters
        ----------

        - year: year for which to generate data.
        - extra_weeks: number of weeks of the following year.
        - start_page: page where the generated data will start.
        - months: list of months.

        """
        self.year = year
        if months is None:
            self.months = g_months
        self.months = months
        self.init_weeks(year, extra_weeks, start_page)

    def __str__(self):
        if not self.weeks:
            return ''
        header_str = self.weeks[0].header + '\n'

        return header_str + '\n'.join([str(w) for w in self.weeks])

    def init_weeks(self, year: int, extra_weeks: int, start_page: int):
        first_january = datetime.date(year, 1, 1)
        # `first_day` is the Monday in the same week as `first_january`..
        self.first_day = first_january - datetime.timedelta(
                first_january.weekday())
        last_december = datetime.date(year, 12, 31)
        # `last_day` is the Sunday in the same week as `last_december`.
        self.last_day = last_december + datetime.timedelta(
                -last_december.weekday() + 7 * (extra_weeks + 1) - 1)
        self.weeks: List[Week] = []
        self.week_of_day: Dict[datetime.date,Week] = {}
        day = copy.copy(self.first_day)
        left_page = copy.copy(start_page)
        while day < self.last_day:
            week = Week(day, left_page, self.months)
            self.weeks.append(week)
            for delta in range(7):
                self.week_of_day[day + datetime.timedelta(delta)] = week
            day += datetime.timedelta(7)
            left_page += 2

    def add_birthday(self, datestr: str, name: str):
        """

        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd, with 0000 for unknown birthday
            year.
        - name: name of the birthday person.

        """
        birthday = Birthday(datestr, name)
        birthday.celebration_year = self.year - 1
        if birthday.celebration_date in self.week_of_day:
            self.week_of_day[birthday.celebration_date].add_birthday(birthday)
        birthday = copy.deepcopy(birthday)
        birthday.celebration_year = self.year
        self.week_of_day[birthday.celebration_date].add_birthday(birthday)
        birthday = copy.deepcopy(birthday)
        birthday.celebration_year = self.year + 1
        if birthday.celebration_date in self.week_of_day:
            self.week_of_day[birthday.celebration_date].add_birthday(birthday)

    def add_nameday(self, datestr: str, name: str):
        """

        Parameters
        ----------

        - datestr: date in format mm-dd.
        - name: name of the celebrated saint.

        """
        nameday = Nameday(datestr, name)
        nameday.celebration_year = self.year - 1
        try:
            if nameday.celebration_date in self.week_of_day:
                self.week_of_day[nameday.celebration_date].add_nameday(nameday)
        except ValueError:
            pass
        nameday = copy.deepcopy(nameday)
        nameday.celebration_year = self.year
        try:
            self.week_of_day[nameday.celebration_date].add_nameday(nameday)
        except ValueError:
            pass
        nameday = copy.deepcopy(nameday)
        nameday.celebration_year = self.year + 1
        try:
            if nameday.celebration_date in self.week_of_day:
                self.week_of_day[nameday.celebration_date].add_nameday(nameday)
        except ValueError:
            pass

    def add_event(self, datestr: str, name: str):
        """

        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd.
        - name: name of the event.

        """
        event = Event(datestr, name)
        if event.celebration_date in self.week_of_day:
            self.week_of_day[event.celebration_date].add_event(event)

    def set_moon(self, datestr: str, phase: str):
        """

        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd.
        - phase: moon phase

        """
        moon = Event(datestr, phase)
        if moon.celebration_date in self.week_of_day:
            self.week_of_day[moon.celebration_date].add_moon(moon)

    def set_holiday(self, datestr: str, name: str):
        """

        Parameters
        ----------

        - datestr: date in format yyyy-mm-dd.
        - name: name of the holiday.

        """
        holiday = Event(datestr, name)
        if holiday.celebration_date in self.week_of_day:
            self.week_of_day[holiday.celebration_date].add_holiday(holiday)

