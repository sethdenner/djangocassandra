from knotis.views import RenderTemplateFragmentMixin

@register.filter(name='render_view')
def render_view(value):
    
