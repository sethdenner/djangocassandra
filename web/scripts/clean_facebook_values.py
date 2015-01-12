from knotis.contrib.endpoint.models import EndpointFacebook


def clean_facebook_fields(output_file):
    with open(output_file, 'w') as f:
        for endpoint in EndpointFacebook.objects.all():

            try:  # Becasue some of these aren't going to be printable.
                f.write('%s, %s, %s, ' % (
                    endpoint.pk,
                    endpoint.value,
                    endpoint.get_uri()
                ))
            except:
                pass

            endpoint.clean()
            endpoint.save()
            try:  # Becasue some of these aren't going to be printable.
                f.write('%s, %s\n' % (
                    endpoint.value,
                    endpoint.get_uri()
                ))
            except:
                pass
