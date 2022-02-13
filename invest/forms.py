from django import forms
from invest.models import Memo

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
        labels = {
            'subject': '제목',
            'content': '내용',
        }

class searchForm(forms.Form):
    search_word = forms.CharField(label= 'Search Company')