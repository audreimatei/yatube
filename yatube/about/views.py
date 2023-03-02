from django.views.generic.base import TemplateView


class AuthorView(TemplateView):
    template_name = 'about/author.html'


class ProjectView(TemplateView):
    template_name = 'about/project.html'


class TechView(TemplateView):
    template_name = 'about/tech.html'
