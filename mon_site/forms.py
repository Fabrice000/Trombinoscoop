from django import forms
from mon_site.models import Person, Student, Employee
class LoginForm(forms.Form):
    email = forms.EmailField(label='Courriel:')
    password = forms.CharField(label='Mot de passe:',widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        # verifie que les deux champs sont valides
        if email and password:
            result = Person.objects.filter(password=password,email=email)
            
            if len(result) != 1:
                raise forms.ValidationError("Adresse de courriel ou mot de passe erroné.")
            
        return cleaned_data
    
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('friends',)

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ('friends',)

class AddFriendForm(forms.Form):
    email = forms.EmailField(label='Courriel :')
    def clean(self):
        cleaned_data = super(AddFriendForm, self).clean()
        email = cleaned_data.get("email")

        # on verifie que le champ est valide

        if email:
            result = Person.objects.filter(email=email)
            if len(result) != 1:
                raise forms.ValidationError("Adresse de courriel erronée.")
        return cleaned_data
