## Knotis External API Documentation

# Identity API

/identity/identity/:
    POST:
        description:
            Creates a new identity with the specified fields.

        parameters:
            identity_type (integer)
            name (string)
            description (string)
            primary_image (id->media.image)

        return:
            identity_id (id->identity.identity)
            identity_name (string)
            errors ({string, string})
            message (string)

    GET:
        description:
            Gets the identities available to the provided user id.

        parameters:
            user_id (id->auth.user)

        return:
            identities ([identity.identity])
            errors ({string, string})
            message (string)

    PUT:
        description:
            updates the identity instance with the specified id with
            the parameters specified.

        parameters:
            id (id->identity.identity)
            identity_type (integer)
            name (string)
            description (string)
            primary_image (id->media.image)

        return:
            errors ({string, string})
            message (string)

    DELETE:
        description:
            Removes the specified resource from being aggregated by the system.

        parameters:
            id (id->identity.identity)

        return:
            errors ({string, string})
            message (string)

/identity/individual/:
    POST:
        description:
            Creates a new individual identity with the specified fields and 
            creates an individual relation from the user with the specified
            id to the new identity.

        parameters:
            name (string)
            description (string)
            primary_image (id->media.image)
            user_id (id->auth.user)

        return:
            individual_id (id->identity.identity)
            individual_name (string)
            errors ({string, string})
            message (string)

    GET:
        description:
            Gets the individual identities available to the provided user id.

        parameters:
            user_id (id->auth.user)

        return:
            individuals ([identity.identity])
            errors ({string, string})
            message (string)

    PUT:
        description:
            updates the individual identity instance with the specified id with
            the parameters specified.

        parameters:
            id (id->identity.identity)
            name (string)
            description (string)
            primary_image (id->media.image)

        return:
            errors ({string, string})
            message (string)

    DELETE:
        description:
            Removes the specified resource from being aggregated by the system.

        parameters:
            id (id->identity.identity)

        return:
            errors ({string, string})
            message (string)

/identity/business/:
    POST:
        description:
            Creates a new business identity with the specified fields and 
            creates an manager relation from the individual with the specified
            id to the new identity.

        parameters:
            name (string)
            description (string)
            primary_image (id->media.image)
            individual_id (id->identity.identity)

        return:
            business_id (id->identity.identity)
            business_name (string)
            errors ({string, string})
            message (string)

    GET:
        description:
            Gets the business managed by the provided individual id.

        parameters:
            individual_id (id->identity.identity)

        return:
            businesses ([identity.identity])
            errors ({string, string})
            message (string)

    PUT:
        description:
            updates the business identity instance with the specified id with
            the parameters specified.

        parameters:
            id (id->identity.identity)
            name (string)
            description (string)
            primary_image (id->media.image)

        return:
            errors ({string, string})
            message (string)

    DELETE:
        description:
            Removes the specified resource from being aggregated by the system.

        parameters:
            id (id->identity.identity)

        return:
            errors ({string, string})
            message (string)

/identity/establishment/:
    POST:
        description:
            Creates a new establishment identity with the specified fields and 
            creates an establishment relation from the business with the specified
            id to the new identity.

        parameters:
            name (string)
            description (string)
            primary_image (id->media.image)
            business_id (id->identity.identity)

        return:
            establishment_id (id->identity.identity)
            establishment_name (string)
            errors ({string, string})
            message (string)

    GET:
        description:
            Gets the establishment identities available to the provided user id.

        parameters:
            business_id (id->identity.identity)

        return:
            establishments ([identity.identity])
            errors ({string, string})
            message (string)

    PUT:
        description:
            updates the establishment identity instance with the specified id with
            the parameters specified.

        parameters:
            id (id->identity.identity)
            name (string)
            description (string)
            primary_image (id->media.image)

        return:
            errors ({string, string})
            message (string)

    DELETE:
        description:
            Removes the specified resource from being aggregated by the system.

        parameters:
            id (id->identity.identity)

        return:
            errors ({string, string})
            message (string)
