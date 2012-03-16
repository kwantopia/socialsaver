from django import forms
from models import *


class ProfilePicUpload(ModelForm):
	
	"""
	individual form to handle profile pic uploads 
	"""
	
	class Meta:
		model = Profile
		fields = ['pic']
		

class ApplicationForm(ModelForm):
	class Meta:
		model = Application
		fields = ['resume', 'cover', 'comments']


class SponsorJobForm(ModelForm):
	class Meta:
		model = SponsorJob
		fields = ['title', 'affiliation', 'city', 'state', 'part_time', 'full_time', 'description', 'start_date', 'requirements', 'major', 'only_mlgrad']

		
		
class InternshipForm(ModelForm):
	class Meta:
		model = Internship
		fields = ['title', 'affiliation', 'city', 'state', 'description', 'start_date', 'requirements', 'major', 'duration']


class UROPForm(ModelForm):
	class Meta:
		model = UROP
		fields = ['title', 'affiliation', 'description', 'start_date', 'requirements', 'major', 'duration']
