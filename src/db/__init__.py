from abc import ABC, abstractmethod
from typing import Optional


class AbstractStorage(ABC):
    """
    Абстрактный класс для работы с хранилищем данных.
    Описывает какие методы должны быть у подобных классов.
    """

    @abstractmethod
    async def close(self):
        """
        Абстрактный асинхронный метод для закрытия соединения
        """
        ...

    @abstractmethod
    async def create_database(self):
        """
        Абстрактный асинхронный метод для создания таблиц бд
        """
        ...

    @abstractmethod
    async def purge_database(self):
        """
        Абстрактный асинхронный метод для удаления таблиц бд
        """
        ...


class AbstractCache(ABC):
    """
    Абстрактный класс для работы с кэшем.
    Описывает какие методы должны быть у подобных классов.
    :get_from_cache_by_id - возвращает один экземпляр класса модели,
    по которой строятся получение из кэша по id
    :get_from_cache_by_key - возвращает один экземпляр класса модели,
    по которой строятся получение из кэша по ключу
    :put_to_cache_by_id - кладет данные в кэш по id.
    :put_to_cache_by_key - кладет данные в кэш по ключу.
    """

    @abstractmethod
    async def close(self):
        """
        Абстрактный асинхронный метод для закрытия соединения
        """
        ...

    @abstractmethod
    async def get_from_cache_by_id(self, _id: str, model) -> Optional:
        """
        Абстрактный асинхронный метод для получения данных по id из кэша
        :param _id: строка с id, по которой выполняется поиск
        :param model: тип модели, в котором возвращаются данные
        :return: объект типа, заявленного в model
        """
        ...

    @abstractmethod
    async def put_to_cache_by_id(self, _id, entity, expire):
        """
        Абстрактный асинхронный метод, который кладет данные в кэш по id
        :param _id:
        :param entity: данные, которые кладем в кэш
        :param expire: время жизни записи
        """
        ...

    @abstractmethod
    async def get_from_cache_by_key(self,
                                    model,
                                    key: str = None,
                                    sort: str = None) -> list | None:
        """
        Абстрактный асинхронный метод для получения данных по ключу из кэша
        :param model: тип модели, в котором возвращаются данные
        :param key: по данному ключу получаем данные из кэша
        :param sort: строка с названием атрибута, по которой необходима
        сортировка
        """
        ...

    @abstractmethod
    async def put_to_cache_by_key(self,
                                  key: str = None,
                                  entities: list = None):
        """
        Абстрактный асинхронный метод, который кладет данные в кэш по ключу
        :param key: по данному ключу записываются данные в кэш
        :param entities: данные, которые кладем в кэш
        """
        ...
