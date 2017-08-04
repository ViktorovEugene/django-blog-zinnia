try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.utils.deprecation import MiddlewareMixin

from zinnia.apps import ZinniaConfig


NAMEAPACES = ()
APP_NAMES = (ZinniaConfig.name,)

_thread_locals = local()


def current_apps():
    return getattr(_thread_locals, 'app_names', None)


def current_namespaces():
    return getattr(_thread_locals, 'namespaces', None)


class ZinniaCurrentAppMiddleware(MiddlewareMixin):
    def process_view(self, request, *args, **kwargs):
        """
        Send broken link emails for relevant 404 NOT FOUND responses.
        """
        namespaces = set(request.resolver_match.namespaces) & set(NAMEAPACES)
        if namespaces:
            _thread_locals.namespaces = namespaces
        else:
            _thread_locals.namespaces = None

        app_names = set(request.resolver_match.app_names) & set(APP_NAMES)
        if app_names:
            _thread_locals.app_names = app_names
        else:
            _thread_locals.app_names = None
