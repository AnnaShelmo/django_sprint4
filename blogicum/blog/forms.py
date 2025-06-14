from django import forms
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Оставьте комментарий..."}
            )
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "text",
            "category",
            "location",
            "image",
            "is_published",
            "pub_date",
        ]
        widgets = {
            "pub_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "text": forms.Textarea(attrs={"rows": 5}),
        }
