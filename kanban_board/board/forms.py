from django import forms
from .models import Task, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assignee']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']