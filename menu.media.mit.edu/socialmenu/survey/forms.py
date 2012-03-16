from django.forms import ModelForm, RadioSelect
from models import EatingHabitSurvey, MenuInterfaceSurvey, ChoiceToEatSurvey

class EatingHabitSurveyForm(ModelForm):
    radio_fields = ['spend_limit', 'fun', 'busy', 'time', 'happy', 'alone',
                    'guilty', 'fun_price']

    class Meta:
        model = EatingHabitSurvey 
        exclude = ['user', 'survey', 'uuid_token', 'completed', 'complete_date']
        widgets = {
            'spend_limit': RadioSelect(attrs={'class':'simple'}),
            'fun': RadioSelect(attrs={'class':'simple'}),
            'busy': RadioSelect(attrs={'class':'simple'}),
            'time': RadioSelect(attrs={'class':'simple'}),
            'happy': RadioSelect(attrs={'class':'simple'}),
            'alone': RadioSelect(attrs={'class':'simple'}),
            'guilty': RadioSelect(attrs={'class':'simple'}),
            'fun_price': RadioSelect(attrs={'class':'simple'}),
        }

class MenuInterfaceSurveyForm(ModelForm):

    radio_fields = ['usability','hierarchy', 'ease_hierarchy', 'phone', 'preorder', 'seating', 'payment' ]

    class Meta:
        model = MenuInterfaceSurvey
        exclude = ['user', 'survey', 'uuid_token', 'completed', 'complete_date']
        widgets = {
            'usability': RadioSelect(attrs={'class':'simple'}),
            'ease_hierarchy': RadioSelect(attrs={'class':'simple'}),
            'hierarchy': RadioSelect(attrs={'class':'simple'}),
            'phone': RadioSelect(attrs={'class':'simple'}),
            'preorder': RadioSelect(attrs={'class':'simple'}),
            'seating': RadioSelect(attrs={'class':'simple'}),
            'payment': RadioSelect(attrs={'class':'simple'}),
        }

class ChoiceToEatSurveyForm(ModelForm):

    radio_fields = ['plan', 'me', 'friends', 'others', 'chef', 'uncertain', 'unsure', 'different', 'spontaneous', 'uniqueness', 'variety', 'averse', 'own']

    class Meta:
        model = ChoiceToEatSurvey 
        exclude = ['user', 'survey', 'uuid_token', 'completed', 'complete_date']

        widgets = {
            'plan': RadioSelect(attrs={'class':'simple'}),
            'me': RadioSelect(attrs={'class':'simple'}),
            'friends': RadioSelect(attrs={'class':'simple'}),
            'others': RadioSelect(attrs={'class':'simple'}),
            'chef': RadioSelect(attrs={'class':'simple'}),
            'uncertain': RadioSelect(attrs={'class':'simple'}),
            'unsure': RadioSelect(attrs={'class':'simple'}),
            'different': RadioSelect(attrs={'class':'simple'}),
            'spontaneous': RadioSelect(attrs={'class':'simple'}),
            'uniqueness': RadioSelect(attrs={'class':'simple'}),
            'variety': RadioSelect(attrs={'class':'simple'}),
            'averse': RadioSelect(attrs={'class':'simple'}),
            'own': RadioSelect(attrs={'class':'simple'}),
        }

