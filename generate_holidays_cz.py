#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys

from calendra.europe import CzechRepublic


long_ = {
    'New year': 'Nový rok',
    'Restoration Day of the Independent Czech State': (
        'Den obnovy samostatného českého státu'),
    'Easter Monday': 'Velikonoční pondělí',
    'Labour Day': 'Svátek práce',
    'Liberation Day': 'Den vítězství',
    'Saints Cyril and Methodius Day': (
        'Den slovanských věrozvěstů Cyrila a Metoděje'),
    'Jan Hus Day': 'Den upálení mistra Jana Husa',
    'St. Wenceslas Day (Czech Statehood Day)': 'Den české státnosti',
    'Independent Czechoslovak State Day': (
        'Den vzniku samostatného československého státu'),
    'Struggle for Freedom and Democracy Day': (
        'Den boje za svobodu a demokracii'),
    'Christmas Eve': 'Štědrý den',
    'Christmas Day': '1. svátek vánoční',
    "St. Stephen's Day (The Second Christmas Day)": '2. svátek vánoční',
    'Good Friday': 'Velký pátek',
}

short_ = {
    'New year': 'Nový rok',
    'Restoration Day of the Independent Czech State': (
        'Den obnovy samostatného českého státu'),
    'Easter Monday': 'Velikonoční pondělí',
    'Labour Day': 'Svátek práce',
    'Liberation Day': 'Den vítězství',
    'Saints Cyril and Methodius Day': (
        'Cyril a Metoděj'),
    'Jan Hus Day': 'Den upálení mistra Jana Husa',
    'St. Wenceslas Day (Czech Statehood Day)': 'Den české státnosti',
    'Independent Czechoslovak State Day': (
        'Den vzniku samostatného československého státu'),
    'Struggle for Freedom and Democracy Day': (
        'Den boje za svobodu a demokracii'),
    'Christmas Eve': 'Štědrý den',
    'Christmas Day': '1. svátek vánoční',
    "St. Stephen's Day (The Second Christmas Day)": '2. svátek vánoční',
    'Good Friday': 'Velký pátek',
}


def generate_holidays(start_year, end_year, length):
    cal = CzechRepublic()
    for year in range(start_year, end_year + 1):
        for holiday in cal.holidays(year):
            if length == 'long':
                print('{},{}'.format(holiday.isoformat(), long_[holiday.name]))
            else:
                print('{},{}'.format(holiday.isoformat(), short_[holiday.name]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        this_year = datetime.datetime.now().year
        generate_holidays(this_year, this_year + 1, 'long')
    else:
        try:
            start_year = int(sys.argv[1])
            end_year = start_year
            try:
                end_year = int(sys.argv[2])
            except IndexError:
                pass
            length = 'long'
            try:
                length = sys.argv[3]
            except IndexError:
                pass
            generate_holidays(start_year, end_year, length)
        except ValueError:
            print('Usage: {} start_year [end_year] [{long|short}]', sys.argv[0])

