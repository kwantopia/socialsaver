from django import forms
from models import Party, Feed, Transaction, TransactionLineItem, Wishlist, Product, ReviewRequest, Review


class ReviewForm(forms.ModelForm):
    def clean_content(self):
        content = self.cleaned_data['content']
        num_words = len(content.split())
        if num_words < 5:
            raise forms.ValidationError("Please provide more details.")
        return content
    
    class Meta:
        model = Review
        exclude = ('reviewer', 'viewed', 'public', 'reply_to', 'viewed_by')


class PReviewForm(forms.ModelForm):
    
    class Meta:
        model = Review
        exclude = ('product', 'reviewer', 'viewed', 'public', 'reply_to', 'viewed_by')

