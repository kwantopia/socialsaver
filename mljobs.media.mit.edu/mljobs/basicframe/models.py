from django.db import models
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.models import User, Group
import datetime 


def calculate_post_expires():
    """
		Generate an expiration date based on settings.JOB_POSTS_EXPIRE_DAYS

		Returns:
			A date object that is JOB_POSTS_EXPIRE_DAYS in the future
    """
    post_expire_days = datetime.timedelta(
        days=settings.JOB_POSTS_EXPIRE_DAYS)
    return datetime.date.today() + post_expire_days	


STATE_CHOICES=(
	('AL', 'Alabama'),
	('AK', 'Alaska'),
)

class Interest(models.Model):

	"""
		defines "interest spheres" for MLJUsers, MLJGroups, and Jobs
			related via InterestWeight with MLJUsers and Jobs (ForeignKey in InterestWeight)
			related via ManyToMany relationship with MLJGroups
	"""
	
	TYPE = "INTEREST"
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return self.name

	def get_json(self):
		result = {
				'id': str(self.id),
				'name': self.name,
		}
		return result

class MLJUser(User):
	"""
		inherits from User in django.contrib.auth.models;
		all user types in MLJobs will inherit from this (MLJUser)
		** using this to keep User separate from being applicaiton specific **
	"""
	pass
	
class MLJGroup(Group):
	"""
		inherits from Group in django.contrib.auth.models;
		all group types will inherit from this (MLJGroup)
		*** using this to keep Group separate from being application specific **
	"""
	
	interests = models.ManyToManyField(Interest)
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
		
class Course(models.Model):

	"""
		all of the main majors/courses of study offered at MIT
	"""
	
	TYPE = "COURSE"
	num = models.IntegerField()
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)

	def __unicode__(self):
		return self.name	
	
class Document(models.Model):

	"""
		handles all file uploads.. ie docs/files for resumes and cover letters, etc..
		Maps to MLJUser via ForeignKey
	"""
	
	RESUME = 0
	COVER = 1
	OTHER = 2
	
	UPLOAD_TYPE = (
		(RESUME,'Resume'),
		(COVER, 'Cover Letter'),
		(OTHER, 'Other'),
	)
	
	user = models.ForeignKey(MLJUser)
	type = models.IntegerField(choices=UPLOAD_TYPE, default=RESUME) 
	file = models.FileField(upload_to='addl_files')
	
	
class Job(models.Model):

	"""
		main class from which all "jobs" will inherit 
		--> used as basic template for posting:
			UROP, internship, full/part-time positions
	"""

	TYPE = "JOB"
	posted_by = models.ForeignKey(MLJUser)
	title = models.CharField(max_length=50)
	affiliation = models.ForeignKey(MLJGroup)
	description = models.TextField()
	
	ASAP = 0
	JAN = 1
	FEB = 2
	MAR = 3
	
	DATE_CHOICES = (
		(ASAP,'As soon as possible'),
		(JAN,'January'),
		(FEB,'February'),
		(MAR,'March'),
	)
	
	start_date = models.IntegerField(choices=DATE_CHOICES, default=ASAP)
	requirements = models.TextField()
	major = models.ManyToManyField(Course)
	
	deleted = models.BooleanField(default=False)
	posted_on = models.DateTimeField(default=datetime.datetime.today)
	expiration_date = models.DateField(
		default=calculate_post_expires,
		help_text=(
			"This field defaults to "
			"%s days from user submission." %
			settings.JOB_POSTS_EXPIRE_DAYS))
	# if the listing produced a "found" hiree --> addressed upon the listing CLOSING/ENDING (deleted=True)
	found = models.BooleanField(default=False)
	# optional place to add comments when the listing closes --> addressed when the listing is CLOSING/ENDING (deleted=True)
	close_comment = models.TextField(null = True)
	

class UROP(Job):

	"""
		inherits from Job (defined above) and used for posting UROPs
	"""
	duration = models.CharField(max_length=200, blank=True)
	
	def __unicode__(self):
		return self.title


		
class Internship(Job):

	"""
		inherits from Job (defined above) and used for posting Internships
	"""

	duration = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=50)	
	state = models.CharField(max_length=30, choices=STATE_CHOICES)
	
	def __unicode__(self):
		return self.title
	
	def __unicode__(self):
		return self.title
	

	
class SponsorJob(Job):

	"""
		inherits from Job (defined above)
		and used for posting full/part time positions offered by Media Lab Sponsors/Companies
		can specify if only ML Grad students can apply
	"""

	part_time = models.BooleanField(default=False)
	full_time = models.BooleanField(default=True)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=30, choices = STATE_CHOICES)
	
	# specifies if this job is limited only to ML Grad students
	only_mlgrad = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.title
	
	
