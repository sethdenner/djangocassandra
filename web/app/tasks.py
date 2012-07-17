from background_task import background
from django.contrib.auth.models import User

@background(schedule=60)
def notify_user(user_id):
    # lookup user by id and send them a message
    user = User.objects.get(pk=user_id)
    user.email_user('Here is a notification', 'You have been notified')

@background(schedule=1)
def test_background_task(message):
    print message
    # lookup user by id and send them a message
    #user = User.objects.get(pk=user_id)
    #user.email_user('Here is a notification', 'You have been notified')
