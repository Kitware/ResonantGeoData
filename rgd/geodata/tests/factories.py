from django.contrib.auth.models import User
from dkc.core.tests.factories import FileFactory
import factory
import factory.django

from rgd.geodata import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user_%d' % n)
    email = factory.Faker('safe_email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ImageFile

    name = factory.Faker('sentence')
    file = factory.SubFactory(FileFactory)
    # creator = factory.SubFactory(UserFactory)
    # modifier = factory.SubFactory(UserFactory)


class ImageSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ImageSet

    name = factory.Faker('sentence')

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for image in extracted:
                self.images.add(image)


class RasterEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RasterEntry

    name = factory.Faker('sentence')
    image_set = factory.SubFactory(ImageSetFactory)

    # If we have an on_commit or post_save method that modifies the model, we
    # need to refresh it afterwards.
    @classmethod
    def _after_postgeneration(cls, instance, *args, **kwargs):
        super()._after_postgeneration(instance, *args, **kwargs)
        instance.refresh_from_db()


class GeometryArchiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GeometryArchive

    name = factory.Faker('sentence')
    file = factory.SubFactory(FileFactory)


class ArbitraryFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ArbitraryFile

    file = factory.django.FileField(filename='sample.dat')

    # If we have an on_commit or post_save method that modifies the model, we
    # need to refresh it afterwards.
    @classmethod
    def _after_postgeneration(cls, instance, *args, **kwargs):
        super()._after_postgeneration(instance, *args, **kwargs)
        instance.refresh_from_db()


class KWCOCOArchiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.KWCOCOArchive

    name = factory.Faker('sentence')
    spec_file = factory.SubFactory(FileFactory)
    image_archive = factory.SubFactory(FileFactory)

    # If we have an on_commit or post_save method that modifies the model, we
    # need to refresh it afterwards.
    @classmethod
    def _after_postgeneration(cls, instance, *args, **kwargs):
        super()._after_postgeneration(instance, *args, **kwargs)
        instance.refresh_from_db()


class FMVFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FMVFile

    name = factory.Faker('sentence')
    file = factory.SubFactory(FileFactory)
    klv_file = factory.django.FileField(filename='sample.klv')
    web_video_file = factory.django.FileField(filename='sample.mp4')
    frame_rate = 30

    # If we have an on_commit or post_save method that modifies the model, we
    # need to refresh it afterwards.
    @classmethod
    def _after_postgeneration(cls, instance, *args, **kwargs):
        super()._after_postgeneration(instance, *args, **kwargs)
        instance.refresh_from_db()


# https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship
# For generating lat-lon coords, this may be helpful:
# https://faker.readthedocs.io/en/latest/providers/faker.providers.geo.html
