from backend.config import settings
from backend.providers.mock_provider import MockProvider
from backend.providers.bom_provider import BomProvider


def get_provider():
    if settings.provider == 'bom':
        return BomProvider()
    return MockProvider()
