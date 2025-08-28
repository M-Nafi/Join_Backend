from django.contrib import admin
from .models import Contact, Task, Subtask, TaskUserDetails

class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 1 

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'emblem', 'color')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'display_users', 'display_subtasks')
    inlines = [SubtaskInline]

    def display_users(self, obj):
        """
        Returns a string of comma-separated usernames for the users assigned to the given Task object.
        """
        return ", ".join([user.username for user in obj.user.all()])
    display_users.short_description = "Users"

    def display_subtasks(self, obj):
        """
        Returns a string of comma-separated subtasktexts for the subtasks associated with the given Task object.
        """
        return ", ".join([subtask.subtasktext for subtask in obj.subtasks.all()])
    display_subtasks.short_description = "Subtasks"

@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('subtasktext', 'checked', 'task')

@admin.register(TaskUserDetails)
class TaskUserDetailsrAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'checked')
