import os

from django.conf import settings
from django import template
register = template.Library()


@register.tag(name='render_static_file')
def render_static_file(parser, token):
    try:
        split_token = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    file_name = split_token[1]
    return RenderStaticFileNode(file_name)


class RenderStaticFileNode(template.Node):
    def __init__(
        self,
        file_name
    ):
        self.file_name = file_name

    def render(
        self,
        context
    ):
        file_name = self.file_name
        try:
            variable = template.Variable(file_name)
            file_name = variable.resolve(context)

        except template.VariableDoesNotExist:
            pass

        try:
            file_content = open(
                os.path.join(
                    settings.STATIC_ROOT,
                    file_name
                ),
                'rb'
            ).read()

        except:
            file_content = ''

        return file_content
