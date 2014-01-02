from django.template import Context
from django.template.loader import get_template


def render_feedback_popup(
    title,
    feedback
):
    popup = get_template('feedback_popup.html')
    context = Context({
        'title': title,
        'feedback': feedback
    })

    return popup.render(context)
