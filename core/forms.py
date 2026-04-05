from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'required_skills', 'min_experience']
        
        # Widgets se hum Django Form ko Bootstrap classes de rahe hain taki HTML me mast dikhe
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'e.g. Senior Data Analyst'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Enter detailed job description here...'
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Python, Machine Learning, SQL (Comma separated)'
            }),
            'min_experience': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. 2'
            }),
        }