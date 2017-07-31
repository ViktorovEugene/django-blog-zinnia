try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.utils.deprecation import MiddlewareMixin

_thread_locals = local()


def get_current_apps():
    apps = getattr(_thread_locals, 'apps', None)

    return apps


def current_app_arg(default=None):
    apps = get_current_apps()
    if apps:
        return ':'.join(apps)
    return default


class ZinniaCurrentAppMiddleware(MiddlewareMixin):
    def process_view(self, request, *args, **kwargs):
        """
        Send broken link emails for relevant 404 NOT FOUND responses.
        """
        from zinnia.managers import APPS
        namespaces = set(request.resolver_match.namespaces) & set(APPS)
        if namespaces:
            _thread_locals.apps = namespaces
        else:
            _thread_locals.app = None
