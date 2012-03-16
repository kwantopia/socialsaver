from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
import random, json
import hashlib
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from basicframe.models import *
from basicframe.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

def login_attempt(request):

	"""
		logging in 
		:url: /login/
		
		TODO:
		-success page should be "HOME" and specific to each type of user
	"""

	user = request.user
	data = {}


	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
			
			try: 
				UndergradUser.objects.get(username = user.username)
				type = "undergrad"
			except ObjectDoesNotExist:
				pass
				
			try:
				GradUser.objects.get(username = user.username)
				type = "grad"
			except ObjectDoesNotExist:
				pass
				
			# error with login for sponsor.. does not authenticate..			
			try:
				SponsorUser.objects.get(username = user.username)
				type = "sponsor"
			except ObjectDoesNotExist:
				pass
				
			return render_to_response (
					"templates/success_"+type+".html",
					data,
					context_instance=RequestContext(request)
			)
		
		else:
			return render_to_response (
					"templates/fail.html",
					data,
					context_instance=RequestContext(request)
			)
	else:
		return render_to_response (
				"templates/success.html",
				data,
				context_instance=RequestContext(request)
		)

@login_required		
def logout(request):
	
	"""
		logging out of session
		:url: /logout/
	"""
	logout()
	
	return render_to_response("templates/success.html")
		
@login_required
def profile(request):

	"""
		calling the profile page of MLJUsers
		:url: /profile/
	"""
	
	
	user = request.user	
	data = {}

	data['user'] = user
	data['profile'] = user.get_profile()
	
	print user.get_profile().fact1
	print user.get_profile().fact2
	print user.get_profile().link1
	
	data['worked_with'] = user.get_profile().worked_with.all()
	
	return render_to_response(
				"templates/profile.html",
				data,
				context_instance=RequestContext(request)
		)

def people(request):

	user = request.user
	data = {}
	
	data['undergrads'] = UndergradUser.objects.all()
	data['grads'] = GradUser.objects.all()
	data['sponsors'] = SponsorUser.objects.all()
	
	return render_to_response(
				"templates/people.html",
				data,
				context_instance=RequestContext(request)
		)	

def listings(request):
	
	user = request.user
	data = {}
	
	data['all'] = Job.objects.all().order_by('id')
	
	return render_to_response(
				"templates/listings.html",
				data, 
				context_instance=RequestContext(request)
		)

@login_required
def portfolio(request):
	
	data = {}
	user = MLJUser.objects.get(username = request.user.username)
	
	try:
		data['bm_job'] = BookmarkJob.objects.filter(user=user).order_by('timestamp')
	except ObjectDoesNotExist:
		pass
	try:
		data['bm_person'] = BookmarkPerson.objects.filter(user=user).order_by('timestamp')
	except ObjectDoesNotExist:
		pass
	try:
		data['bm_group'] = BookmarkGroup.objects.filter(user=user).order_by('timestamp')
	except ObjectDoesNotExist:
		pass
	try:
		data['recs'] = Recommendation.objects.filter(made_for=user).order_by('timestamp')
	except ObjectDoesNotExist:
		pass
	try:
		data['made'] = Recommendation.objects.filter(made_by=user).order_by('timestamp')
	except ObjectDoesNotExist:
		pass
	
	return render_to_response(
				"templates/portfolio.html",
				data, 
				context_instance=RequestContext(request)
		)	

@login_required		
def post_listing(request):
	
	user = MLJUser.objects.get(username=request.user.username)
	data = {}
	
	# getting user type
	try:
		UndergradUser.objects.get(username=user.username)
		return render_to_response(
				"templates/fail.html",
				data, 
				context_instance=RequestContext(request)
		)
	except ObjectDoesNotExist:
		try:
			user = GradUser.objects.get(username=user.username)
			data['Grad'] = True
			
			if request.method == 'POST':
				form = UROPForm(request.POST)
				if form.is_valid():
					title = form.cleaned_data['title']
					affiliation = form.cleaned_data['affiliation']
					description = form.cleaned_data['description']
					start_date = form.cleaned_data['start_date']
					requirements = form.cleaned_data['requirements']
					major = form.cleaned_data['major']
					duration = form.cleaned_data['duration']
					form.save()
					data['form'] = form
				
				return render_to_response (
							"templates/urop_form.html",
							data,
							context_instance=RequestContext(request)
					)
			else:
				data['form'] = UROPForm()
			
		except ObjectDoesNotExist:
			user = SponsorUser.objects.get(username=user.username)
			data['Sponsor'] = True
			
			if request.method == 'POST':
				form = InternshipForm(request.POST)
				if form.is_valid():
					title = form.cleaned_data['title']
					affiliation = form.cleaned_data['affiliation']
					city = form.cleaned_data['city']
					state = form.cleaned_data['state']
					description = form.cleaned_data['description']
					start_date = form.cleaned_data['start_date']
					requirements = form.cleaned_data['requirements']
					major = form.cleaned_data['major']
					duration = form.cleaned_data['duration']
					form.save()
					data['form'] = form
				
				return render_to_response (
							"templates/urop_form.html",
							data,
							context_instance=RequestContext(request)
					)
			else:
				data['form'] = InternshipForm()
				
	return render_to_response(
				"templates/urop_form.html",
				data, 
				context_instance=RequestContext(request)
		)

@login_required		
def profile_pic_upload(request):
	"""
		:url: /profile/picture/upload
	"""
	profile = request.user.get_profile()
	data = {}
	
	if request.method=='POST':
		form = ProfilePicUpload(request.POST, request.FILES)
		if form.is_valid():
			save_file(request)
			data['result'] = "success" 
		else: 
			data['result'] = form.errors
	else:
		data['result'] = "error"
	
	return render_to_response (
				"templates/display_results.html",
				data,
				context_instance = RequestContext(request)
		)

@login_required
def save_file(request):
	profile = request.user.get_profile()
	file_content = ContentFile(request.FILES['pic'].read())
	profile.pic.save(request.FILES['pic'].name, file_content)