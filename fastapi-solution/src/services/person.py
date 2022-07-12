import json
from functools import lru_cache
from typing import Tuple, Union

from api.v1.films import FilmRating
from db.elastic_queries import *
from fastapi import Depends
from models.film import FilmFull
from models.person import Person
from pkg.cache_storage.redis_storage import get_redis_storage_service
from pkg.cache_storage.storage import ABSCacheStorage
from pkg.storage.elastic_storage import get_elastic_storage_service
from pkg.storage.storage import ABSStorage
from services.films import FilmService


class PersonService:

    def __init__(self, elastic: ABSStorage, cache_storage: ABSCacheStorage):
        self.cache_storage = cache_storage
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """Получение персоны по ID.

        :param person_id: str
        :return: Optional[Person]
        """
        cashed_data = await self.cache_storage.get_data(key=person_id)
        if cashed_data:
            person = Person.parse_raw(cashed_data)
            return person

        doc = await self.elastic.get_by_id(id=person_id, index_name='person')

        if not doc:
            return None
        person = Person(**doc['_source'])
        await self.cache_storage.set_data(key=f"{person_id}", data=json.dumps(doc['_source']))

        return person

    async def get_list(self,
                       page_size: int,
                       offset_from: int,
                       ) -> Union[Tuple[Optional[int], Optional[List[Person]]], None]:
        """Получение списка персон.

        :param page_size: int
        :param offset_from: int
        :return:List[Person]
        """

        cashed_data = await self.cache_storage.get_data(key=f'person_list{page_size}{offset_from}')
        if cashed_data:
            person_list = [Person(**d['_source']) for d in json.loads(cashed_data.decode('utf8'))['data']]
            total = json.loads(cashed_data.decode('utf8'))['total']
            return total, person_list

        query = match_query(match_value={"match_all": {}}, offset_from=offset_from, page_size=page_size)
        elastic_response = await self.elastic.search(index_name='person', query=json.dumps(query))
        total = elastic_response['hits']['total']['value']
        person_list = [Person(**p['_source']) for p in elastic_response['hits']['hits']]

        redis_json = {
            'total': total,
            'data': elastic_response['hits']['hits']
        }
        await self.cache_storage.set_data(
            key=f'person_list{page_size}{offset_from}',
            data=json.dumps(redis_json))

        if not person_list:
            return None, None

        return total, person_list

    async def get_by_name(self,
                          name: str,
                          page_size: int,
                          offset_from: int) -> Union[Tuple[Optional[int], Optional[List[Person]]], None]:
        """Поиск персон по имени.

        :param name: str
        :param page_size: int
        :param offset_from: int
        :return: Optional[List[Person], None]
        """

        cashed_data = await self.cache_storage.get_data(key=f'person_{name}_{page_size}{offset_from}')
        if cashed_data:
            person_list = [Person(**d['_source']) for d in json.loads(cashed_data.decode('utf8'))['data']]
            total = json.loads(cashed_data.decode('utf8'))['total']
            return total, person_list

        query = match_query(match_value={"match": {'full_name': name}},
                            offset_from=offset_from,
                            page_size=page_size)
        elastic_response = await self.elastic.search(index_name='person', query=json.dumps(query))
        total = elastic_response['hits']['total']['value']
        person_list = [Person(**p['_source']) for p in elastic_response['hits']['hits']]

        redis_json = {
            'total': total,
            'data': elastic_response['hits']['hits']
        }
        await self.cache_storage.set_data(
            key=f'person_{name}_{page_size}{offset_from}',
            data=json.dumps(redis_json))

        if not person_list:
            return None, None

        return total, person_list

    async def get_film_by_person(
            self,
            film_service: FilmService,
            person_id: str,
            roles: list,
            page_size: int = 10,
            offset_from: int = 0) -> Union[Tuple[Optional[int], Optional[List[FilmFull]]], Tuple[None, None]]:
        """Поиск персон по имени.

        :param person_id: str
        :param roles
        :param film_service: FilmService
        :param page_size: int
        :param offset_from: int
        :return: Optional[List[FilmFull]]
        """
        cashed_key = "film_by_person_{}".format(
            '_'.join(
                filter(
                    None,
                    (
                        person_id,
                        str(offset_from),
                        str(page_size),
                        '_'.join(roles) if roles else None)
                )
            )
        )
        cashed_data = await self.cache_storage.get_data(key=cashed_key)
        if cashed_data:
            film_list = [FilmFull(**d['_source']) for d in json.loads(cashed_data.decode('utf8'))['data']]
            if not film_list and not 'subscription' in roles:
                total_count, films = await film_service.get_list(
                    name=None,
                    genres=None,
                    page_size=3,
                    page_number=1,
                    sort=FilmRating.desc,
                    roles=roles)
                if not film_list:
                    film_list = []
                film_list = film_list + films
            total = json.loads(cashed_data.decode('utf8'))['total']
            return total, film_list

        query = nested_query(condition="should",
                             nested_filter=[
                                 {"path": "actors", "value": {"actors.id": person_id}},
                                 {"path": "writers", "value": {"writers.id": person_id}},
                             ],
                             page_size=page_size,
                             offset_from=offset_from,
                             roles=roles
                             )
        elastic_response = await self.elastic.search(index_name='movies', query=json.dumps(query))
        total = elastic_response['hits']['total']['value']
        film_list = [FilmFull(**p['_source']) for p in elastic_response['hits']['hits']]

        if not film_list and not 'subscription' in roles:
            total_count, films = await film_service.get_list(
                name=None,
                genres=None,
                page_size=3,
                page_number=1,
                sort=FilmRating.desc,
                roles=roles)
            if not film_list:
                total = 0
                film_list = []
            film_list = film_list + films

        redis_json = {
            'total': total,
            'data': elastic_response['hits']['hits']
        }
        await self.cache_storage.set_data(
            key=cashed_key,
            data=json.dumps(redis_json))

        if not film_list:
            return None, None

        return total, film_list


@lru_cache()
def get_person_service(
        redis: ABSCacheStorage = Depends(get_redis_storage_service),
        elastic: ABSStorage = Depends(get_elastic_storage_service),
) -> PersonService:
    return PersonService(elastic, redis)
