#
# Birthday file: one birthday per line.
#   line = "yyyy-mm-dd,person", where yyyy is the birth year.
#   If the birthday year is unknow, write 0000 as year.
# Nameday file: one nameday (or other event) per line.
#   line = "i,mm-dd,person", where i is either 0 to avoid inclusion or 1.
# Moon file: one moon phase per line.
#   line = "yyyy-mm-dd,moon_phase".
# Event file: one event per line.
#   line = "yyyy-mm-dd,event".
# Holiday file: one holiday per line.
#   line = "yyyy-mm-dd,holiday".

import datetime
import copy
import warnings

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
__all__ = ['Calendar']

# Do not touch.
g_weekdays = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
        ]

def str_for_csv(l, join=', '):
    """Add double quotes (and join if list)"""
    if l is None:
        return '""'
    elif isinstance(l, list):
        return '"' + join.join([str(v) for v in l]) + '"'
    else:
        return '"' + str(l) + '"'


class Day:
    def __init__(self, date):
        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.birthdays = []
        self.namedays = []
        self.events = []
        self.moon = None
        self.holiday = None

    @property
    def holiday(self):
        return self.__dict__['holiday']

    @holiday.setter
    def holiday(self, value):
        if value is not None and not self.valid_date(value):
            warnings.warn('Holiday not at the correct date, ignoring')
        self.__dict__['holiday'] = value

    @property
    def moon(self):
        return self.__dict__['moon']

    @moon.setter
    def moon(self, value):
        if value is not None and not self.valid_date(value):
            warnings.warn('Moon not at the correct date, ignoring')
        self.__dict__['moon'] = value

    def valid_date(self, event):
        if (hasattr(event, 'year') and (event.year != 1) and
                (event.celebration_date.year != self.date.year)):
            return False
        if event.month != self.date.month:
            return False
        if event.day != self.date.day:
            return False
        return True

    def add_birthday(self, birthday):
        if self.valid_date(birthday):
            self.birthdays.append(birthday)
        else:
            warnings.warn('Birthday not at the correct date, ignoring')

    def add_nameday(self, nameday):
        if self.valid_date(nameday):
            self.namedays.append(nameday)
        else:
            warnings.warn('Nameday not at the correct date, ignoring')

    def add_event(self, event):
        if self.valid_date(event):
            self.events.append(event)
        else:
            warnings.warn('Event not at the correct date, ignoring')


class Week:
    def __init__(self, monday, left_page, months):
        """
        Parameters
        ----------
        monday: a datetime.date object.
        """
        if monday.isoweekday() != 1:
            raise ValueError('First argument must be on Monday')
        self._monday = monday
        self._months = months
        self._left_page = left_page
        self._right_page = left_page + 1
        self.days = []
        for delta in range(7):
            self.days.append(Day(monday + datetime.timedelta(delta)))

    def __str__(self):
        # This must correspond to the content of self.header.
        days_data = []
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
    def month_str(self):
        month_monday = self.monday.month - 1
        month_sunday = self.sunday.month - 1
        if month_monday == month_sunday:
            return self._months[month_monday]
        else:
            return (self._months[month_monday] + ' - ' +
                    self._months[month_sunday])
    @property
    def monday(self):
        return self.days[0]

    @property
    def tuesday(self):
        return self.days[1]

    @property
    def wednesday(self):
        return self.days[2]

    @property
    def thursday(self):
        return self.days[3]

    @property
    def friday(self):
        return self.days[4]

    @property
    def saturday(self):
        return self.days[5]

    @property
    def sunday(self):
        return self.days[6]

    @property
    def number(self):
        return self._monday.isocalendar()[1]

    @property
    def code(self):
        return '{}-{:02}'.format(self.sunday.year, self._monday.isocalendar()[1])

    def add_birthday(self, birthday):
        delta = (birthday.celebration_date - self._monday).days
        self.days[delta].add_birthday(birthday)

    def add_nameday(self, nameday):
        delta = (nameday.celebration_date - self._monday).days
        self.days[delta].add_nameday(nameday)

    def add_event(self, event):
        delta = (event.celebration_date - self._monday).days
        self.days[delta].add_event(event)

    def add_moon(self, moon):
        """
        Parameters
        ----------
        - moon: an Event instance.
        """
        delta = (moon.celebration_date - self._monday).days
        self.days[delta].moon = moon

    def add_holiday(self, holiday):
        """
        Parameters
        ----------
        - holiday: an Event instance.
        """
        delta = (holiday.celebration_date - self._monday).days
        self.days[delta].holiday = holiday


# TODO: handle 02-29
class Birthday:
    def __init__(self, datestr, name):
        self.year = int(datestr[:4])
        if not self.year:
            # Minimum year for datetime.date is 1.
            self.year = 1
        self.month = int(datestr[5:7])
        self.day = int(datestr[8:10])
        self.date = datetime.date(self.year, self.month, self.day)
        self.name = name
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
    def __init__(self, datestr, name):
        self.month = int(datestr[:2])
        self.day = int(datestr[3:5])
        self.name = name

        self.celebration_year = datetime.date.today().year

    @property
    def celebration_date(self):
        return datetime.date(self.celebration_year, self.month, self.day)

    def __str__(self):
        return self.name


class Event:
    def __init__(self, datestr, name):
        self.year = int(datestr[:4])
        self.month = int(datestr[5:7])
        self.day = int(datestr[8:10])
        self.name = name

    @property
    def celebration_date(self):
        return datetime.date(self.year, self.month, self.day)

    def __str__(self):
        return self.name


class Calendar:
    def __init__(self, year, extra_weeks, start_page=2, months=g_months):
        """
        Parameters
        ----------
        year: int, year for which to generate data.
        extra_weeks: int, number of weeks of the following year.
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

    def init_weeks(self, year, extra_weeks, start_page):
        first_january = datetime.date(year, 1, 1)
        # first_day is a Monday.
        self.first_day = first_january - datetime.timedelta(
                first_january.weekday())
        last_december = datetime.date(year, 12, 31)
        # last_day is a Sunday.
        self.last_day = last_december + datetime.timedelta(
                -last_december.weekday() + 7 * (extra_weeks + 1) - 1)
        self.weeks = []
        self.week_of_day = {}
        day = copy.deepcopy(self.first_day)
        left_page = copy.deepcopy(start_page)
        while day < self.last_day:
            week = Week(day, left_page, self.months)
            self.weeks.append(week)
            for delta in range(7):
                self.week_of_day[day + datetime.timedelta(delta)] = week
            day += datetime.timedelta(7)
            left_page += 2

    def add_birthday(self, datestr, name):
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

    def add_nameday(self, datestr, name):
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

    def add_event(self, datestr, name):
        event = Event(datestr, name)
        if event.celebration_date in self.week_of_day:
            self.week_of_day[event.celebration_date].add_event(event)

    def set_moon(self, datestr, name):
        moon = Event(datestr, name)
        if moon.celebration_date in self.week_of_day:
            self.week_of_day[moon.celebration_date].add_moon(moon)

    def set_holiday(self, datestr, name):
        holiday = Event(datestr, name)
        if holiday.celebration_date in self.week_of_day:
            self.week_of_day[holiday.celebration_date].add_holiday(holiday)

