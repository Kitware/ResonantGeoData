from django.conf import settings
from django.db import models


class Collection(models.Model):
    name = models.CharField(max_length=127)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='CollectionMembership')

    class Meta:
        default_related_name = 'collections'


class CollectionMembership(models.Model):
    READER = 1
    OWNER = 2
    ROLE_CHOICES = [
        (READER, 'Reader'),
        (OWNER, 'Owner'),
    ]
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.SmallIntegerField(
        choices=ROLE_CHOICES,
        default=READER,
        help_text=(
            'A "reader" can view assets in this collection. '
            'An "owner" can additionally add/remove other users, set their permissions, delete the collection, and add/remove other files.'
        ),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['collection', 'user'],
                name='unique_user',
            )
        ]
        default_related_name = 'collection_memberships'
