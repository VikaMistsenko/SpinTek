import csv
import datetime
import requests
from bs4 import BeautifulSoup


def parse_date(date_str):
    month_names = {
        'jaanuar': '01',
        'veebruar': '02',
        'märts': '03',
        'aprill': '04',
        'mai': '05',
        'juuni': '06',
        'juuli': '07',
        'august': '08',
        'september': '09',
        'oktoober': '10',
        'november': '11',
        'detsember': '12',
    }
    date_str = date_str.replace('.', '')
    day, month_name, year = date_str.split()
    month = month_names[month_name]
    return datetime.datetime.strptime(f'{day} {month} {year}', '%d %m %Y').date().strftime('%Y-%m-%d')


def payday_reminder():
    while True:
        try:
            year = int(input("Sisestage aasta (2022-2027): "))
            if year < 2022 or year > 2027:
                raise ValueError
            break
        except ValueError:
            print("Viga: sisestage aasta vahemikus 2022-2027!")
    holidays = read_holidays(year)
    holidays = [parse_date(holiday) for holiday in holidays]
    with open(f'{year}.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Kuu', 'Palgamakse kuupäev', 'Meeldetuletuse saatmise kuupäev'])
        for month in range(1, 13):
            pay_date = datetime.date(year, month, 10)
            pay_date = find_workday(pay_date, holidays)
            reminder_date = pay_date - datetime.timedelta(days=3)
            reminder_date = find_workday(reminder_date, holidays)
            writer.writerow([datetime.date(year, month, 1).strftime('%B'), pay_date.strftime('%Y-%m-%d'),
                             reminder_date.strftime('%Y-%m-%d')])
    print_csv(f'{year}.csv')


def read_holidays(year):
    url = f"https://xn--riigiphad-v9a.ee/?y={year}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        holiday_cells = soup.find_all('td', itemprop="startDate")
        fail_name = "holiday.txt"
        with open(fail_name, 'w', encoding='utf-8') as f:
            for cell in holiday_cells:
                f.write(cell.text.strip() + '\n')
    else:
        print('Error:', response.status_code)

    with open('holiday.txt', 'r') as f:
        holidays = [line.strip().split(' ', 1)[1] for line in f.readlines()]
    return holidays


def find_workday(date, holidays):
    while date.strftime('%A') in ['Saturday', 'Sunday'] or date.strftime('%Y-%m-%d') in holidays:
        date -= datetime.timedelta(days=1)
    return date


def print_csv(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        header = lines[0].strip().split(',')
        rows = [line.strip().split(',') for line in lines[1:]]
        column_widths = [max(len(row[i]) for row in [header] + rows) for i in range(len(header))]
        divider = '+' + '+'.join('-' * (width + 2) for width in column_widths) + '+'
        print(divider)
        print('| ' + ' | '.join(f'{header[i]:^{column_widths[i]}}' for i in range(len(header))) + ' |')
        print(divider)
        for row in rows:
            print('| ' + ' | '.join(f'{row[i]:^{column_widths[i]}}' for i in range(len(row))) + ' |')
            print(divider)


payday_reminder()
