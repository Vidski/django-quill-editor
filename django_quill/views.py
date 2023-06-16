import inspect
import os
import warnings
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.module_loading import import_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django_quill import utils
from django_quill.backends import get_backend
from django_quill.utils import storage


def get_upload_filename(upload_name, request):
    # Generate date based path to put uploaded file.
    # If QUILL_IU_RESTRICT_BY_DATE is True upload file to date specific path.
    if getattr(settings, "QUILL_IU_RESTRICT_BY_DATE", True):
        date_path = datetime.now().strftime("%Y/%m/%d")
    else:
        date_path = ""

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(settings.QUILL_IU_UPLOAD_PATH, date_path)

    if getattr(settings, "QUILL_IU_SLUGIFY_FILENAME", True) and not hasattr(
            settings, "QUILL_IU_FILENAME_GENERATOR"
    ):
        upload_name = utils.slugify_filename(upload_name)

    if getattr(settings, "QUILL_IU_ADD_TIMESTAMP", True) and not hasattr(
            settings, "QUILL_IU_ADD_TIMESTAMP"
    ):
        upload_name = utils.add_timestamp(upload_name)

    if getattr(settings, "QUILL_IU_ADD_USER_ID", True) and not hasattr(
            settings, "QUILL_IU_ADD_USER_ID"
    ):
        upload_name = utils.add_user_id(request.user.id, upload_name)

    if hasattr(settings, "QUILL_IU_FILENAME_GENERATOR"):
        generator = import_string(settings.QUILL_IU_FILENAME_GENERATOR)
        # Does the generator accept a request argument?
        try:
            inspect.signature(generator).bind(upload_name, request)
        except TypeError:
            # Does the generator accept only an upload_name argument?
            try:
                inspect.signature(generator).bind(upload_name)
            except TypeError:
                warnings.warn(
                    "Update %s() to accept the arguments `filename, request`."
                    % settings.QUILL_IU_FILENAME_GENERATOR
                )
            else:
                warnings.warn(
                    "Update %s() to accept a second `request` argument."
                    % settings.QUILL_IU_FILENAME_GENERATOR,
                    PendingDeprecationWarning,
                )
                upload_name = generator(upload_name)
        else:
            upload_name = generator(upload_name, request)

    return storage.get_available_name(os.path.join(upload_path, upload_name))


class ImageUploadView(generic.View):
    http_method_names = ["post"]

    def post(self, request, **kwargs):
        """
        Uploads a file and send back its URL.
        """
        uploaded_file = request.FILES["image"]

        backend = get_backend()

        filewrapper = backend(storage, uploaded_file)
        allow_nonimages = getattr(settings, "QUILL_IU_ALLOW_NONIMAGE_FILES", True)

        # Throws an error when an non-image file are uploaded.
        if not filewrapper.is_image and not allow_nonimages:
            return HttpResponse(status=400)

        filepath = get_upload_filename(uploaded_file.name, request)

        saved_path = filewrapper.save_as(filepath)

        _, filename = os.path.split(saved_path)
        retdata = {"url": f'{reverse_lazy("quill_redirect")}?f={saved_path}', "fileName": filename}

        return JsonResponse(retdata)


upload = csrf_exempt(ImageUploadView.as_view())


class S3RedirectView(generic.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        name = request.GET.get('f', None)
        if not name or not name.startswith(settings.QUILL_IU_UPLOAD_PATH):
            return HttpResponseNotFound()
        return redirect(storage.url(name))


s3_redirect = csrf_exempt(S3RedirectView.as_view())
