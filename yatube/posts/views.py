from django.shortcuts import render


def index(request):
    context = {
        'title': 'Это главная страница проекта Yatube',
    }
    return render(request, 'posts/index.html', context)


# not working
def group_posts(request, slug):
    context = {
        'title': 'Здесь будет информация о группах проекта Yatube',
    }
    return render(request, 'posts/group_list.html', context)
