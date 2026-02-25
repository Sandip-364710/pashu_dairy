from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Animal, MilkRecord


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="પાસવર્ડ",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'પાસવર્ડ દાખલ કરો'})
    )
    password2 = forms.CharField(
        label="પાસવર્ડની પુષ્ટિ",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'પાસવર્ડ ફરીથી દાખલ કરો'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('name', 'mobile', 'village')
        labels = {
            'name': 'નામ',
            'mobile': 'મોબાઇલ નંબર',
            'village': 'ગામ',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'તમારું નામ દાખલ કરો'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'મોબાઇલ નંબર દાખલ કરો'}),
            'village': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ગામનું નામ દાખલ કરો'}),
        }


class CustomUserLoginForm(forms.Form):
    mobile = forms.CharField(
        max_length=10,
        label='મોબાઇલ નંબર',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'મોબાઇલ નંબર દાખલ કરો',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='પાસવર્ડ',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'પાસવર્ડ દાખલ કરો'
        })
    )


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['tag_no', 'animal_type', 'breed', 'insemination_date']
        labels = {
            'tag_no': 'ટેગ નંબર',
            'animal_type': 'પ્રાણી પ્રકાર',
            'breed': 'જાત',
            'insemination_date': 'બીજદાનની તારીખ',
        }
        widgets = {
            'tag_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ટેગ નંબર દાખલ કરો'}),
            'animal_type': forms.Select(attrs={'class': 'form-select', 'onchange': 'this.form.submit();'}),
            'breed': forms.Select(attrs={'class': 'form-select'}),
            'insemination_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        animal_type = kwargs.pop('animal_type', None)
        super().__init__(*args, **kwargs)
        
        # Define breed mappings
        cow_breeds = [
            ('gir', 'ગીર'),
            ('sahiwal', 'સાહિવાલ'),
            ('holstein', 'હોલ્સ્ટેન'),
            ('jersey', 'જર્સી'),
            ('kankrej', 'કાંકરેજ'),
        ]
        
        buffalo_breeds = [
            ('murrah', 'મુરાહ'),
            ('jafarabadi', 'જાફરાબાદી'),
            ('mehsani', 'મહેસાણી'),
            ('banni', 'બન્ની'),
        ]
        
        if animal_type == 'cow':
            self.fields['breed'].choices = cow_breeds
        elif animal_type == 'buffalo':
            self.fields['breed'].choices = buffalo_breeds
        else:
            # Show all breeds when no animal type is selected
            self.fields['breed'].choices = cow_breeds + buffalo_breeds


class AnimalTypeSelectionForm(forms.Form):
    animal_type = forms.ChoiceField(
        choices=[('', 'પ્રાણી પ્રકાર પસંદ કરો')] + Animal.ANIMAL_TYPES,
        label='પ્રાણી પ્રકાર',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CheckupStatusForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['checkup_status']
        labels = {
            'checkup_status': 'તપાસ સ્થિતિ',
        }
        widgets = {
            'checkup_status': forms.Select(attrs={'class': 'form-select'}),
        }


class MilkRecordForm(forms.ModelForm):
    class Meta:
        model = MilkRecord
        fields = ['animal', 'date', 'session', 'liters', 'price_per_liter']
        labels = {
            'animal': 'પ્રાણી',
            'date': 'તારીખ',
            'session': 'સમય (સવાર/સાંજ)',
            'liters': 'લીટર',
            'price_per_liter': 'દર પ્રતિ લીટર',
        }
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
            'liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'લીટર દાખલ કરો'}),
            'price_per_liter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'દર દાખલ કરો'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['animal'].queryset = Animal.objects.filter(owner=user)
