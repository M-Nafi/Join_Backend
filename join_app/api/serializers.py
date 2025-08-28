from rest_framework import serializers
from ..models import Contact, Task, Subtask, TaskUserDetails
from user_auth_app.models import CustomUser
from user_auth_app.api.serializers import CustomUserSerializer
import re

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'phone', 'emblem', 'color')
        read_only_fields = ('id',)

    def validate_email(self, value):
        """
        Validates a contact's email.

        Raises:
            serializers.ValidationError: If the contact's E-Mail is the same as the user's E-Mail.
            serializers.ValidationError: If the contact's E-Mail already exists in the user's contacts.
            serializers.ValidationError: If the contact's E-Mail already exists in the user table.
        """
        user = self.context['request'].user
        contact_id = self.instance.id if self.instance else None

        if user.email == value:
            raise serializers.ValidationError("E-Mail cannot be the same as the user's E-Mail.")

        if Contact.objects.filter(user=user, email=value).exclude(id=contact_id).exists():
            raise serializers.ValidationError("email already exists.")

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("email already exists.")

        return value

    def create(self, validated_data):
        """
        Creates a new contact.

        Associates the contact with the user of the current request.

        :return: The created contact.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Updates an existing contact.

        :return: The updated contact.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
    def perform_destroy(self, instance):
        """
        Deletes an existing contact.

        If the contact is associated with the same user as the request, the user is also deleted.

        """
        user = instance.user
        instance.delete()

        if user == self.request.user:
            user.delete()

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ('id', 'subtasktext', 'checked', 'task')
        read_only_fields = ('task',)

    def validate_subtasks(self, value):
        """
        Validates a list of subtasks.

        Raises:
            serializers.ValidationError: If the list has more than 5 elements.
        """
        if len(value) > 5:
            raise serializers.ValidationError("maximum 5 subtasks.")
        return value

class TaskUserDetailsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = TaskUserDetails
        fields = ('user', 'checked')

class TaskSerializer(serializers.ModelSerializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    user = TaskUserDetailsSerializer(source='user_statuses', many=True, read_only=True)
    subtasks = SubtaskSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = ('cardId', 'title', 'description', 'date', 'priority', 'category', 'status', 'user_ids', 'user', 'subtasks')

    def validate_user_ids(self, user_ids):
        """
        Validates a list of user IDs.

        Raises:
            serializers.ValidationError: If any user ID does not exist.
        """
        for user_id in user_ids:
            if not CustomUser.objects.filter(id=user_id).exists():
                raise serializers.ValidationError(f"Invalid user ID: {user_id}")
        return user_ids

    def create(self, validated_data):
        """
        Creates a new task.

        Creates a new task with the validated data.

        Assigns the task to the users with the IDs provided in the validated data.

        Replaces the subtasks of the task with the subtasks provided in the validated data.

        :return: The created task.
        """
        subtasks_data = validated_data.pop('subtasks', [])
        user_ids = validated_data.pop('user_ids', [])

        task = Task.objects.create(**validated_data)
        self._assign_task_users(task, user_ids)
        self._assign_subtasks(task, subtasks_data)

        return task

    def update(self, instance, validated_data):
        """
        Updates an existing task.

        Updates an existing task with the validated data.

        Assigns the task to the users with the IDs provided in the validated data.

        Replaces the subtasks of the task with the subtasks provided in the validated data.

        :return: The updated task.
        """
        subtasks_data = validated_data.pop('subtasks', [])
        user_ids = validated_data.pop('user_ids', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._assign_task_users(instance, user_ids)
        self._assign_subtasks(instance, subtasks_data)

        return instance

    def _assign_task_users(self, task, user_ids):
        """
        Assigns the task to the users with the IDs provided in user_ids.

        First clears any existing user assignments, then creates new TaskUserDetails
        objects for each user ID in user_ids.
        """
        task.user.clear()
        TaskUserDetails.objects.bulk_create([
            TaskUserDetails(task=task, user_id=user_id, checked=True) for user_id in user_ids
        ])

    def _assign_subtasks(self, task, subtasks_data):
        """
        Replaces the subtasks of the task with the subtasks provided in subtasks_data.

        First deletes any existing subtasks, then creates new Subtask objects for each
        subtask dictionary in subtasks_data.
        """
        Subtask.objects.filter(task=task).delete()
        Subtask.objects.bulk_create([
            Subtask(task=task, **subtask_data) for subtask_data in subtasks_data
        ])