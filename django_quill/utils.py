import datetime
import os.path
import random
import string

from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.encoding import force_str
from django.utils.module_loading import import_string

# Non-image file icons, matched from top to bottom
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}


# Allow for a custom storage backend defined in settings.
def get_storage_class():
    return import_string(
        getattr(
            settings,
            "QUILL_IU_STORAGE_BACKEND",
            "django.core.files.storage.DefaultStorage",
        )
    )()


storage = get_storage_class()


def slugify_filename(filename):
    """Slugify filename"""
    name, ext = os.path.splitext(filename)
    slugified = get_slugified_name(name)
    return slugified + ext


def add_timestamp(filename):
    """add timestamp to filename"""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f'{name}_{timestamp}{ext}'


def add_user_id(user_id, filename):
    """add user_id to filename"""
    name, ext = os.path.splitext(filename)
    return f'{user_id}_{name}{ext}'


def get_slugified_name(filename):
    slugified = slugify(filename)
    return slugified or get_random_string()


def get_random_string():
    return "".join(random.sample(string.ascii_lowercase * 6, 6))


def get_thumb_filename(file_name):
    """
    Generate thumb filename by adding _thumb to end of
    filename before . (if present)
    """
    return force_str("{0}_thumb{1}").format(*os.path.splitext(file_name))


def get_media_url(path):
    """
    Determine system file's media URL.
    """
    return storage.url(path)


def is_valid_image_extension(file_path):
    extension = os.path.splitext(file_path.lower())[1]
    return extension in IMAGE_EXTENSIONS
