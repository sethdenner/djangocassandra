from django.core.management.base import BaseCommand, CommandError

from app.models.contents import Content
from optparse import make_option

from django.contrib.auth.models import User

import re
import os

class Command(BaseCommand):

    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    option_list = BaseCommand.option_list + (
        make_option('-i',
                    '--input_dir',
                    help='Input template directory.',
                    dest='input_dir',
                    metavar='INPUT DIRCETORY'),

        make_option('-o',
                    '--output_dir',
                    help='Output Directory.',
                    dest='output_dir',
                    metavar='OUTPUT DIRECTORY'),
    )


    def handle(self, *args, **options):
        def scrape_file(input_html,
                        output_html,
                        user = User.objects.get(pk="fa612ae0-253d-435c-8746-a6278e4c03cd"),
                        parent = None,
                        backend_name = 'test',
                        ):
            input_html = open(input_html, 'r')
            output_html = open(output_html, 'w')

            input_contents = input_html.read()

            # This is simlay.
            #user = User.objects.get(pk="fa612ae0-253d-435c-8746-a6278e4c03cd")
            #backend_name = 'test'

            # To make each name unique.
            paragraph_content_count = 1
            url_content_count = 1
            url_count = 1

            # Look at each paragraph,  look for hyper links and handle appropriately.
            paragraph_matches = re.findall('<p[^>]*>.*</p>', input_contents)
            for i in paragraph_matches:
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
                            content_type='1.3',
                            user=user,
                            name = backend_name + '_url_' + str(url_count),
                            parent=parent,
                            value=url
                        )
                        url_new.save()

                        url_count += 1
                        paragraph_contents = paragraph_contents.replace(url, "{{ %s }}" % url_new.name)

                    paragraph_content_new = Content(
                        content_type='1.4',
                        user=user,
                        name = backend_name + '_paragrah_html_' + str(paragraph_content_count) + '|safe',
                        parent=parent,
                        value=paragraph_contents
                    )

                    paragraph_content_new.save()

                # No url in this paragraph
                else:

                    paragraph_content_new = Content(
                        content_type='1.2',
                        user=user,
                        name = backend_name + '_content_' + str(paragraph_content_count),
                        parent=parent,
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
                    parent=parent,
                    value=url_content
                )
                url_content_new.save()

                url_new = Content(
                    content_type='1.3',
                    user=user,
                    name = backend_name + '_url_' + str(url_count),
                    parent=parent,
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
            return

        # Todo:
        #   Assign Parent appropriately.
        #   Assign User appropriately.
        #   Assign backend (template name)
        #   Type of content.

        web_content_root = Content.objects.get(pk='9f5b072c-e1ed-4897-85ca-c87aa27c7d49')

        input_dir = options['input_dir']
        output_dir = options['output_dir']

        for dirname, dirnames, filenames in os.walk(input_dir):

            for subdirname in dirnames:
                dir = os.path.join(dirname, subdirname).replace(input_dir, output_dir)
                if not os.path.exists(dir):
                    os.makedirs(dir)

            for filename in filenames:
                input_html = os.path.join(dirname, filename)
                output_html = os.path.join(dirname.replace(input_dir, output_dir), filename)

                user = User.objects.get(pk="fa612ae0-253d-435c-8746-a6278e4c03cd")
                new_template = Content(
                    content_type='1.1',
                    user=user,
                    name=filename.replace('.html', ''),
                    parent=web_content_root,
                    value=input_html
                )

                new_template.save()

                scrape_file(input_html, output_html,
                        user, parent=new_template, backend_name = new_template.name)
