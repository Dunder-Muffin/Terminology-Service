from rest_framework import serializers

from .models import Element, RefBook


class RefBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefBook
        fields = ["id", "code", "name"]


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ["code", "value"]
