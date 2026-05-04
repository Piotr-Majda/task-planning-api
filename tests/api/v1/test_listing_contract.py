import pytest


def _task_payload(idx: int) -> dict:
    return {
        "name": f"Task {idx:02d}",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
    }


def _project_payload(idx: int) -> dict:
    return {
        "name": f"Project {idx:02d}",
    }


def _user_payload(idx: int) -> dict:
    return {
        "name": f"User {idx:02d}",
    }


RESOURCE_SPECS = [
    ("tasks", _task_payload),
    ("projects", _project_payload),
    ("users", _user_payload),
]


@pytest.fixture(params=RESOURCE_SPECS, ids=["tasks", "projects", "users"])
def resource_spec(request):
    return request.param


@pytest.fixture
def endpoint(resource_spec) -> str:
    return resource_spec[0]


@pytest.fixture
def payload_factory(resource_spec):
    return resource_spec[1]


@pytest.fixture
def create_resources(client, endpoint: str, payload_factory):
    def _create(count: int):
        created = []
        for idx in range(count):
            response = client.post(f"/api/v1/{endpoint}", json=payload_factory(idx))
            assert response.status_code == 200, response.json()
            created.append(response.json())
        return created
    return _create


@pytest.fixture
def given_single_resource(create_resources):
    return create_resources(1)


@pytest.fixture
def given_eleven_resources(create_resources):
    return create_resources(11)


@pytest.fixture
def given_twelve_resources(create_resources):
    return create_resources(12)


@pytest.fixture
def given_search_focus_resources(client, endpoint: str, payload_factory, create_resources):
    create_resources(8)

    alpha = client.post(f"/api/v1/{endpoint}", json={**payload_factory(50), "name": "Alpha Focus"})
    beta = client.post(f"/api/v1/{endpoint}", json={**payload_factory(51), "name": "Beta Focus"})
    other = client.post(f"/api/v1/{endpoint}", json={**payload_factory(52), "name": "Other Name"})
    assert alpha.status_code == 200, alpha.json()
    assert beta.status_code == 200, beta.json()
    assert other.status_code == 200, other.json()

    return [alpha, beta, other]


def test_listing_contract__default_pagination__returns_first_ten_sorted_by_name(client, endpoint, given_eleven_resources):
    response = client.get(f"/api/v1/{endpoint}")
    assert response.status_code == 200, response.json()

    body = response.json()
    assert len(body) == 10

    expected_names = sorted([item["name"] for item in given_eleven_resources])[:10]
    present_names = [item["name"] for item in body]
    assert present_names == expected_names


def test_listing_contract__page_zero__returns_422(client, endpoint, given_single_resource):

    response = client.get(f"/api/v1/{endpoint}?page=0")
    assert response.status_code == 422, response.json()


def test_listing_contract__limit_zero__returns_422(client, endpoint, given_single_resource):

    response = client.get(f"/api/v1/{endpoint}?limit=0")
    assert response.status_code == 422, response.json()


def test_listing_contract__limit_above_hundred__returns_422(client, endpoint, given_single_resource):

    response = client.get(f"/api/v1/{endpoint}?limit=101")
    assert response.status_code == 422, response.json()


def test_listing_contract__name_sort_desc__returns_ten_items_in_desc_order(client, endpoint, given_twelve_resources):

    response = client.get(f"/api/v1/{endpoint}?sort=name&order=desc")
    assert response.status_code == 200, response.json()

    body = response.json()
    assert len(body) == 10

    expected_names = sorted([item["name"] for item in given_twelve_resources], reverse=True)[:10]
    present_names = [item["name"] for item in body]
    assert present_names == expected_names


def test_listing_contract__invalid_order_value__returns_422(client, endpoint, given_single_resource):

    response = client.get(f"/api/v1/{endpoint}?order=invalid")
    assert response.status_code == 422, response.json()


def test_listing_contract__search_by_token__returns_matching_sorted_names(client, endpoint, given_search_focus_resources):

    response = client.get(f"/api/v1/{endpoint}?search=Focus")
    assert response.status_code == 200, response.json()

    present_names = [item["name"] for item in response.json()]
    assert present_names == ["Alpha Focus", "Beta Focus"]


def test_listing_contract__search_with_forbidden_character__returns_422(client, endpoint, given_single_resource):

    response = client.get(f"/api/v1/{endpoint}?search=<")
    assert response.status_code == 422, response.json()
