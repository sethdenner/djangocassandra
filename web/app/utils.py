from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

class Email:
    
    @staticmethod
    def generate_email(
        template,
        subject,
        from_email,
        recipients_list,
        data={}
    ):
        text = get_template(template + '.txt')
        html = get_template(template + '.html')
        
        context = Context(data)
        
        text_content = text.render(context)
        html_content = html.render(context)
        email = EmailMultiAlternatives(
            subject, 
            text_content, 
            from_email, 
            recipients_list
        )
        email.attach_alternative(
            html_content, 
            "text/html"
        )
        return email
        