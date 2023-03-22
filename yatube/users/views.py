from django.urls import reverse_lazy
from django.views.generic import CreateView

from posts.models import Profile
from users.forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        profile = Profile.objects.create(user=self.object)
        profile.save()
        return response
