from django.contrib.auth.decorators import login_required
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^upload/", login_required(views.upload), name="quill_upload"),
    re_path(r"^mentions/", login_required(views.users), name="quill_mentions"),
    re_path(r"^tags/", login_required(views.tags), name="quill_tags"),
    re_path(r"^redirect/", login_required(views.s3_redirect), name="quill_redirect"),
]
