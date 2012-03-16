from django.forms import ModelForm, RadioSelect
from models import BasicMobileSurvey, BasicShoppingSurvey, ChoiceToEatSurvey 

class BasicMobileSurveyForm(ModelForm):

    class Meta:
        model = BasicMobileSurvey
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')

class BasicShoppingSurveyForm(ModelForm):
    
    radio_fields = ['online_review', 'friend_review', 'experience_review', 'planned', 'compare_price',
                'compare_product_online', 'compare_product_store', 'impulse', 'sale']
    class Meta:
        model = BasicShoppingSurvey 
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
        widgets = {
            'online_review': RadioSelect(attrs={'class':'simple'}),
            'friend_review': RadioSelect(attrs={'class':'simple'}),
            'experience_review': RadioSelect(attrs={'class':'simple'}),
            'planned': RadioSelect(attrs={'class':'simple'}),
            'compare_price': RadioSelect(attrs={'class':'simple'}),
            'compare_product_online': RadioSelect(attrs={'class':'simple'}),
            'compare_product_store': RadioSelect(attrs={'class':'simple'}),
            'impulse': RadioSelect(attrs={'class':'simple'}),
            'sale': RadioSelect(attrs={'class':'simple'}),
        }
         
class ChoiceToEatSurveyForm(ModelForm):

    radio_fields = []

    class Meta:
        model = ChoiceToEatSurvey 
        exclude = ['user', 'survey', 'uuid_token', 'completed', 'complete_date']


