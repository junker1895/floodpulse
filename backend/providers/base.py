from typing import Protocol


class ProviderObservation(dict):
    pass


class Provider(Protocol):
    def fetch_observations(self) -> list[ProviderObservation]:
        ...
