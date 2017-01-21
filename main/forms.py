from django import forms


class SubmitForm(forms.Form):
    answer_file = forms.FileField(label='Answer File')
    truth_file = forms.FileField(label='Truth File')
    tasktype = forms.IntegerField(label='Task Type', min_value=0, max_value=2)

