from django.db.models.signals import m2m_changed, post_save
from django.db.models import Count
from django.dispatch import receiver
from tasks.models import TodoItem, Category, PriorityCount, PRIORITY_CHOICES
from collections import Counter


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    for cat in instance.category.all():
        slug = cat.slug

        new_count = 0
        for task in TodoItem.objects.all():
            new_count += task.category.filter(slug=slug).count()

        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
    if action != "post_remove":
        return

    # cat_counter = Counter()
    for t in Category.objects.all():
        Category.objects.filter(slug=t.slug).update(
            todos_count=TodoItem.objects.filter(category=t.id).count())


@receiver(post_save, sender=TodoItem)
def task_cats_saved(**kwargs):
    for item_priority, vv in PRIORITY_CHOICES:
        PriorityCount.objects.update_or_create(
            priority=item_priority,
            defaults={'todos_count': TodoItem.objects.filter(
                priority=item_priority).count()},
        )
