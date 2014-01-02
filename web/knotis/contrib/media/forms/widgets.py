from knotis.forms import ItemSelectWidget


class ImageSelectWidget(ItemSelectWidget):
    def render(
        self,
        name,
        value,
        attrs=None
    ):
        return ''
