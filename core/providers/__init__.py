"""
OmniDirector AI — Provider Factory
"""
from core.config import config
from core.providers.base import BaseOmniProvider
from core.providers.simulation_provider import SimulationOmniProvider
from core.providers.meta_provider import MetaModelAPIProvider
from core.providers.baseten_provider import BasetenOmniProvider

def get_active_provider() -> BaseOmniProvider:
    if config.meta_api_key and not config.meta_api_key.startswith("your_"):
        return MetaModelAPIProvider()
    if config.baseten_api_key and not config.baseten_api_key.startswith("your_"):
        return BasetenOmniProvider()
    return SimulationOmniProvider()
