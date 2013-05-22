from django.forms import (
    Form,
    CharField,
    PasswordInput
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    HTML,
    Div,
    Field,
    ButtonHolder,
    Submit
)

class SignUpForm(Form):
    username = CharField(
        label=''
    )
    password = CharField(
        label='',
        widget=PasswordInput()
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(SignUpForm, self).__init__(
            *args,
            **kwargs
        )

        self.helper = FormHelper()
        self.helper.form_id = 'id-signup-form'
        self.helper.form_method = 'post'
        self.helper.form_action = '/auth/signup/'
        self.helper.layout = Layout(
            Div(
                Field(
                    'username',
                    id='username-input',
                    placeholder='Username'
                ),
                Field(
                    'password',
                    id='password-input',
                    placeholder='Password'
                ),
                css_class='modal-body'
            ),
            ButtonHolder(
                Submit(
                    'signup',
                    'Sign Up',
                    css_class='btn btn-primary',
                ),
                HTML(
                    '<button class="btn" data-dismiss="modal" '
                    'aria-hidden="true">Cancel</button>'
                ),
                css_class='modal-footer'
            )
        )
