import re
from django import forms
from manage.models import Domain

class DomainFormView(forms.ModelForm):

	old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
	new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
	confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
	class Meta:
		model = Domain 
		fields = ['filter_mode', 'filter_type', 'listmac',
		 'old_password', 'new_password', 'confirm_password' ]
		widgets = {
            'filter_mode': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'filter_type': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'listmac': forms.Textarea(attrs={'class': 'form-control'}),
        }
	def clean(self):
		cleaned_data = super(DomainFormView, self).clean()
		new_password = cleaned_data['new_password']
		confirm_password = cleaned_data['confirm_password']
		if new_password != confirm_password:
			raise forms.ValidationError(u"Passwords do not match.")
		return cleaned_data

class DomainFormCreate(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
	confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

	class Meta:
		model = Domain
		fields = ['domain', "password", 'confirm_password']
		widgets = {
            'domain': forms.TextInput(attrs={'class': 'form-control'}),
        }
	def clean(self):
		cleaned_data = super(DomainFormCreate, self).clean()
		domain_value = cleaned_data['domain']
		match = re.compile("^(\w+[.]\w+)$")
		if not match.match(domain_value):
			raise forms.ValidationError(u"Domain Name is not valid! (only letter and number)")
		password = cleaned_data['password']
		confirm_password = cleaned_data['confirm_password']
		if password != confirm_password:
			raise forms.ValidationError(u"Passwords do not match.")
		return cleaned_data

	def save(self, user=False, commit=True):
		if user:
			dom = super(DomainFormCreate, self).save(commit=False)
			dom.user = user
			if commit:
				dom.save()
			return dom
		return super(DomainFormCreate, self).save()
class DomainFormDelete(forms.ModelForm):
	class Meta:
		model = Domain
		fields = []