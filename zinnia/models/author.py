"""Author model for Zinnia"""
from django.apps import apps
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.urls import reverse

from zinnia.managers import entries_published
from zinnia.managers import EntryRelatedPublishedManager
from zinnia.middleware.zinnia_app import get_current_apps


def safe_get_user_model():
    """
    Safe loading of the User model, customized or not.
    """
    user_app, user_model = settings.AUTH_USER_MODEL.split('.')
    return apps.get_registered_model(user_app, user_model)


class AuthorPublishedManager(models.Model):
    """
    Proxy model manager to avoid overriding of
    the default User's manager and issue #307.
    """
    published = EntryRelatedPublishedManager()

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Author(safe_get_user_model(),
             AuthorPublishedManager):
    """
    Proxy model around :class:`django.contrib.auth.models.get_user_model`.
    """

    def entries_published(self):
        """
        Returns author's published entries.
        """
        return entries_published(self.entries)

    def get_absolute_url(self):
        """
        Builds and returns the author's URL based on his username.
        """
        current_apps = get_current_apps()
        if current_apps:
            current_apps = ':'.join(current_apps)
        return reverse('zinnia:author_detail', args=[self.get_username()],
                       current_app=current_apps)

    def __str__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return self.get_full_name() or self.get_username()

    class Meta:
        """
        Author's meta informations.
        """
        proxy = True
