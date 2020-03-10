from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from process.models import TaskSchedule
from masters.models import Customer

from .serializers import TriggerSerializer


class Trigger(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TriggerSerializer(data=request.data)
        if serializer.is_valid():
            print(request.user.id)
            customer = Customer.objects.get(id=request.user.id)
            api_task = TaskSchedule(
            cust_id=customer,
            task_id=request.data['task_id'],
            bot_id=request.data['bot_id'],
            status='N')
            api_task.save()

            return Response({"Status": "In Progress"}, status=status.HTTP_200_OK)
        else:
            return Response({"Validation Message": "Unable to proceed without Mandatory Fields"},
                            status=status.HTTP_400_BAD_REQUEST)
