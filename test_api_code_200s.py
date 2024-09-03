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
        status_forcelist=[status for status in range(201, 600)],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    yield session
    session.close()


@pytest.mark.parametrize("status_code, h1_text_expected", [
    (100, "100 Continue"),
    (202, "202 Accepted"),
    (303, "303 See Other"),
    (407, "407 Proxy Authentication Required"),
    (501, "501 Not Implemented")
])
def test_status_code(status_code, h1_text_expected, session):
    url = base_url + str(status_code)
    try:
        response = session.get(url, timeout=(1, 5))
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/html"
        soup = BeautifulSoup(response.text, "html.parser")
        h1_element = soup.select_one("h1.text-center.my-12")
        h1_text = h1_element.get_text()
        assert h1_text == h1_text_expected
    except requests.exceptions.Timeout as e:
        print(f'Timed out: {e}')
