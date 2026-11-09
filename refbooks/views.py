import datetime

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import RefBook, Version
from .serializers import ElementSerializer, RefBookSerializer


class RefBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RefBook.objects.all()
    serializer_class = RefBookSerializer

    @extend_schema(
        summary="Получение списка справочников",
        description="""Возвращает список справочников. Если указан `date`, то только те справочники,
у которых есть версия с датой начала действия раньше или равной указанной.

Пример запроса: `GET /refbooks/?date=2022-10-01`

Пример ответа:
```
{
    "refbooks": [
        {"id": 1, "code": "MS1", "name": "Специальности медицинских работников"},
        {"id": 2, "code": "ICD-10", "name": "Международный классификатор заболеваний МКБ-10"}
    ]
}
```""",
        parameters=[
            OpenApiParameter("date", OpenApiTypes.DATE, description="Дата начала действия в формате ГГГГ-ММ-ДД"),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        date = request.query_params.get("date")
        if date:
            try:
                date = datetime.date.fromisoformat(date)
            except ValueError:
                return Response(
                    {"detail": "Неверный формат даты, ожидается YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(versions__start_date__lte=date)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"refbooks": serializer.data})

    @extend_schema(
        summary="Получение элементов заданного справочника",
        description="""Возвращает элементы указанной версии справочника.
Если версия не указана - элементы текущей версии.

Пример запроса: `GET /refbooks/1/elements/?version=1.0`

Пример ответа:
```
{
    "elements": [
        {"code": "1", "value": "Врач-терапевт"},
        {"code": "2", "value": "Травматолог-ортопед"},
        {"code": "3", "value": "Хирург"}
    ]
}
```""",
        parameters=[
            OpenApiParameter("version", str, description="Версия справочника"),
        ],
        responses=ElementSerializer(many=True),
    )
    @action(detail=True, methods=["get"])
    def elements(self, request, pk=None):
        version = self._get_version(self.get_object(), request.query_params.get("version"))
        serializer = ElementSerializer(version.elements.all(), many=True)
        return Response({"elements": serializer.data})

    @extend_schema(
        summary="Валидация элемента справочника",
        description="""Проверяет, что элемент с данным кодом и значением есть в указанной версии справочника.
Если версия не указана - проверяется текущая версия.

Пример запроса: `GET /refbooks/1/check_element/?code=1&value=Врач-терапевт`

Пример ответа:
```
{"exists": true}
```""",
        parameters=[
            OpenApiParameter("code", str, required=True),
            OpenApiParameter("value", str, required=True),
            OpenApiParameter("version", str, description="Версия справочника"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["get"])
    def check_element(self, request, pk=None):
        code = request.query_params.get("code")
        value = request.query_params.get("value")
        if not code or not value:
            return Response({"detail": "Параметры code и value обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        version = self._get_version(self.get_object(), request.query_params.get("version"))
        exists = version.elements.filter(code=code, value=value).exists()
        return Response({"exists": exists})

    def _get_version(self, refbook: RefBook, version: str | None) -> Version:
        """Returns requested version or current one if version is not passed"""
        if version:
            return get_object_or_404(refbook.versions, version=version)

        current_version = refbook.get_current_version()
        if current_version is None:
            raise NotFound("У справочника нет актуальной версии")
        return current_version
