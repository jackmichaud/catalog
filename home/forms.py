from django import forms
from .models import CustomUser, Message, CustomImage # <-- ADDED 'Message' IMPORT

class ProfileForm(forms.ModelForm):
    avatar_upload = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = [
            "bio",
            "sustainability_interests",
            "nickname",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "sustainability_interests": forms.TextInput(),
            "nickname": forms.TextInput(),
        }
    
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        image_file = self.cleaned_data.get("avatar_upload")

        if image_file and user:
            custom_image = CustomImage.objects.create(
                image=image_file,
                user=user,
                category="avatars"
            )
            instance.avatar = custom_image

        if commit:
            instance.save()

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