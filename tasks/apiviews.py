from django.http import JsonResponse
from django.views import View
from django.http.response import HttpResponse

from tasks.models import Task, TaskHistory
from tasks.models import STATUS_CHOICES

from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from django.contrib.auth.models import User

from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    ChoiceFilter,
    BooleanFilter,
    DateFilter,
)

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username",]


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model=Task
        fields=['id', 'title','description','user', 'completed', 'status']

class TaskFilter(FilterSet):
    completed = BooleanFilter()

class TaskViewSet(ModelViewSet):
    queryset= Task.objects.all()
    serializer_class= TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user= self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskHistorySerializer(ModelSerializer):
    # task = TaskSerializer()

    class Meta:
        model = TaskHistory
        fields = ["oldstatus", "newstatus", "change_date" ]


class HistoryFilter(FilterSet):
    oldstatus = ChoiceFilter(choices=STATUS_CHOICES)
    newstatus = ChoiceFilter(choices=STATUS_CHOICES)
    # * https://django-filter.readthedocs.io/en/stable/ref/filters.html#method
    change_date = DateFilter(method="datefilter")

    def datefilter(self, queryset, name, value):
        return queryset.filter(
            updated_date__year=value.year,
            updated_date__month=value.month,
            updated_date__day=value.day,
        )


class TaskHistoryViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HistoryFilter

    def get_queryset(self):
        return TaskHistory.objects.filter(
            task_id=self.kwargs["task_pk"],
            user=self.request.user,
        )
#====================================================================
# class TaskListAPI(APIView):
#     def get(self, request):
#         tasks= Task.objects.filter(deleted=False)
#         data=TaskSerializer(tasks, many=True).data
#         return Response({"tasks":data})