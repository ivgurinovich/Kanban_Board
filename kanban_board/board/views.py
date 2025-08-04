from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Comment
from .forms import TaskForm, CommentForm, TaskFilterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import matplotlib.pyplot as plt
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from .models import Task
from django.contrib.auth.models import User
import os
from django.conf import settings
from datetime import datetime
from .forms import RegisterForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from django.template.loader import render_to_string


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            return redirect('task_board')
    else:
        form = TaskForm()
    return render(request, 'board/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_board')
    else:
        form = TaskForm(instance=task)
    return render(request, 'board/task_form.html', {'form': form})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('task_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'board/task_detail.html', {'task': task, 'comments': comments, 'form': form})


def generate_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF', status=500)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # логин после регистрации вот тут!!!!!!
            return redirect('task_board')
    else:
        form = RegisterForm()
    return render(request, 'board/register.html', {'form': form})


@login_required
def task_board(request):
    tasks = Task.objects.all()
    form = TaskFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['assignee']:
            tasks = tasks.filter(assignee__username__icontains=form.cleaned_data['assignee'])
        if form.cleaned_data['author']:
            tasks = tasks.filter(author__username__icontains=form.cleaned_data['author'])
        if form.cleaned_data['status']:
            tasks = tasks.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['start_date']:
            tasks = tasks.filter(created_at__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            tasks = tasks.filter(created_at__lte=form.cleaned_data['end_date'])
        if form.cleaned_data.get('show_only_mine'):
            tasks = tasks.filter(assignee=request.user)

    status_columns = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    return render(request, 'board/task_board.html', {
        'tasks': tasks,
        'form': form,
        'status_columns': status_columns,
    })


@csrf_exempt
@login_required
def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        try:
            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})


def generate_report(request):
    tasks = Task.objects.all()
    form = TaskFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['assignee']:
            tasks = tasks.filter(assignee__username__icontains=form.cleaned_data['assignee'])
        if form.cleaned_data['author']:
            tasks = tasks.filter(author__username__icontains=form.cleaned_data['author'])
        if form.cleaned_data['status']:
            tasks = tasks.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['start_date']:
            tasks = tasks.filter(created_at__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            tasks = tasks.filter(created_at__lte=form.cleaned_data['end_date'])
        if form.cleaned_data.get('show_only_mine'):
            tasks = tasks.filter(assignee__isnull=False, assignee=request.user)

    template = get_template('board/report_template.html')
    html = template.render({'tasks': tasks})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF', status=500)


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.author != request.user:
        return HttpResponse("You do not have permission to delete this task.", status=403)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_board')

    return render(request, 'board/task_confirm_delete.html', {'task': task})
