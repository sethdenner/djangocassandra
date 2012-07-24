from django.utils.unittest import TestCase
from django.db.models import Model, CharField
from models import ManyToManyFieldNonRel


class Publication(Model):
    title = CharField(max_length=30)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Article(Model):
    headline = CharField(max_length=100)
    publications = ManyToManyFieldNonRel(Publication)

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)


class ManyToManyNonRelTest(TestCase):
    def setUp(self):
        super(ManyToManyNonRelTest, self).setUp()

        titles = [
            'The Python Journal',
            'Science News',
            'Science Weekly'
        ]
        headlines = [
            'Django lets you build web apps easily',
            'NASA uses Python'
        ]

        self.publications = [Publication(t) for t in titles]
        self.articles = [Article(h)for h in headlines]

        for p in self.publications:
            p.save()

        for a in self.articles:
            a.save()

    def tearDown(self):
        super(ManyToManyNonRelTest, self).tearDown()

    def test_relation(self):
        self.articles[0].publications.add(self.publications[0])
        self.articles[1].publications.add(
            self.publications[0],
            self.publications[1]
        )
        self.articles[1].publications.add(self.publications[2])
        self.articles[1].publications.add(self.publications[2])

        self.assertRaises(
            TypeError,
            self.articles[1].publications.add,
            self.articles[0]
        )

        article_publications0 = self.articles[0].publications.all()
        article_publications1 = self.articles[1].publications.all()

        self.assertEqual(len(article_publications0), 1)
        self.assertEqual(len(article_publications1), 3)

        publication_articles0 = self.publications[0].article_set.all()
        publication_articles1 = self.publications[1].article_set.all()
        publication_articles2 = self.publications[2].article_set.all()

        self.assertEqual(len(publication_articles0), 2)
        self.assertEqual(len(publication_articles1), 1)
        self.assertEqual(len(publication_articles2), 1)
