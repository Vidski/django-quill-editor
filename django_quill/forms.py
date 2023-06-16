from django import forms
from .widgets import QuillWidget, QuillUploadWidget

__all__ = ("QuillFormField",)


class QuillFormField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "widget": QuillWidget(),
            }
        )
        super().__init__(*args, **kwargs)


class QuillUploadFormField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "widget": QuillUploadWidget(),
            }
        )
        super().__init__(*args, **kwargs)
