from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.db.models import Count
from django.core.cache import cache
import time
import datetime

from tasks.models import TodoItem, Category, PriorityCount


def index(request):

    datetime_from_cache = cache.get('datetime_from_cache')
    if datetime_from_cache is None:
        datetime_from_cache = datetime.datetime.now()
        cache.set('datetime_from_cache', datetime_from_cache, 300)

    counts = {c.name: c.todos_count for c in Category.objects.all()}
    counts_priority = {
        c.get_priority_display(): c.todos_count for c in PriorityCount.objects.all()}

    return render(request, "tasks/index.html", {"counts": counts, "counts_priority": counts_priority, "datetime_from_cache": datetime_from_cache})


def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        tags = []
        categories = []
        for t in user_tasks:
            tags.append(list(t.category.all()))

            for cat in t.category.all():
                if cat not in categories:
                    categories.append(cat)
            context["categories"] = categories

        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"
