#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        }

_ = short_

def generate_holidays(start_year, end_year):
    cal = CzechRepublic()
    for year in range(start_year, end_year + 1):
        for holiday in cal.holidays(year):
            print('{},{}'.format(holiday.isoformat(), _[holiday.name]))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        generate_holidays(2015, 2020)
    else:
        try:
            start_year = int(sys.argv[1])
            end_year = int(sys.argv[2])
            generate_holidays(start_year, end_year)
        except ValueError:
            print('Usage: {} start_year end_year', sys.argv[0])