class InterestWeight(models.Model):

	"""
		the relationship between Interest and either MLJUser or Job models via ForeignKey 
		will have weight from 0-10 ... using jQuery UI for slider
	"""
	interest = models.ForeignKey(Interest)
	user = models.ForeignKey(MLJUser, null=True)
	job = models.ForeignKey(Job, null=True)
	weight = models.IntegerField()
	updated = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return "%s for %s"%(self.weight, self.interest.name)
	
class Application(models.Model):

	"""
		the "job application" that is submitted when students apply for a Job
		
		Current Idea:
			will be put in each Portfolio but also be sent via email
	"""

	applicant = models.ForeignKey(MLJUser, related_name='%(app_label)s_%(class)s_applied')
	employer = models.ForeignKey(MLJUser, related_name='%(app_label)s_%(class)s_new')
	job = models.ForeignKey(Job)
	group = models.ForeignKey(MLJGroup)
	
	resume = models.ManyToManyField(Document, related_name='uploaded_resume')
	cover = models.ManyToManyField(Document, related_name='uploaded_cover')
	comments = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return self.job.title


		
class MLGroup(MLJGroup):

	"""
		inherits from MLJGroup (definined above) which inherits from Group in django.contrib.auth.models
		used to define which Media Lab Group a GradUser (ie Grad Student) is affiliated with
		each MLGroup will have its own "profile" as well
	"""
	
	TYPE = "ML GROUP"
	charm_id = models.IntegerField(null=True)
	mission = models.TextField()
	description = models.TextField()

	pldb_image = models.CharField(max_length=128, default="")
	url = models.CharField(max_length=100, null=True)

	image = models.ImageField(upload_to='images', blank=True) 

	def __unicode__(self):
		return self.name
	
class MLSponsor(MLJGroup):

	"""
		inherits from MLJGroup (defined above)
		used to define which Sponsor/Company a SponsorUser (ie a representative from said Sponsor) is affiliated with
		each MLSponsor will have its own "profile" as well
	"""

	TYPE = "ML SPONSOR/COMP"

	industry = models.CharField(max_length=50)
	city = models.CharField(max_length=50)	
	state = models.CharField(max_length=30, choices=STATE_CHOICES)
	
	about = models.TextField()
	url = models.CharField(max_length=100, null=True)
	image = models.ImageField(upload_to='images', blank=True)

	def __unicode__(self):
		return self.name
	
class UndergradUser(MLJUser):

	"""
		inherits from MLJUser (defined above)
		for Undergraduate Users 
	"""

	TYPE = "UNDERGRAD"
	
	# UNDECLARED=0
	# CIVIL_ENVIRN=1
	# MECHANICAL=2
	# MATERIALS=3
	# ARCHITECTURE=4
	# CHEMISTRY=5
	# EECS=6
	# BIOLOGY=7
	# PHYSICS=8
	# BRAIN_COG=9
	# CHEM_E=10
	# URBAN=11
	# EAPS=12
	# ECONOMICS=14
	# MANAGEMENT=15
	# AERO_ASTRO=16
	# POLI_SCI=17
	# MATH=18
	# BIO_ENG=20
	# HUMANITIES=21
	# NUCLEAR=22
	# LING_PHIL=24
	# CMS=13
	# ESD=19
	# HST=23
	# MAS=25
	# STS=26

	# MAJOR_CHOICES=(
		# (UNDECLARED, 'Undeclared'),
		# (CIVIL_ENVIRN, 'Course 1: Civil and Environmental Engineering'),
		# (MECHANICAL, 'Course 2: Mechanical Engineering'),
		# (MATERIALS,'Course 3: Materials Science and Engineering'),
		# (ARCHITECTURE,'Course 4: Architecture'),
		# (CHEMISTRY,'Course 5: Chemistry'),
		# (EECS, 'Course 6: Electrical Engineering and Computer Science'),
		# (BIOLOGY,'Course 7: Biology'),
		# (PHYSICS,'Course 8: Physics'),
		# (BRAIN_COG, 'Course 9: Brain and Cognitive Sciences'),
		# (CHEM_E,'Course 10: Chemical Engineering'),
		# (URBAN,'Course 11: Urban Studies and Planning'),
		# (EAPS, 'Course 12: Earth, Atmospheric, and Planetary Sciences'),
		# (ECONOMICS,'Course 14: Economics'),
		# (MANAGEMENT,'Course 15: Business and Management (Sloan School)'),
		# (AERO_ASTRO, 'Course 16: Aeronautics and Astronautics'),
		# (POLI_SCI, 'Course 17: Political Science'),
		# (MATH,'Course 18: Mathematics'),
		# (BIO_ENG,'Course 20: Biological Engineering'),
		# (HUMANITIES,'Course 21: Humanities (SHASS)'),
		# (NUCLEAR,'Course 22: Nuclear Science and Engineering'),
		# (LING_PHIL, 'Course 24: Linguistics and Philosophy'),
		# (CMS, 'CMS: Comparative Media Studies'),
		# (ESD, 'ESD: Engineering Systems Division'),
		# (HST, 'HST: Health Sciences and Technology'),
		# (MAS, 'MAS: Media Arts and Sciences'),
		# (STS, 'STS: Science, Technology, and Society'),
	# )
	
	prim_major = models.ForeignKey(Course, related_name='%(app_label)s_%(class)s_prim_major')
	prim_major_track = models.CharField(max_length=200, blank=True)
	sec_major = models.ForeignKey(Course, related_name='%(app_label)s_%(class)s_sec_major', null=True)
	sec_major_track = models.CharField(max_length=200, null=True)
	minor_one = models.CharField(max_length=200, null=True)
	minor_two = models.CharField(max_length=200, null=True)
	grad_year=models.CharField(max_length=4)

	def __unicode__(self):
		return self.get_full_name()
	
