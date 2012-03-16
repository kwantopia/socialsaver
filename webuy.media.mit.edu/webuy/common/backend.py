from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

logger = settings.LOGGER

class OTNBackend(ModelBackend):

    def authenticate(self, email=None, pin=None):
        email = email.lower()
        try:
            user = self.user_class.objects.get(my_email=email)
            if(user.pin == pin):
                return user
            else:
                return None
        except self.user_class.DoesNotExist:
            logger.debug('User with email %s does not exist'%email)
            return None

    def get_user(self, user_id=None):
        try:
            return self.user_class.objects.get(pk=user_id) 
        except self.user_class.DoesNotExist:
            logger.debug('User with user_id %s does not exist'%user_id)
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.',2))
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class
        


        
