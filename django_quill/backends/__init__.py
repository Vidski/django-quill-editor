import warnings

from django.conf import settings
from django.utils.module_loading import import_string

from .dummy_backend import DummyBackend


__all__ = ["get_backend", "DummyBackend"]

try:
    from .pillow_backend import PillowBackend
except ImportError:
    pass


# Allow for a custom image backend defined in settings.
def get_backend():
    backend_path = getattr(
        settings, "QUILL_IU_IMAGE_BACKEND", "django_quill.backends.DummyBackend"
    )

    # Honour old registry keys while emitting warnings
    if backend_path is None:
        backend_path = "django_quill.backends.DummyBackend"
        warnings.warn(
            "QUILL_IU_IMAGE_BACKEND now uses a fully qualified path to the backend class."
            "  None should be changed to 'django_quill.backends.DummyBackend'",
            PendingDeprecationWarning,
            stacklevel=2,
        )

    return import_string(backend_path)