

def apply_limit_and_offset(query, limit, offset):
    query = query.limit(limit)
    if offset > 0:
        query = query.offset(offset)
    return query
