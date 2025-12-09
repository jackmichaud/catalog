from django import forms
from .models import CustomUser, Message, Conversation, CustomImage # <-- ADDED 'Message' IMPORT

class GroupConversationForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Conversation
        fields = ['name', 'participants']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['participants'].queryset = CustomUser.objects.exclude(id=user.id)

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
        return instance

class MessageForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False)
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
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        image_file = self.cleaned_data.get("image_upload")

        if image_file and user:
            custom_image = CustomImage.objects.create(
                image=image_file,
                user=user,
                category="message_attachments"
            )
            instance.image_attachment = custom_image

        if commit:
            instance.save()
        return instance