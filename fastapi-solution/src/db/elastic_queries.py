from typing import List, Dict, Optional


def match_query(
        match_value: dict,
        offset_from: int,
        page_size: int,
        sort: dict = {}):
    """формирование запроса для elastic.

    Args:
        match_value:
        offset_from:
        page_size:
        sort:

    Returns:

    """

    body = {
        "bool": {
            "must": [],
            "should": [],
            "filter": []
        }
    }
    body['bool']['must'].append(match_value)
    query = {'query': body,
             "from": offset_from,
             "size": page_size,
             "sort": [sort],
             "aggs": {}
             }
    return query


def nested_query(
        condition: str,
        nested_filter: List[dict],
        offset_from: int,
        page_size: int,
        roles: Optional[List[str]] = None,
        must_not: list = None,
        sort: Optional[List[dict]] = None):
    def create_nested(filter_values: dict):
        return {
            "nested": {
                "path": filter_values['path'],
                "query": {
                    "bool": {
                        "must": [
                            {"match": filter_values['value']},
                        ]

                    }
                }
            }
        }

    if roles:
        if 'subscription' in roles:
            must_not = [{"range": {"imdb_rating": {'gte': '100'}}}]
        if 'not_subscription' in roles:
            must_not = [{"range": {"imdb_rating": {'gte': '7'}}}]
        if 'failed' in roles:
            must_not = [{"range": {"imdb_rating": {'gte': '6'}}}]
        if 'unauthorized' in roles:
            must_not = [{"range": {"imdb_rating": {'gte': '6'}}}]

    query = {
        "query": {
            "bool": {
                "must_not": must_not if must_not else [],
                condition: [create_nested(element) for element in nested_filter]
            }
        },
        "from": offset_from,
        "size": page_size,
        "sort": sort if sort else [],
    }
    return query
