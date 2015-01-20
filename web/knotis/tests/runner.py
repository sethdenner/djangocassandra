from django_nose import BasicNoseRunner


class KnotisTestSuiteRunner(BasicNoseRunner):
    """
    The knotis test suite runner - because we run cassandra.

    Based on some of the documentation at
    https://github.com/django-nose/django-nose


    In the current state, this overrides the two main functions from the
    NoseTestSuitRunner. I guess that means it could just inheric from
    django_nose.BaseTestSuitRunner but I'm not willing to mess with it much
    more.


    This means that there will definite side effects on a dev and test
    database.

    Future writings of this class will be more similar to
    https://github.com/django-nose/django-nose/blob/master/django_nose/runner.py#L323
    That is liable to change lines. Look at the NoseTestSuiteRunner Class.

    """

    def setup_databases(self):
        pass

    def teardown_databases(self, *args, **kwargs):
        pass
