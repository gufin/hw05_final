from django.core.paginator import Paginator


def paginator_add(post_list, post_per_page, request=None):
    paginator = Paginator(post_list, post_per_page)
    page_number = 1 if request is None else request.GET.get('page')
    return paginator.get_page(page_number)
