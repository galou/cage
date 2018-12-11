#!/usr/bin/env python3

import sys

from calendra.europe import France


_ = {
        'New year': 'nouvel an',
        'Easter Monday': 'lundi de Pâques',
        'Labour Day': 'fête du travail',
        'Victory in Europe Day': 'victoire 1945',
        'Ascension Thursday': 'Ascension',
        'Whit Monday': 'Pentecôte',
        'Bastille Day': 'fête nationale',
        'Assumption of Mary to Heaven': 'Assomption',
        'All Saints Day': 'Toussaint',
        'Armistice Day': 'armistice 1918',
        'Christmas Day': 'Noël',
        }


def generate_holidays(start_year, end_year):
    cal = France()
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

