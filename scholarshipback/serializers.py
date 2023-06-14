from rest_framework import serializers

from .models import *


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'


class CompaingSerializer(serializers.ModelSerializer):
    startDate = serializers.DateTimeField(source='date_start')
    endDate = serializers.DateTimeField(source='date_end')

    class Meta:
        model = Compaing
        fields = ['id', 'name', 'startDate', 'endDate', 'show_student_points']


class CompaingSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Compaing
        fields = "__all__"


class DictLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = dictLevelProgress
        fields = ["name", 'id', 'dictprogress']


class DictStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = dictStatusProgress
        fields = ["name", 'id', 'dictprogress']


class DictViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = dictViewProgress
        fields = ["name", 'id', 'dictprogress']


class DictProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictProgress
        fields = ["name", 'id']


class NominationsSerializers(serializers.ModelSerializer):
    dict_level_progress = DictLevelSerializer(many=True, read_only=True)
    dict_status_progress = DictStatusSerializer(many=True, read_only=True)
    dict_view_progress = DictViewSerializer(many=True, read_only=True)
    dict_progress = DictProgressSerializer(many=True, read_only=True)

    class Meta:
        model = DictTypeMiracle
        fields = ['id', 'name', "dict_level_progress", "dict_status_progress", "dict_view_progress", "dict_progress"]


class CommentsSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    admin = AdminSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = "__all__"


class RequestSerializer(serializers.ModelSerializer):
    typeMiracle = NominationsSerializers(read_only=True)
    student = StudentSerializer(read_only=True)
    compaing = CompaingSerializer(read_only=True)
    comments = CommentsSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = "__all__"


class CreateNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['text']


class ListNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'text']


class DataInfoMiracleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataInfoMiracle
        exclude = ['id', 'point', 'type_micacle']


class BigBoysSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigBoys
        fields = "__all__"
