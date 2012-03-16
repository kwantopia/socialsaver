from django.forms import ModelForm, RadioSelect
from models import BasicFoodSurvey, EatingCompanySurvey, EatingOutSurvey, FriendsSurvey, DigitalReceiptSurvey

class BasicFoodSurveyForm(ModelForm):

    radio_fields = ['different', 'spontaneous', 'uniqueness', 'variety', 'averse',
                    'own', 'regret', 'expert', 'share', 'yelp', 'yelp_community']

    class Meta:
        model = BasicFoodSurvey
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
        widgets = {
            'different': RadioSelect(attrs={'class':'simple'}),
            'spontaneous': RadioSelect(attrs={'class':'simple'}),
            'uniqueness': RadioSelect(attrs={'class':'simple'}),
            'variety': RadioSelect(attrs={'class':'simple'}),
            'averse': RadioSelect(attrs={'class':'simple'}),
            'own': RadioSelect(attrs={'class':'simple'}),
            'regret': RadioSelect(attrs={'class':'simple'}),
            'expert': RadioSelect(attrs={'class':'simple'}),
            'yelp': RadioSelect(attrs={'class':'simple'}),
            'yelp_community': RadioSelect(attrs={'class':'simple'}),
            'share': RadioSelect(attrs={'class':'simple'})
        }
 
class EatingCompanySurveyForm(ModelForm):

    radio_fields = ['fun', 'waste', 'time', 'happy', 'alone', 'together']

    class Meta:
        model = EatingCompanySurvey 
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
        widgets = {
            'fun': RadioSelect(attrs={'class':'simple'}),
            'waste': RadioSelect(attrs={'class':'simple'}),
            'time': RadioSelect(attrs={'class':'simple'}),
            'happy': RadioSelect(attrs={'class':'simple'}),
            'alone': RadioSelect(attrs={'class':'simple'}),
            'together': RadioSelect(attrs={'class':'simple'})
        }

class EatingOutSurveyForm(ModelForm):
    radio_fields = ['cheap', 'health', 'plan', 'me', 'friends', 'regret', 'others', 'chef',
                    'popular', 'expensive', 'taste']

    class Meta:
        model = EatingOutSurvey
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
        widgets = {
            'cheap': RadioSelect(attrs={'class':'simple'}),
            'health': RadioSelect(attrs={'class':'simple'}),
            'plan': RadioSelect(attrs={'class':'simple'}),
            'plan': RadioSelect(attrs={'class':'simple'}),
            'me': RadioSelect(attrs={'class':'simple'}),
            'friends': RadioSelect(attrs={'class':'simple'}),
            'regret': RadioSelect(attrs={'class':'simple'}),
            'others': RadioSelect(attrs={'class':'simple'}),
            'chef': RadioSelect(attrs={'class':'simple'}),
            'popular': RadioSelect(attrs={'class':'simple'}),
            'expensive': RadioSelect(attrs={'class':'simple'}),
            'taste': RadioSelect(attrs={'class':'simple'})
        }

class DigitalReceiptSurveyForm(ModelForm):

    radio_fields = ['helpful', 'sharing', 'stats', 'stats_change', 'popularity', 'friends',
                    'talk', 'new', 'reviews', 'reputation', 'spending', 'changed', 'general',
                    'cheap', 'healthy']

    class Meta:
        model = DigitalReceiptSurvey
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
        widgets = {
            'helpful': RadioSelect(attrs={'class':'simple'}),
            'sharing': RadioSelect(attrs={'class':'simple'}),
            'stats': RadioSelect(attrs={'class':'simple'}),
            'stats_change': RadioSelect(attrs={'class':'simple'}),
            'popularity': RadioSelect(attrs={'class':'simple'}),
            'friends': RadioSelect(attrs={'class':'simple'}),
            'talk': RadioSelect(attrs={'class':'simple'}),
            'new': RadioSelect(attrs={'class':'simple'}),
            'reviews': RadioSelect(attrs={'class':'simple'}),
            'reputation': RadioSelect(attrs={'class':'simple'}),
            'spending': RadioSelect(attrs={'class':'simple'}),
            'changed': RadioSelect(attrs={'class':'simple'}),
            'general': RadioSelect(attrs={'class':'simple'}),
            'cheap': RadioSelect(attrs={'class':'simple'}),
            'healthy': RadioSelect(attrs={'class':'simple'})
        }


class FriendsSurveyForm(ModelForm):

    class Meta:
        model = FriendsSurvey
        exclude = ('user', 'survey', 'uuid_token', 'completed', 'complete_date')
