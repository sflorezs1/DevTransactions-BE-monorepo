from abc import ABC, abstractmethod

class SecretsAdapter(ABC):
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass