"""Managers of Zinnia"""
from django.db import models
from django.utils import timezone
from django.contrib.sites.models import Site

from zinnia.settings import SEARCH_FIELDS
from django.utils.translation import get_language

from zinnia.middleware.zinnia_app import current_apps, current_namespaces

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """
    Return the published tags.
    """
    from tagging.models import Tag
    from zinnia.models.entry import Entry
    tags_entry_published = Tag.objects.usage_for_queryset(
        Entry.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


# The argument to use the language of current thread .
CURRENT_LANGUAGE = 'current-language'


def get_optional_lang_arg(arg_name, language):
    optional_filters = {}
    if language and (current_namespaces() or current_apps()):
        optional_filters[arg_name] = get_language() \
            if language == CURRENT_LANGUAGE else language

    return optional_filters


def entries_published(queryset, language=CURRENT_LANGUAGE):
    """
    Return only the entries published.
    """
    now = timezone.now()
    return queryset.filter(
        models.Q(start_publication__lte=now) |
        models.Q(start_publication=None),
        models.Q(end_publication__gt=now) |
        models.Q(end_publication=None),
        status=PUBLISHED, sites=Site.objects.get_current(),
        **get_optional_lang_arg('language', language))


class EntryPublishedLocalManager(models.Manager):
    """
    Manager to retrieve published entries.
    """

    def get_queryset(self):
        """
        Return published entries.
        """
        return entries_published(
            super(EntryPublishedLocalManager, self).get_queryset())

    def on_site(self):
        """
        Return entries published on current site.
        """
        return super(EntryPublishedLocalManager, self).get_queryset().filter(
            sites=Site.objects.get_current())

    def search(self, pattern):
        """
        Top level search method on entries.
        """
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """
        Advanced search on entries.
        """
        from zinnia.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """
        Basic search on entries.
        """
        lookup = None
        for pattern in pattern.split():
            query_part = models.Q()
            for field in SEARCH_FIELDS:
                query_part |= models.Q(**{'%s__icontains' % field: pattern})
            if lookup is None:
                lookup = query_part
            else:
                lookup |= query_part

        return self.get_queryset().filter(lookup)


class EntryRelatedPublishedManager(models.Manager):
    """
    Manager to retrieve objects associated with published entries.
    """

    def get_queryset(self, language=CURRENT_LANGUAGE):
        """
        Return a queryset containing published entries.
        """
        now = timezone.now()
        return super(
            EntryRelatedPublishedManager, self).get_queryset().filter(
            models.Q(entries__start_publication__lte=now) |
            models.Q(entries__start_publication=None),
            models.Q(entries__end_publication__gt=now) |
            models.Q(entries__end_publication=None),
            entries__status=PUBLISHED,
            entries__sites=Site.objects.get_current(),
            **get_optional_lang_arg('entries__language', language)
            ).distinct()
