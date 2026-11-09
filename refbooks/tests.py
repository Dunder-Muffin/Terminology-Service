import pytest
from rest_framework.test import APIClient

from .models import Element, RefBook, Version


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def refbook(db):
    refbook = RefBook.objects.create(code="MS1", name="Специальности медицинских работников")
    other = RefBook.objects.create(code="ICD-10", name="МКБ-10")
    Version.objects.create(refbook=other, version="1.0", start_date="2022-10-01")

    v1 = Version.objects.create(refbook=refbook, version="1.0", start_date="2022-01-01")
    v2 = Version.objects.create(refbook=refbook, version="2.0", start_date="2030-01-01")

    Element.objects.create(version=v1, code="1", value="Врач-терапевт")
    Element.objects.create(version=v1, code="2", value="Травматолог-ортопед")
    Element.objects.create(version=v2, code="1", value="Врач-терапевт")
    Element.objects.create(version=v2, code="2", value="Травматолог-ортопед")
    Element.objects.create(version=v2, code="3", value="Хирург")
    return refbook


def test_refbooks_list(api_client, refbook):
    response = api_client.get("/refbooks/")

    assert response.status_code == 200
    assert len(response.json()["refbooks"]) == 2
    assert response.json()["refbooks"][0] == {
        "id": refbook.id,
        "code": "MS1",
        "name": "Специальности медицинских работников",
    }


def test_refbooks_list_by_date(api_client, refbook):
    response = api_client.get("/refbooks/?date=2022-06-01")

    assert response.status_code == 200
    assert [r["code"] for r in response.json()["refbooks"]] == ["MS1"]


def test_refbooks_list_wrong_date(api_client, refbook):
    response = api_client.get("/refbooks/?date=01.06.2022")

    assert response.status_code == 400


def test_elements_current_version(api_client, refbook):
    response = api_client.get(f"/refbooks/{refbook.id}/elements/")

    assert response.status_code == 200
    assert response.json()["elements"] == [
        {"code": "1", "value": "Врач-терапевт"},
        {"code": "2", "value": "Травматолог-ортопед"},
    ]


def test_elements_by_version(api_client, refbook):
    response = api_client.get(f"/refbooks/{refbook.id}/elements/?version=2.0")

    assert response.status_code == 200
    assert len(response.json()["elements"]) == 3


def test_elements_refbook_not_found(api_client, db):
    response = api_client.get("/refbooks/999/elements/")

    assert response.status_code == 404


def test_check_element(api_client, refbook):
    response = api_client.get(f"/refbooks/{refbook.id}/check_element/?code=1&value=Врач-терапевт")

    assert response.status_code == 200
    assert response.json() == {"exists": True}


def test_check_element_not_in_current_version(api_client, refbook):
    # Хирург is only in version 2.0
    response = api_client.get(f"/refbooks/{refbook.id}/check_element/?code=3&value=Хирург")
    assert response.json() == {"exists": False}

    response = api_client.get(f"/refbooks/{refbook.id}/check_element/?code=3&value=Хирург&version=2.0")
    assert response.json() == {"exists": True}


def test_check_element_without_params(api_client, refbook):
    response = api_client.get(f"/refbooks/{refbook.id}/check_element/")

    assert response.status_code == 400
