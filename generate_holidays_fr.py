#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys

from calendra.europe import France


long_ = {
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
    'Good Friday': 'vendredi saint',
}

short_ = {
    'New year': 'nouv. an',
    'Easter Monday': 'l. de Pâques',
    'Labour Day': 'f. du travail',
    'Victory in Europe Day': 'vict. 1945',
    'Ascension Thursday': 'Ascension',
    'Whit Monday': 'Pentecôte',
    'Bastille Day': 'fête nat.',
    'Assumption of Mary to Heaven': 'Assomption',
    'All Saints Day': 'Toussaint',
    'Armistice Day': 'arm. 1918',
    'Christmas Day': 'Noël',
    'Good Friday': 'ven. saint',
}


def generate_holidays(start_year, end_year, length):
    cal = France()
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

