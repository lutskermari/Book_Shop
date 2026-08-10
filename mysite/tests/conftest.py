import pytest


@pytest.fixture(autouse=True)
def disable_throttling(settings):
    """Автоматично вимикає rate limiting для всіх тестів."""
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
        "anon": None,
        "user": None,
    }
