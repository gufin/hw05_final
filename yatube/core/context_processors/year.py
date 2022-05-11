from django.utils import timezone


def year(request):
    year_val = timezone.now().year
    return {
        'year': year_val
    }
