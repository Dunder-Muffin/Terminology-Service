from django.contrib import admin

from .models import Element, RefBook, Version


class VersionInline(admin.TabularInline):
    model = Version
    extra = 0


class ElementInline(admin.TabularInline):
    model = Element
    extra = 0


@admin.register(RefBook)
class RefBookAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "name", "current_version", "current_version_start_date"]
    search_fields = ["code", "name"]
    inlines = [VersionInline]

    @admin.display(description="Текущая версия")
    def current_version(self, obj):
        version = obj.get_current_version()
        return version.version if version else None

    @admin.display(description="Дата начала действия версии")
    def current_version_start_date(self, obj):
        version = obj.get_current_version()
        return version.start_date if version else None


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ["refbook_code", "refbook_name", "version", "start_date"]
    list_filter = ["refbook"]
    inlines = [ElementInline]

    @admin.display(description="Код справочника")
    def refbook_code(self, obj):
        return obj.refbook.code

    @admin.display(description="Наименование справочника")
    def refbook_name(self, obj):
        return obj.refbook.name


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ["code", "value", "version"]
    list_filter = ["version__refbook"]
