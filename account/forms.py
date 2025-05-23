from django import forms
from .models import User, Deposite

class UpdatePhotoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['image']
        
class IdentityForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['identity_front_image', 'identity_back_image']
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['address_image']
        
class ProveForm(forms.ModelForm):
    class Meta:
        model = Deposite
        fields = ['image']