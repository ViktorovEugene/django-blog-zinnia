try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.utils.deprecation import MiddlewareMixin

_thread_locals = local()


def get_current_apps():
    app = getattr(_thread_locals, 'apps', None)

    return app


class ZinniaCurrentAppMiddleware(MiddlewareMixin):
    def process_view(self, request, *args, **kwargs):
        """
        Send broken link emails for relevant 404 NOT FOUND responses.
        """
        from zinnia.models_bases.entry import APPS
        namespaces = set(request.resolver_match.namespaces) & set(APPS)
        if namespaces:
            _thread_locals.apps = namespaces
        else:
            _thread_locals.app = None
