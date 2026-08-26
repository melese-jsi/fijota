from datetime import date


from django import forms
from django.utils import timezone
from .models import Expense


class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = [
            "amount",
            "description",
            "category",
            "expense_date",
        ]

        widgets = {

            "amount": forms.NumberInput(
                attrs={
                    "class": "input",
                    "placeholder": "Amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "description": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "What did you spend on?",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "input",
                }
            ),


            "expense_date": forms.DateInput(
                attrs={
                    "class": "input",
                    "type": "date",
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['expense_date'] = timezone.localdate()