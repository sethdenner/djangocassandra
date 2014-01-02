from django.test import TestCase
from django.views.generic import View
from django.template.loader import get_template
from django.template import Context


from knotis.views.mixins import RenderTemplateFragmentMixin
from knotis.templatetags.render_template_fragment import TemplateFragmentNode


class RenderTemplateFragmentTests(TestCase):
    def setUp(self):
        class TestView(View, RenderTemplateFragmentMixin):
            template_name = 'testing/template.html'
            view_name = 'test_view'

        TestView.register_template_fragment()

        self.test_view = TestView

    def test_render_template_fragment(self):
        context = Context({
            'param1': 'test1',
            'param2': 'test2',
            'param3': 'test3'
        })
        node = TemplateFragmentNode(self.test_view.view_name)
        mixin_markup = node.render(context)

        template = get_template(self.test_view.template_name)
        django_markup = template.render(context)

        self.assertEqual(mixin_markup, django_markup)
