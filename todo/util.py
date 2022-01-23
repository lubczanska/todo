import datetime


def date_parser(date):
    today = datetime.date.today()
    week_shift = 0
    if date == 'today':
        parsed_date = today
    elif date == 'tomorrow':
        parsed_date = today + datetime.timedelta(1)
    else:
        if date.startswith('next'):
            week_shift = 7
            date = date[5:]
        days = {'monday': 0, 'tuesday': 1, 'friday': 4, 'wednesday': 2, 'thursday': 3, 'saturday': 5, 'sunday': 6}
        parsed_date = today + datetime.timedelta(week_shift + (days[date]-today.weekday()) % 7)
    return parsed_date
