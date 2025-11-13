from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "avatar",
            "bio",
            "sustainability_interests",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "sustainability_interests": forms.TextInput(),
        }