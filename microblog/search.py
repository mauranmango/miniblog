from flask import current_app


def add_to_index(index, model):            # model -> eshte modeli i sqlalchemy
    if not current_app.elasticsearch:      # Ne qofte se elasticsearch URL nuk eshte konfiguruar kthehet menjehere
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, document=index, id=model.id, body=payload)  # indeksojme blog postin ne elasticsearch


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, document=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    # multi_match mund te ekzekutoje queryn ne disa fields brenda objektit. Ne rastin tone te gjitha
    search = current_app.elasticsearch.search(index='index', document=index,
                                              body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                                                    'from': (page - 1) * per_page, 'size': per_page})
    # Ekstraktojme vetem id nga rezultatet e kerkimit
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']
    