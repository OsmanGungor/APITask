import requests
from bs4 import BeautifulSoup
import pytest
from requests.adapters import HTTPAdapter, Retry

base_url = "https://http.cat/status/"


@pytest.fixture(scope="session")
def session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[status for status in range(200, 600) if status != 403],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    yield session
    session.close()


def test_status_code_403(session):
    url = base_url
    try:
        response = session.get(url)
        assert response.status_code == 403
        assert response.headers["Content-Type"] == "text/html"
        soup = BeautifulSoup(response.text, "html.parser")
        assert soup.h1.text == "403 Forbidden"
    except requests.exceptions.Timeout as e:
        print(f'Timed out: {e}')
