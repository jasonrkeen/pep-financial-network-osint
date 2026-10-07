"""Source ancestry is explicit. Shared ancestry cannot corroborate itself."""


def split_ids(value):
    return [item.strip() for item in value.split(';') if item.strip()]


def roots(source_id, sources, visiting=None):
    visiting = set() if visiting is None else visiting
    if source_id in visiting:
        raise ValueError('source-lineage cycle: ' + source_id)
    if source_id not in sources:
        raise ValueError('missing lineage source: ' + source_id)
    parents = split_ids(sources[source_id]['derived_from'])
    if not parents:
        return {source_id}
    result = set()
    for parent in parents:
        result |= roots(parent, sources, visiting | {source_id})
    return result


def independent_roots(source_ids, sources):
    result = set()
    for source_id in split_ids(source_ids):
        result |= roots(source_id, sources)
    return result
