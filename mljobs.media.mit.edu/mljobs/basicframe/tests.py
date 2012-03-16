"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from basicframe.models import *
from basicframe.forms import *
from django.contrib.auth import authenticate
import datetime
from PIL import Image
Image.init()

class SimpleTest(TestCase):

	def setUp(self):
		# creating some courses
		course = Course(num=0, name="Undeclared")
		course.save()
		course = Course(num=1, name="Course 1: Civil and Environmental Engineering")
		course.save()
		course = Course(num=2, name="Course 2: Mechanical Engineering")
		course.save()
		course = Course(num=3, name="Course 3: Materials Science and Engineering")
		course.save()
		course = Course(num=4, name="Course 4: Architecture")
		course.save()
		course = Course(num=5, name="Course 5: Chemistry")
		course.save()
		course = Course(num=6, name="Course 6: Electrical Engineering and Computer Science")
		course.save()
		course = Course(num=7, name="Course 7: Biology")
		course.save()
		course = Course(num=8, name="Course 8: Physics")
		course.save()
		course = Course(num=9, name="Course 9: Brain and Cognitive Sciences")
		course.save()		
		course = Course(num=10, name="Course 10: Chemical Engineering")
		course.save()
		course = Course(num=11, name="Course 11: Urban Studies and Planning")
		course.save()
		course = Course(num=12, name="Course 12: Earth, Atmospheric, and Planetary Science")
		course.save()
		course = Course(num=13, name="CMS: Comparative Media Studies")
		course.save()
		course = Course(num=14, name="Course 14: Economics")
		course.save()
		course = Course(num=15, name="Course 15: Business and Management (Sloan School)")
		course.save()
		course = Course(num=16, name="Course 16: Aeronautics and Astronautics")
		course.save()
		course = Course(num=17, name="Course 17: Policital Science")
		course.save()
		course = Course(num=18, name="Course 18: Mathematics")
		course.save()
		course = Course(num=19, name="ESD: Engineering Systems Division")
		course.save()
		course = Course(num=20, name="Course 20: Biological Engineering")
		course.save()
		course = Course(num=21, name="Course 21: Humanities (SHASS)")
		course.save()
		course = Course(num=22, name="Course 22: Nuclear Science and Engineering")
		course.save()
		course = Course(num=23, name="HST: Health Sciences and Technology")
		course.save()
		course = Course(num=24, name="Course 24: Linguistics and Philosophy")
		course.save()
		course = Course(num=25, name="MAS: Media Arts and Sciences")
		course.save()
		course = Course(num=26, name="STS: Science, Technology, and Society")
		course.save()	

		
		# creating some interests
		interest = Interest(name="Programming", description="ex: various languages")
		interest.save()
		interest = Interest(name="Field Work", description="working outside")
		interest.save()
		interest = Interest(name="Artificial Intelligence", description="lorem ipsum")
		interest.save()
		interest = Interest(name="Web Design", description="CSS-genius")
		interest.save()
		interest = Interest(name="Databases", description="storage and such")
		interest.save()
		interest = Interest(name="Music", description="sound quality")
		interest.save()
		# creating some groups
		self.viral_group = MLGroup(name="Viral Communications",
							description="Building agile, scalable communication system that will work with wired, wireless and ad-hoc networks.",)
		self.viral_group.save()
		
		self.fluid_group = MLGroup(name="Fluid Interfaces",
							description="Fluid interfaces is about user interfaces that allow seamless integration between physical and virtual world in a just in time manner.",)
		self.fluid_group.save()
		self.fluid_group.interests.add(Interest.objects.get(name='Programming'))
		self.fluid_group.interests.add(Interest.objects.get(name='Artificial Intelligence'))
		
		
		self.human_group = MLGroup(name="Human Dynamics Group",
							description="Human dynamics group is about understanding organizational and social behaviors of human using various sensor technologies including phones.",)
		self.human_group.save()
		self.human_group.interests.add(Interest.objects.get(name="Web Design"))
		self.human_group.interests.add(Interest.objects.get(name="Databases"))
		
		# creating some sponsors/companies
		self.bose = MLSponsor(name="Bose", industry="Electronics", city="Cambridge", state="MA", about="local company founded by alum")
		self.bose.save()
		self.bose.interests.add(Interest.objects.get(name="Music"))
		
		self.someco = MLSponsor(name="Some Company", industry="Communication Technologies", city="Birmingham", state="AL", about="does some cool stuff")
		self.someco.save()
		self.someco.interests.add(Interest.objects.get(name="Web Design"))
		self.someco.interests.add(Interest.objects.get(name="Databases"))
		
		self.anotherco = MLSponsor(name="Another Company", industry="Industrial Design", city="Juneau", state="AK", about="does other cool stuff")
		self.anotherco.save()
		self.anotherco.interests.add(Interest.objects.get(name="Music"))
		self.anotherco.interests.add(Interest.objects.get(name="Programming"))

		# creating some undergrads
		self.stephanie = UndergradUser(username="niwen", first_name="Stephanie", last_name="Chang", email="niwen@mit.edu", password="stephchang", grad_year="2013", prim_major=Course.objects.get(num=6))
		self.stephanie.set_password('stephchang')
		self.stephanie.save()
		
		self.eric = UndergradUser(username="eshyu", first_name="Eric", last_name="Shyu", email="eshyu@mit.edu", password="ericshyu", grad_year="2013", prim_major=Course.objects.get(num=4))
		self.eric.set_password('ericshyu')
		self.eric.save()
		self.eric.prim_major=Course.objects.get(num=6)
		self.eric.save()
		
		self.eunice = UndergradUser(username="engiarta", first_name="Eunice", last_name="Giarta", email="engiarta@mit.edu", password="eungiarta", grad_year="2013", prim_major=Course.objects.get(num=2))
		self.eunice.set_password('eungiarta')
		self.eunice.save()
		self.eunice.prim_major_track="2A-6: Concentration in Comp Sci"
		self.eunice.minor_one="15: Management Sciences"
		self.eunice.save()
		
		self.eun = UndergradUser(username="eun", first_name="Fake", last_name="Name", email="eunice@mit.edu", password="eunice", grad_year="2011", prim_major=Course.objects.get(num=6), prim_major_track="6-3: Computer Science")
		self.eun.set_password('eunice')
		self.eun.save()
		self.eun.sec_major=(Course.objects.get(num=3))
		self.eun.sec_major_track="pretend its 18: Mathematics"
		self.eun.save()
		
		# creating some grads
		self.kwan = GradUser(username="kwan", first_name="Kwan Hong", last_name="Lee", email="kool@mit.edu", password="kwanhl", group=self.human_group)
		self.kwan.set_password('kwanhl')
		self.kwan.save()
		self.kwan.group=(MLGroup.objects.get(name="Viral Communications"))
		self.kwan.save()
		
		self.grace = GradUser(username="gracewoo", first_name="Grace", last_name="Woo", email="gracewoo@mit.edu", password="grawoo", group=self.viral_group)
		self.grace.save()
		
		# creating some sponsor reps
		self.bob = SponsorUser(username="bobby", first_name="Bob", last_name="Bee", email="fake@mit.edu", password="bobbee", group=self.bose)
		self.bob.set_password('bobbee')
		self.bob.save()
		
		self.rep = SponsorUser(username="username", first_name="first", last_name="last", email="fake1@mit.edu", password="password", group=self.someco)
		self.rep.set_password('password')
		self.rep.save()		

		self.rep1 = SponsorUser(username="arep", first_name="first", last_name="last", email="fake2@mit.edu", password="password", group=self.bose)
		self.rep1.set_password('password')
		self.rep1.save()
		
				# creating some job posts
		self.urop = UROP(posted_by=self.kwan, title="android developer", affiliation=self.viral_group, 
					description="will be building and testing apps for the andoid mobile platform",
					start_date=Job.ASAP, requirements="java and such",)
		self.urop.save()
		self.urop.duration = "semester"
		self.urop.major.add(Course.objects.get(num=6))
		self.urop.save()
		
		self.internship = Internship(posted_by=self.bob, title="some awesome internship", affiliation=self.bob.group, 
					description="working to help design and implement something pretty awesome",
					start_date=Job.ASAP, requirements="interest in product design and manufacturing",)
		self.internship.save()
		self.internship.duration = "summer; approx 10 weeks"
		self.internship.major.add(Course.objects.get(num=2))
		self.internship.major.add(Course.objects.get(num=6))
		self.internship.save()
		
		self.urop2 = SponsorJob(posted_by=self.kwan, title="product designer", affiliation=self.viral_group, 
					description="will be designing, building, and testing things",
					start_date=Job.ASAP, requirements="able to use basic tools, mechanically skilled",)
		self.urop2.save()
		self.urop2.duration = "semester"
		self.urop2.major.add(Course.objects.get(num=6))
		self.urop2.save()
		
		#creating interest weights
		intweight = InterestWeight(user = self.kwan, interest=Interest.objects.get(name="Web Design"), weight=77)
		intweight.save()
		intweight = InterestWeight(user = self.bob, interest=Interest.objects.get(name="Web Design"), weight=77)
		intweight.save()	
		intweight = InterestWeight(job = self.urop, interest=Interest.objects.get(name="Web Design"), weight=77)
		intweight.save()
		intweight = InterestWeight(user = self.stephanie, interest=Interest.objects.get(name="Web Design"), weight=50)
		intweight.save()
		intweight = InterestWeight(user = self.grace, interest=Interest.objects.get(name="Web Design"), weight=50)
		intweight.save()
		intweight = InterestWeight(user = self.eunice, interest=Interest.objects.get(name="Field Work"), weight=22)
		intweight.save()
		intweight = InterestWeight(user = self.eric, interest=Interest.objects.get(name="Databases"), weight=77)
		intweight.save()
		intweight = InterestWeight(job = self.urop, interest=Interest.objects.get(name="Databases"), weight=77)
		intweight.save()
		
		# creating some user profiles
		profile = Profile(user=self.eunice, fact1="im a 'wannabe foodie'--i cruise through yelp reviews and seek out those top and hole-in-the-wall restaurants", 
						fact2="hmm.. i also like to build things; hence my interest in both course 2 and 6", fact3="something else about me", link1="tasteofthree.wordpress.com",
						involvement="various clubs, orgs, and student groups..")
		profile.save()
		profile.worked_with.add(self.kwan)
		profile.worked_with.add(self.stephanie)
		profile.save()
		
		profile = Profile(user=self.kwan, fact1="something", 
						fact2="something else", fact3="and something else about me", link1="encounter.media.mit.edu",
						involvement="research")
		profile.save()
		profile.worked_with.add(self.eunice)
		profile.worked_with.add(self.stephanie)
		profile.save()
		
		profile = Profile(user=self.bob, fact1="something", 
						fact2="something else", fact3="and something else about me",
						involvement="research")
		profile.save()
		profile.worked_with.add(self.eun)
		profile.save()
		
		# creating some recommendations
		self.rec1 = Recommendation(made_by=self.kwan, made_for=self.eric, job=self.urop, note="smart, good work ethic, experienced")
		self.rec1.save()
		self.rec2 = Recommendation(made_by=self.stephanie, made_for=self.eric, job=self.urop, note="good team member")
		self.rec2.save()
		self.rec3 = Recommendation(made_by=self.kwan, made_for=self.eunice, job=self.urop, note="good work ethic, experienced")
		self.rec3.save()
		self.rec4 = Recommendation(made_by=self.kwan, made_for=self.stephanie, job=self.internship, note="fast learner, excellent worker")
		self.rec4.save()		
		self.rec5 = Recommendation(made_by=self.eunice, made_for=self.eric, job=self.internship, note="works well under pressure, efficient")
		self.rec5.save()
		self.rec6 = Recommendation(made_by=self.eric, made_for=self.eunice, job=self.internship, note="works well independently as well as in groups")
		self.rec6.save()
		
		# creating some messages
		self.message = Message(sender=self.stephanie, receiver=self.eunice, subject="hey!",note="hey there! let's get together and work on updating our resumes!")
		self.message.save()
		self.message1 = Message(sender=self.stephanie, receiver=self.eric, note="hello! a friend and i are working on our resumes; you should join us!")
		self.message1.save()
		self.message2 = Message(sender=self.eric, receiver=self.bob, subject="job inquiry", note="Hi! I had a quick question about this position.")
		self.message2.save()
		self.message3 = Message(sender=self.kwan, receiver=self.stephanie, subject="perfect for you", note="Hello. I noticed that you might be a good fit for this job. Please check it out!")
		self.message3.save()
		
		# creating some bookmarks
		self.bkurop = BookmarkJob(user=self.eric, note="this is something i might be interested in", job=self.urop)
		self.bkurop.save()
		self.bkjob = BookmarkJob(user=self.eunice, note="one to think about", job=self.urop)
		self.bkjob.save()
		self.bkperson1 = BookmarkPerson(user=self.eunice, note="good person", person=self.eun)
		self.bkperson1.save()		
		self.bkperson2 = BookmarkPerson(user=self.eunice, note="also a good person", person=self.eric)
		self.bkperson2.save()
		self.bkgrp = BookmarkGroup(user=self.eunice, note="i like their statement", group=self.viral_group)
		self.bkgrp.save()		
		
	def test_authentication(self):
		print "*********** testing authentication ************"
		# should return "SUCCESS"
		user = authenticate(username='engiarta', password='eungiarta')
		if user is not None:
			if user.is_active:
				user = UndergradUser.objects.get(username = user.username)
				print type(user)
				print "SUCCESS"
			else:
				print "sorry.. not active"
		else:
			print "incorrect login info"
		
		# should return "incorrect login info"
		user = authenticate(username='eshyu', password='wrong')
		if user is not None:
			if user.is_active:
				print "SUCCESS"
			else:
				print "sorry.. not active"
		else:
			print "incorrect login info"
			
	def test_login(self):
		"""
			testing current log-in view
		"""
		print "*********** testing login ************"
		response = self.client.post("/login/", {"username":"engiarta", "password":"eungiarta"})
		print response
		
		self.assertContains(response, "Undergrad")
		
		response = self.client.post("/login/", {"username":"eshyu", "password":"wrong"})
		print response
		self.assertNotContains(response, "Undergrad")
		self.assertContains(response, "Success!!")
	
		response = self.client.post("/login/", {"username":"kwan", "password":"kwanhl"})
		print response
		self.assertContains(response, "GradUser")
		
		response = self.client.post("/login/", {"username":"bobby", "password":"bobbee"})
		print response
		self.assertContains(response, "Sponsor")
	
	def test_bookmarks(self):
		print "*********** testing bookmarks ************"
		print self.bkurop
		print self.bkurop.timestamp
		print self.bkurop.job.expiration_date
		
	def test_portfolio(self):
		print "****************testing portfolio*******************"
		test = BookmarkPerson.objects.filter(user=MLJUser.objects.get(username="engiarta")).order_by('timestamp')
		print test
		for each in test:
			print each.timestamp
		print BookmarkGroup.objects.filter(user=self.eunice)
		print BookmarkJob.objects.filter(user=self.eunice)
		print BookmarkJob.objects.filter(user=MLJUser.objects.get(username="engiarta"))
		
	def test_profiles(self):
		print "*********** testing profiles ************"
		response = self.eunice.get_profile()
		print response
		print response.worked_with.all()

		response = self.kwan.get_profile()
		print response
		print response.worked_with.all()
		print self.kwan.groups.all()
		
		response = self.bob.get_profile()
		print response
		
		
	def test_jobs(self):
		print "*********** testing jobs ************"
		print self.urop
		print self.urop.posted_by
		print self.urop.TYPE
		print self.urop.posted_on
		print self.urop.expiration_date
		
	def test_interests(self):
		print "*********** testing interests ************"
		print Interest.objects.all()
		print InterestWeight.objects.all()

		print InterestWeight.objects.filter(user=self.kwan)
		print self.kwan.interestweight_set.all()

		
		one = Interest.objects.get(id=1)
		print one.get_json()
		
		print "#### specific interest test"
		web_interest = InterestWeight.objects.filter(interest = Interest.objects.get(name="Web Design"))
		print web_interest
		
		for each in web_interest:
			if each.user:
				print each.user.get_full_name()
			elif each.job:
				print each.job.title
			else:
				print "uh oh"

		
		print""
		print"***** specific 77, wd test **"
		int_77 = InterestWeight.objects.filter(interest__name="Web Design")
		print int_77
		print"**after filter**"
		sweet = int_77.filter(weight=77)
		for each in sweet:
			if each.user:
				print each.user.get_full_name()
			elif each.job:
				print each.job.title
			else:
				print "uh oh"
			
		print "**end test**"
	
	def test_recommendations(self):
		print "*************testing recs**************"
		print self.rec1
		print self.rec1.note
		
		for_urop = Recommendation.objects.filter(job=self.urop)
		for each in for_urop:
			print each, each.note
	
	def test_messages(self):
		print "************* testing messages ****************"
		print Message.objects.filter(sender=self.stephanie)
		print Message.objects.filter(note__icontains='resume')
		
	def test_some_views(self):
		"""
			tests the current profile view
		"""
		print "*************profile view*******************"
		response = self.client.post("/login/", {"username":"engiarta", "password":"eungiarta"})
		print response
		
		resp = self.client.post("/profile/")
		print resp.content

	def test_people_view(self):
		print "***************people view******************"
		response = self.client.post("/people/")
		print response.content
		
		
	# def test_logout(self):
		# print "***********testing logout*************"
		# response = self.client.post("/login/", {"username":"engiarta", "password":"eungiarta"})
		# resp = self.client.get("/logout/", {"username":"engiarta", "password":"eungiarta"})		
		# print resp.content
		# self.assertContains(response, "Success!!")
		# self.assertContains(resp, "Success!!")
		
		
	def test_listings_view(self):
		"""
			testing the current listings view
		"""
		print "*****************listings view************************"
		response = self.client.post("/listings/")
		print response.content
		
	def test_porftolio(self):
		"""
			testing current portfolio view
		"""
		print "************** portfolio view ***********************"
		response = self.client.post("/login/", {"username":"eshyu", "password":"ericshyu"})
		print response.content
		
		response = self.client.post("/portfolio/", {"username":"eshyu", "password":"ericshyu"})
		print response.content
		
	def test_post_view(self):
		"""
			testing the current post_listing view
		"""
		print "***************post_listing view****************************"
		response = self.client.post("/login/", {"username":"kwan", "password":"kwanhl"})
		print response.content
		self.assertContains(response, "Grad")
		response = self.client.get("/post_listing/")
		print response.content
		# self.assertContains(response, "Grad")
		
		response = self.client.post("/login/", {"username":"bobby", "password":"bobbee"})
		print response.content
		self.assertContains(response, "Sponsor")
		response = self.client.get("/post_listing/", {"username":"bobby", "password":"bobbee"})
		print response.content
		# self.assertContains(response, "Sponsor")	
	
		response = self.client.post("/login/", {"username":"eshyu", "password":"ericshyu"})
		print response.content
		self.assertContains(response, "Undergrad")
		response = self.client.get("/post_listing/", {"username":"eshyu", "password":"ericshyu"})
		print response.content
		self.assertContains(response, "FAIL")
		
		
	def test_profile_pic_upload(self):
		"""
			testing the profile pic upload
		"""
		print "*************profile_pic_upload***********************"
		resp = self.client.post("/login/", {"username":"engiarta","password":"eungiarta"})
		self.assertContains(resp, "Undergrad")
		pic = open('test/test_pic.jpg')
		response = self.client.post("/profile/picture/upload/", {'pic':pic})
		print response.content
		pic.close()
		
		pic2 = open('test/droidcon.png')
		response = self.client.post("/profile/picture/upload/", {'pic':pic2})
		print response.content
		pic2.close()
		
		
	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		self.failUnlessEqual(1 + 1, 2)

		
__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

