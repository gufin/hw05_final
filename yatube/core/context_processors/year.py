import datetime


def year(request):
    year_val = datetime.date.today().year
    return {
        'year': year_val
    }
