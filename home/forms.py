from django import forms
from .models import CustomUser, Message # <-- ADDED 'Message' IMPORT

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "avatar",
            "bio",
            "sustainability_interests",
            "nickname",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "sustainability_interests": forms.TextInput(),
            "nickname": forms.TextInput(),
        }
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'image_attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'})
        }
        labels = {
            'content': '',
            'image_attachment': 'Attach Image'
        }