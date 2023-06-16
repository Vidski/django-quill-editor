from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^upload/", login_required(views.upload), name="quill_upload"),
    re_path(r"^redirect/", login_required(views.s3_redirect), name="quill_redirect"),
]