class GradUser(MLJUser):

	"""
		inherits from MLJUser (defined above)
		for Media Lab Grad Students
			will have the ability to post UROPs
	"""

	TYPE = "GRAD"
	group= models.ForeignKey(MLJGroup)

	def __unicode__(self):
		return self.get_full_name()
	
class SponsorUser(MLJUser):

	"""
		inherits from MLJUser (defined above)
		for Representatives/individuals of a ML Sponsor/Company
			will have the ability to post Internships and full/part-time positions
	"""
	
	TYPE = "SPONS REP"
	group = models.ForeignKey(MLSponsor)

	def __unicode__(self):
		return self.get_full_name()
	
class Profile(models.Model):

	"""
		each MLJUser will have a specific Profile
			related to MLJUser via OneToOne relation
	"""

	TYPE = "PROFILE"
	user = models.OneToOneField(User)
	pic = models.ImageField(upload_to='profile_pic', null=True)
	resume1 = models.FileField(upload_to='resumes', null=True)
	resume2 = models.FileField(upload_to='resumes', null=True)
	fact1 = models.TextField(max_length=250, blank=True)
	fact2 = models.TextField(max_length=250, blank=True)
	fact3 = models.TextField(max_length=250, blank=True)
	link1 = models.CharField(max_length=100, blank=True)
	link2 = models.CharField(max_length=100, blank=True)
	link3 = models.CharField(max_length=100, blank=True)
	involvement = models.TextField()
	worked_with = models.ManyToManyField(MLJUser, related_name='worked_with', null=True)
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return self.user.get_full_name()


class Bookmark(models.Model):

	"""
		a "bookmark" ... acts as a way to mark a "favorite"
	"""

	TYPE = "BOOKMARK"
	user = models.ForeignKey(MLJUser)
	note = models.TextField(blank=True)
	deleted = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	
class BookmarkJob(Bookmark):

	"""
		inherits from Bookmark
		--> indicates a Job posting that user wants to add to Portfolio
	"""

	TYPE = "BOOKMARKED JOB"
	job = models.ForeignKey(Job)
	
	def __unicode__(self):
		return "bookmark: %s"%self.job.title

class BookmarkGroup(Bookmark):

	"""
		inherits from Bookmark
		--> indicates a particular Group (ie MLGroup or MLSponsor) that user wants to add to Portfolio
	"""

	TYPE = "BOOKMARKED GROUP"
	group = models.ForeignKey(Group)

	def __unicode__(self):
		return "bookmark: %s" %self.group.name
	
class BookmarkPerson(Bookmark):

	"""
		inherits from Bookmark
		--> indicates a particular person, ie MLJUser, that user wants to add to Portfolio
	"""

	TYPE = "BOOKMARKED PERSON"
	person = models.ForeignKey(MLJUser)

	def __unicode__(self):
		return "bookmark: %s" %self.person.get_full_name()

class Recommendation(models.Model):

	"""
		way for a user to recommend another user for a position while
		simultaneously recommending a particular job to another user
	"""
	
	made_by = models.ForeignKey(MLJUser, related_name='made_recommendation')
	made_for = models.ForeignKey(MLJUser, related_name='recommended_for')
	job = models.ForeignKey(Job)
	note = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return "%s has been recommended by %s" %(self.made_for, self.made_by)

class Message(models.Model):

	"""
		for sending messages to another user
		
		Current Idea: via email (as email addresses are stored in MLJUser)
	"""
	sender = models.ForeignKey(MLJUser, related_name = 'sent_msg')
	receiver = models.ForeignKey(MLJUser, related_name = 'receive_msg')
	subject = models.CharField(max_length=250, default="(No Subject)")
	note = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return "message from %s to %s" %(self.sender, self.receiver)
		

	
	
	
