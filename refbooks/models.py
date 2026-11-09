from django.db import models
from django.utils import timezone


class RefBook(models.Model):
    code = models.CharField("Код", max_length=100, unique=True)
    name = models.CharField("Наименование", max_length=300)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def get_current_version(self) -> "Version | None":
        today = timezone.now().date()
        return self.versions.filter(start_date__lte=today).order_by("-start_date").first()


class Version(models.Model):
    refbook = models.ForeignKey(RefBook, on_delete=models.CASCADE, related_name="versions", verbose_name="Справочник")
    version = models.CharField("Версия", max_length=50)
    start_date = models.DateField("Дата начала")

    class Meta:
        verbose_name = "Версия справочника"
        verbose_name_plural = "Версии справочников"
        constraints = [
            models.UniqueConstraint(fields=["refbook", "version"], name="unique_refbook_version"),
            models.UniqueConstraint(fields=["refbook", "start_date"], name="unique_refbook_start_date"),
        ]

    def __str__(self) -> str:
        return f"{self.refbook.code} - {self.version}"


class Element(models.Model):
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name="elements", verbose_name="Версия")
    code = models.CharField("Код элемента", max_length=100)
    value = models.CharField("Значение элемента", max_length=300)

    class Meta:
        verbose_name = "Элемент справочника"
        verbose_name_plural = "Элементы справочника"
        constraints = [
            models.UniqueConstraint(fields=["version", "code"], name="unique_version_element_code"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.value}"
