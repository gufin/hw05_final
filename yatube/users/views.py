from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PassChange(CreateView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_done.html'
