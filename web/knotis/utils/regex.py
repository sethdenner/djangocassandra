REGEX_UUID = (
    '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
)


REGEX_BACKEND_NAME = (
    '[a-zA-Z]+[a-zA-Z0-9-_]*'
)


REGEX_CATEGORY = (
    'tra|sho|res|rea|pub|pro|'
    'pet|nig|leg|hom|hea|foo|'
    'fin|edu|bea|aut|art|all'
)


REGEX_NOT_CATEGORY_PREVIOUS = ''.join([
    '(?<!',
    REGEX_CATEGORY,
    ')'
])


REGEX_OFFER_FILTERING = ''.join([
    '(/(?P<business>',
    REGEX_BACKEND_NAME,
    REGEX_NOT_CATEGORY_PREVIOUS,
    '(?<!premium)))?(/(?P<category>',
    REGEX_CATEGORY,
    '))?(/(?P<premium>premium))?',
    '(/(?P<page>[\d]+))?',
])
