from django.core.management.base import BaseCommand, CommandError

from app.models.contents import Content
from optparse import make_option

from django.contrib.auth.models import User#, Group

import re

class Command(BaseCommand):

    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    option_list = BaseCommand.option_list + (
        make_option('-i',
                    '--input_html',
                    help='Input Html file.',
                    dest='input_html',
                    metavar='INPUT HTML'),

        make_option('-o',
                    '--output_html',
                    help='Output Html file.',
                    dest='output_html',
                    metavar='OUTPUT HTML'),
    )

    def handle(self, *args, **options):

        # Todo:
        #   Assign Parent appropriately.
        #   Assign User appropriately.
        #   Assign backend (template name)
        #   Type of content.

        input_html = options['input_html']
        output_html = options['output_html']

        input_html = open(input_html, 'r')
        output_html = open(output_html, 'w')

        input_contents = input_html.read()

        # This is simlay.
        user = User.objects.get(pk="fa612ae0-253d-435c-8746-a6278e4c03cd")
        backend_name = 'test'
        content_root = None

        # To make each name unique.
        paragraph_content_count = 1
        url_content_count = 1
        url_count = 1

        # Look at each paragraph,  look for hyper links and handle appropriately.
        paragraph_matches = re.findall('<p[^>]*>.*</p>', input_contents)
        print paragraph_matches
        for i in paragraph_matches:
            print i
            m = re.search('(?P<p_tag><p[^>]*>)(?P<content>.*)</p>', i)

            paragraph_contents = m.group('content')

            # Django exception!
            if re.search('{%.*%}|{{.*}}', paragraph_contents) != None:
                continue

            # Are there urls in this paragraph?
            paragraph_urls = re.findall('<a href="[^"]*">.*</a>', paragraph_contents)

            if len(paragraph_urls) > 0:

                for j in paragraph_urls:

                    url = re.search('<a href="(?P<url>[^"]*)">(?P<url_content>.*)</a>', j).group('url')
                    url_new = Content(
                        content_type='1.2',
                        user=user,
                        name = backend_name + '_url_' + str(url_count),
                        parent=content_root,
                        value=url
                    )
                    url_new.save()
                    url_count += 1
                    paragraph_contents = paragraph_contents.replace(url, "{{ %s }}" % url_new.name)

                paragraph_content_new = Content(
                    content_type='1.2',
                    user=user,
                    name = backend_name + '_paragrah_html_' + str(paragraph_content_count) + '|safe',
                    parent=content_root,
                    value=paragraph_contents
                )

                paragraph_content_new.save()

            # No url in this paragraph
            else:

                paragraph_content_new = Content(
                    content_type='1.2',
                    user=user,
                    name = backend_name + '_content_' + str(paragraph_content_count),
                    parent=content_root,
                    value=paragraph_contents
                )

                paragraph_content_new.save()

            replacement_text = '%s{{ %s }}</p>' % (m.group('p_tag'), paragraph_content_new.name)

            paragraph_content_count += 1
            input_contents = input_contents.replace(i, replacement_text, 1)

        # The hyper links outside of paragraphs.
        href_matches = re.findall('<a href="[^"]*">.*</a>', input_contents)

        for i in href_matches:

            # Django exception!
            if re.search('{%.*%}|{{.*}}', i) != None:
                continue

            m = re.search('<a href="(?P<url>[^"]*)">(?P<url_content>.*)</a>', i)

            url = m.group('url')
            url_content = m.group('url_content')

            url_content_new = Content(
                content_type='1.2',
                user=user,
                name = backend_name + '_url_content_' + str(url_content_count),
                #parent=content_root,
                value=url_content
            )
            url_content_new.save()

            url_new = Content(
                content_type='1.2',
                user=user,
                name = backend_name + '_url_' + str(url_count),
                #parent=content_root,
                value=url
            )
            url_new.save()

            input_contents = input_contents.replace(i,
                    '<a href="{{ %s }}">{{ %s }} </a>' % ( url_new.name, url_content_new.name))

            url_content_count += 1
            url_count += 1

        input_html.close()

        output_html.write(input_contents)
        output_html.close()
