#!/usr/bin/env python3

from optparse import OptionParser

from csvcalendar import Calendar

def generate_csv(year, **kwargs):
    """
    Parameters
    ----------
    year: int, year for which to generate data.
    extra_weeks: int, number of weeks of the following year.
    birthday_file: str, file with birthdays (cf. above for
      format explanation).
    nameday_file: str, file with namedays (cf. above for
      format explanation).
    event_file: str, file with events (cf. above for
      format explanation).
    """
    extra_weeks = kwargs.get('extra_weeks', 2)
    start_page = kwargs.get('start_page', 2)
    birthday_file = kwargs.get('birthday_file', None)
    event_file = kwargs.get('event_file', None)
    holiday_file = kwargs.get('holiday_file', None)
    moon_file = kwargs.get('moon_file', None)
    month_file = kwargs.get('month_file', None)
    nameday_file = kwargs.get('nameday_file', None)

    cal = Calendar(year,
            extra_weeks=extra_weeks,
            start_page=start_page,
            months=get_months(month_file))
    add_birthdays(cal, birthday_file)
    add_events(cal, event_file, cal.add_event)
    add_events(cal, holiday_file, cal.set_holiday)
    add_events(cal, moon_file, cal.set_moon)
    add_namedays(cal, nameday_file)
    print(cal)


def get_months(month_file):
    months = []
    with open(month_file, 'r') as f:
        for l in f.readlines():
            months.append(l.strip())
    if len(months) != 12:
        raise ValueError('Error in month file')
    return months


def add_birthdays(cal, birthday_file):
    if birthday_file is None:
        return
    with open(birthday_file, 'r') as f:
        try:
            for l in f.readlines():
                datestr = l[:10]
                name = l[11:].strip()
                cal.add_birthday(datestr, name)
        except:
            raise ValueError('Wrong format for birthday file, see --help for details')


def add_events(cal, event_file, add_function):
    """Add events with format 'yyy-mm-dd,name'"""
    if event_file is None:
        return
    with open(event_file, 'r') as f:
        try:
            for l in f.readlines():
                datestr = l[:10]
                name = l[11:].strip()
                add_function(datestr, name)
        except:
            raise ValueError('Wrong file format, see --help for details')



def add_namedays(cal, nameday_file):
    if nameday_file is None:
        return
    with open(nameday_file, 'r') as f:
        for l in f.readlines():
            try:
                include = bool(int(l[0]))
            except (ValueError, IndexError):
                raise ValueError('Wrong format for nameday file, see --help for details')
            if not include:
                continue
            datestr = l[2:7]
            name = l[8:].strip()
            cal.add_nameday(datestr, name)


if __name__ == '__main__':
    usage = "usage: %prog [options] year"
    parser = OptionParser(usage=usage)

    parser.add_option('-e', '--extra-weeks', dest='extra_weeks',
            action='store', type='int', default=2,
            help='extra weeks of the following year')

    parser.add_option('-s', '--start-page', dest='start_page',
            action='store', type='int', default=2,
            help='start page for week 1 (even number)')

    parser.add_option('-b', '--birthday-file', dest='birthday_file',
            action='store', type='string', metavar='FILE', default=None,
            help='birthday file with "YYYY-mm-dd,name" format')

    parser.add_option('-d', '--holiday-file', dest='holiday_file',
            action='store', type='string', metavar='FILE', default=None,
            help='holiday file with "YYYY-mm-dd,name" format')

    parser.add_option('-m', '--moon-file', dest='moon_file',
            action='store', type='string', metavar='FILE', default=None,
            help='moon file with "YYYY-mm-dd,name" format')

    parser.add_option('-n', '--nameday-file', dest='nameday_file',
            action='store', type='string', metavar='FILE', default=None,
            help='nameday file with "{0|1},mm-dd,name" format')

    parser.add_option('-t', '--month-file', dest='month_file',
            action='store', type='string', metavar='FILE', default=None,
            help='month file with one month per line')

    parser.add_option('-v', '--event-file', dest='event_file',
            action='store', type='string', metavar='FILE', default=None,
            help='event file with "YYYY-mm-dd,name" format')

    options, args = parser.parse_args()
    if not args:
        parser.error('year argument missing')
    generate_csv(int(args[0]),
            extra_weeks=options.extra_weeks,
            start_page=options.start_page,
            birthday_file=options.birthday_file,
            holiday_file=options.holiday_file,
            moon_file=options.moon_file,
            nameday_file=options.nameday_file,
            month_file=options.month_file,
            event_file=options.event_file)
