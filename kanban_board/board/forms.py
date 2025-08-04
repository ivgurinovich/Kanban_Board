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


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + [(status, status) for status, _ in Task.STATUS_CHOICES]

    assignee = forms.CharField(required=False, label='Assignee')
    author = forms.CharField(required=False, label='Author')
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='From date')
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='To date')
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status')
    show_only_mine = forms.BooleanField(required=False, label='Show only my tasks')
