from django import forms


class BookingReportForm(forms.Form):
    start_date = forms.DateField(label='Start Date')
    end_date = forms.DateField(label='End Date')
    format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('xlsx', 'Excel'), ('pdf', 'PDF')],
        label='Format'
    )


class UserReportForm(forms.Form):
    user_id = forms.IntegerField(label='User ID')
    format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('xlsx', 'Excel'), ('pdf', 'PDF')],
        label='Format'
    )
