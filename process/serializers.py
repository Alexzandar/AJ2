from rest_framework import serializers


class TriggerSerializer(serializers.Serializer):

    task_id = serializers.CharField(max_length=20)
    bot_id = serializers.CharField(max_length=20)
