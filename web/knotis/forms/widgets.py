from django.forms import Widget
from django.template import (
    Context,
    Template
)
from django.template.loader import get_template
from django.utils.safestring import mark_safe


class TemplateWidget(Widget):
    template_name = None  # Subclass needs to define this

    def __init__(
        self,
        parameters={},
        *args,
        **kwargs
    ):
        self.parameters = parameters

        super(TemplateWidget, self).__init__(
            *args,
            **kwargs
        )

    def render(
        self,
        name,
        value,
        attrs=None
    ):
        if not self.template_name:
            raise Exception('template_name is not defined for this class')

        template = Template(get_template(self.template_name))
        context = Context(self.parameters)
        return mark_safe(template.render(context))


class ItemSelectRow(object):
    def __init__(
        self,
        item,
        title=None,
        image=None,
        checked=False,
        disabled=False
    ):
        self.item = item
        self.title = title
        self.image = image
        self.checked = checked
        self.disabled = disabled


class ItemSelectAction(object):
    def __init__(
        self,
        name,
        url,
        css_class=None,
        method='GET'
    ):
        self.name = name
        self.url = url
        self.css_class = css_class
        self.method = method


class ItemSelectWidget(TemplateWidget):
    template_name = 'knotis/layout/item_select.html'

    def __init__(
        self,
        rows=[],
        actions=[],
        select_multiple=False,
        render_images=False,
        image_dimensions='32x32',
        *args,
        **kwargs
    ):
        self.rows = rows
        self.actions = actions
        self.select_multiple = select_multiple
        self.render_images = render_images
        self.image_dimensions = image_dimensions

        return super(ItemSelectWidget, self).__init__(
            *args,
            **kwargs
        )

    def render(
        self,
        name,
        value,
        attrs=None
    ):
        self.parameters.update({
            'rows': self.rows,
            'actions': self.actions,
            'select_multiple': self.select_multiple,
            'render_images': self.render_images,
            'image_dimensions': self.image_dimensions
        })

        return super(ItemSelectWidget, self).render(
            name,
            value,
            attrs
        )

    def value_from_datadict(
        self,
        data,
        files,
        name
    ):
        return super(ItemSelectWidget, self).value_from_datadict(
            data,
            files,
            name
        )
