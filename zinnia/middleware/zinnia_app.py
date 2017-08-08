try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.utils.deprecation import MiddlewareMixin
from zinnia.settings import APPLICATION_INSTANCES


_application_instances_set = set(APPLICATION_INSTANCES)
_thread_locals = local()


def get_current_apps():
    if _application_instances_set:
        return getattr(_thread_locals, 'apps', None)


def current_app_arg(default=None):
    apps = get_current_apps()
    if apps:
        return ':'.join(apps)
    return default


class ZinniaCurrentAppMiddleware(MiddlewareMixin):
    def process_view(self, request, *args, **kwargs):
        namespaces = set(request.resolver_match.namespaces) & \
                     _application_instances_set
        if namespaces:
            _thread_locals.apps = namespaces
        else:
            _thread_locals.app = None

if not _application_instances_set:
    del ZinniaCurrentAppMiddleware.process_view