REGEX_UUID = (
    '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
)
REGEX_PASSWORD = (
    '[\w.@+-]+$'
)

REGEX_PROMO = (
    '[a-fA-Z0-9]{8}'
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

"""
Credit card regular expressions.
"""
REGEX_CC_VISA = '4[0-9]{12}(?:[0-9]{3})?'
REGEX_CC_MASTER_CARD = '5[1-5][0-9]{14}'
REGEX_CC_AMERICAN_EXPRESS = '3[47][0-9]{13}'
REGEX_CC_DINERS_CLUB = '3(?:0[0-5]|[68][0-9])[0-9]{11}'
REGEX_CC_DISCOVER = '6(?:011|5[0-9]{2})[0-9]{12}'
REGEX_CC_JCB = '(?:2131|1800|35\d{3})\d{11}'
REGEX_CC_ANY = '|'.join([
    REGEX_CC_VISA,
    REGEX_CC_MASTER_CARD,
    REGEX_CC_AMERICAN_EXPRESS,
    REGEX_CC_DINERS_CLUB,
    REGEX_CC_DISCOVER,
    REGEX_CC_JCB
])
