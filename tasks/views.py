from typing import Any, Optional, Type
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .forms import CaptchaTestModelForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from kafka import KafkaProducer
import json

from . models import Task
# Create your views here.

class LoginView(LoginView):
    template_name = 'task/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'task/register.html'
    form_class = CaptchaTestModelForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    template_name = 'task/task_list.html'
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'task/task_detail.html'

def get_partition(key, all, available):
    #return 0 entails persist message to P0
    return 0

class TaskCreate(LoginRequiredMixin, CreateView):
    template_name = 'task/task_form.html'
    model = Task
    fields = ['title', 'body', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        producer = KafkaProducer(bootstrap_servers=['172.20.10.2:29092'],
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        #partitioner=get_partition
                        )
        producer.send('Redemption', form.cleaned_data)
        print(form.cleaned_data)
        return super(TaskCreate, self).form_valid(form)
    

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'task/task_form.html'
    fields = ['title', 'body', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    template_name = 'task/task_confirm_delete.html'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)
