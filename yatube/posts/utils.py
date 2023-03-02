from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def get_all_fields(klass):
    return tuple(field.name for field in klass._meta.fields)


def get_page_obj(request, posts):
    return Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))
