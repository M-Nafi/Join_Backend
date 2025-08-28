from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ContactSerializer, TaskSerializer, SubtaskSerializer
from ..models import Contact, Task, Subtask
from rest_framework.exceptions import ValidationError

class ContactList(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of Contact objects associated with the user of the
        current request.
        """
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creates a new contact.

        Associates the contact with the user of the current request.

        """
        try:
            serializer.save(user=self.request.user)
        except ValidationError as e:
            print("Validation Error Details:", e.detail)
            raise Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns a queryset of Contact objects associated with the user of the
        current request.
        """
        return Contact.objects.filter(user=self.request.user)

class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of Task objects associated with the user of the
        current request.
        
        If the user is a guest, only returns tasks created by the user.
        """
        user = self.request.user
        if user.is_guest:
            return Task.objects.filter(created_by=user)
        return Task.objects.filter(created_by=user)

    def perform_create(self, serializer):
        """
        Creates a new task.

        Saves the task with the validated data from the serializer and associates
        the task with the user of the current request.

        """
        serializer.save(created_by=self.request.user)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'cardId'

    def get_queryset(self):
        """
        Returns a queryset of Task objects associated with the user of the
        current request.

        Only returns tasks created by the user.
        """
        return Task.objects.filter(created_by=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        """
        Partially updates a task.

        If the request data contains a 'status' key, the task's status is
        updated to the provided value. If the 'status' key is present but has
        no value, a 400 Bad Request response is returned.

        If the request data does not contain a 'status' key, the task is updated
        as per the standard Django Rest Framework partial update implementation.

        """
        instance = self.get_object()
        if 'status' in request.data:
            status_value = request.data.get('status')
            if not status_value:
                return Response(
                    {"error": "Status field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.status = status_value
            instance.save()
            return Response(
                {"message": "Status updated successfully", "status": instance.status}
            )
        
        return super().partial_update(request, *args, **kwargs)

class SubtaskList(generics.ListCreateAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of Subtask objects associated with the task identified
        by the 'cardId' URL parameter.

        Only returns subtasks associated with the task created by the user of the
        current request.

        """
        task = self._get_task()
        return Subtask.objects.filter(task=task)

    def perform_create(self, serializer):
        """
        Creates a new subtask.

        Saves the subtask with the validated data from the serializer and associates
        the subtask with the task identified by the 'cardId' URL parameter.

        Only creates subtasks associated with the task created by the user of the
        current request.

        """
        task = self._get_task()
        serializer.save(task=task)

    def _get_task(self):
        """
        Returns a Task object associated with the user of the current request and
        identified by the 'cardId' URL parameter.

        :raises: Http404 if the task does not exist
        """
        task_id = self.kwargs.get('cardId')
        user = self.request.user
        return get_object_or_404(Task, cardId=task_id, created_by=user)

class SubtaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        """
        Partially updates a subtask.

        If the request data is valid, the subtask associated with the task
        identified by the 'cardId' URL parameter is updated with the provided
        data.

        Returns a 200 OK response if the subtask is successfully updated, or a
        400 Bad Request response if the data is invalid.

        """
        task = self._get_task()
        subtask = self._get_subtask(task)
        serializer = self.serializer_class(subtask, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_task(self):
        """
        Returns a Task object associated with the user of the current request and
        identified by the 'cardId' URL parameter.

        :raises: Http404 if the task does not exist
        """
        task_id = self.kwargs.get('cardId')
        return get_object_or_404(Task, cardId=task_id, created_by=self.request.user)

    def _get_subtask(self, task):
        """
        Returns a Subtask object associated with the task identified by the 'cardId'
        URL parameter and the user of the current request.

        :raises: Http404 if the subtask does not exist
        """
        subtask_id = self.kwargs.get('id')
        user = self.request.user
        return get_object_or_404(Subtask, id=subtask_id, task=task)