from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Comment
from .forms import TaskForm, CommentForm
from django.contrib.auth.decorators import login_required
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


def generate_report(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    user_id = request.GET.get('user')

    tasks = Task.objects.all()

    if date_from:
        tasks = tasks.filter(created_at__date__gte=date_from)
    if date_to:
        tasks = tasks.filter(created_at__date__lte=date_to)
    if user_id:
        tasks = tasks.filter(author__id=user_id)

    # Pie chart
    status_counts = {
        'To Do': tasks.filter(status='to_do').count(),
        'In Progress': tasks.filter(status='in_progress').count(),
        'Done': tasks.filter(status='done').count(),
    }

    labels = list(status_counts.keys())
    sizes = list(status_counts.values())

    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')

    chart_path = os.path.join(settings.MEDIA_ROOT, 'task_chart.png')
    plt.savefig(chart_path)
    plt.close()

    context = {
        'tasks': tasks,
        'date_from': date_from,
        'date_to': date_to,
        'user_filter': User.objects.get(pk=user_id).username if user_id else None,
        'chart_path': f'file://{chart_path}'
    }

    return generate_pdf('board/report_template.html', context)


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
    status_columns = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    return render(request, 'board/task_board.html', {
        'tasks': tasks,
        'status_columns': status_columns
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
