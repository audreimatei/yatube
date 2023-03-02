from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AuthorView.as_view(), name='author'),
    path('project/', views.ProjectView.as_view(), name='project'),
    path('tech/', views.TechView.as_view(), name='tech')
]
