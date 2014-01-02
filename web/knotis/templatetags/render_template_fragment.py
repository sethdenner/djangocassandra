from django import template
register = template.Library()

from knotis.views.mixins import RenderTemplateFragmentMixin


@register.tag(name='render_fragment')
def render_template_fragment(parser, token):
    try:
        split_token = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    view_name = split_token[1]

    if not view_name in RenderTemplateFragmentMixin.registered_fragments:
        raise template.TemplateSyntaxError(
            '"%s" is not a registered template fragment' % (
                view_name
            )
        )

    return TemplateFragmentNode(
        view_name
    )


class TemplateFragmentNode(template.Node):
    def __init__(
        self,
        view_name
    ):
        self.view_name = view_name

    def render(
        self,
        context
    ):
        view_class = RenderTemplateFragmentMixin.registered_fragments[
            self.view_name
        ]

        instance = view_class()
        return instance.render_template_fragment(context)
