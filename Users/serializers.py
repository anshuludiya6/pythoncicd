from rest_framework import serializers
from .models import *

class BankInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankInformation
        # fields = '__all__'
        exclude = ['created_by', 'created_on', 'updated_by', 'updated_on', 'is_deleted']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['created_by', 'updated_by', 'updated_on', 'is_deleted']

class ExperienceInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceInformation
        exclude = ['created_by', 'created_on','updated_by', 'updated_on', 'is_deleted']

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        exclude = ['created_by', 'updated_by', 'created_on', 'updated_on', 'is_deleted']

