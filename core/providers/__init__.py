"""
OmniDirector AI — Provider Factory
"""
from core.config import config
from core.providers.base import BaseOmniProvider
from core.providers.simulation_provider import SimulationOmniProvider
from core.providers.meta_provider import MetaModelAPIProvider
from core.providers.baseten_provider import BasetenOmniProvider

def get_active_provider(provider_name: str = "") -> BaseOmniProvider:
    pref = (provider_name or config.primary_provider).lower()
    
    if "sim" in pref or "mock" in pref or "local" in pref:
        return SimulationOmniProvider()
    if "baseten" in pref and config.baseten_api_key and not config.baseten_api_key.startswith("your_"):
        return BasetenOmniProvider()
    if "meta" in pref and config.meta_api_key and not config.meta_api_key.startswith("your_"):
        return MetaModelAPIProvider()

    # Automatic fallback order if no specific match
    if config.baseten_api_key and not config.baseten_api_key.startswith("your_"):
        return BasetenOmniProvider()
    if config.meta_api_key and not config.meta_api_key.startswith("your_"):
        return MetaModelAPIProvider()
    return SimulationOmniProvider()
