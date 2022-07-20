from abc import ABC, abstractmethod


class ABSStorage(ABC):

    @abstractmethod
    def send_to_ugc_storage(self, **kwargs):
        pass
