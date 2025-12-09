from django import forms
from .models import CustomUser, Message, Conversation # <-- ADDED 'Message' IMPORT

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

SPECIES_CHOICES = [
    ("", "Please select an option"),
    ("oak", "Oak"),
    ("red_oak", "Red Oak"),
    ("white_oak", "White Oak"),
    ("maple", "Maple"),
    ("sugar_maple", "Sugar Maple"),
    ("pine", "Pine"),
    ("spruce", "Spruce"),
    ("birch", "Birch"),
    ("cherry", "Cherry"),
    ("dogwood", "Dogwood"),
    ("elm", "Elm"),
    ("hickory", "Hickory"),
    ("linden", "Linden"),
    ("poplar", "Poplar"),
    ("sycamore", "Sycamore"),
    ("willow", "Willow"),
    # ... add more
]