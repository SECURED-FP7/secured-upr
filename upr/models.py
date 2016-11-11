from django.db import models

class User (models.Model):

	user_id = models.CharField(primary_key=True,max_length=100)
	creator = models.ForeignKey('User',null=True)
	integrityLevel = models.IntegerField(blank=False, default=0)
	type = models.CharField(max_length=100, blank=False, default= 'normal')
	optimization_profile=models.CharField(max_length=100,default="MIN_TRANFER_COSTMIN_LATENCY")
	is_admin = models.BooleanField(default=False)
	is_cooperative = models.BooleanField(default=False)
	is_infrastructure = models.BooleanField(default=False)
	hash = models.CharField(max_length=100, blank=False)
	salt = models.CharField(max_length=100, blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class Group (models.Model):
	name = models.CharField(primary_key=True, max_length=100)
	description = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now=True)

class PSAGroupAssociation(models.Model):
	psa_id=models.CharField(max_length=100, blank=False, default= '0')
	group = models.ForeignKey('Group')
	timestamp = models.DateTimeField(auto_now=True)

class UserGroupAssociation(models.Model):
	group = models.ForeignKey('Group')
	user = models.ForeignKey('User')
	timestamp = models.DateTimeField(auto_now=True)

class UserPSA (models.Model):
	psa_id = models.CharField(max_length=100,blank=False)
	user = models.ForeignKey('User')
	active = models.CharField(max_length=100,blank=False, default='yes')
	running_order = models.IntegerField()
	timestamp = models.DateTimeField(auto_now=True)

class UserHSPLAssociation (models.Model):
	editor = models.ForeignKey('User',related_name='editor_hspl')
	target = models.ForeignKey('User',related_name='target_hspl')
	hspl = models.CharField(max_length=60000,blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class UserMSPLAssociation (models.Model):
	mspl_id=models.AutoField(primary_key=True)
	internalID = models.CharField(max_length=100)
	target = models.ForeignKey('User',related_name='target_mspl')
	editor = models.ForeignKey('User',related_name='editor_mspl')
	mspl = models.CharField(max_length=60000,blank=False)
	capability = models.CharField(max_length=200, blank=False) #Capabilities are in PSAR
	is_reconciled =models.BooleanField(default=False)	
	timestamp = models.DateTimeField(auto_now=True)

class UserSGAssociation (models.Model):
	editor = models.ForeignKey('User',related_name='editor_sg')
	target = models.ForeignKey('User',related_name='target_sg')
	sg = models.CharField(max_length=60000,blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class UserAGAssociation (models.Model):
	editor = models.ForeignKey('User',related_name='editor_ag')
	target = models.ForeignKey('User',related_name='target_ag')
	ag = models.CharField(max_length=60000,blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class UserRAGAssociation (models.Model):
	target = models.ForeignKey('User',related_name='target_rag')
	asg = models.CharField(max_length=60000,blank=False)
	ned_info = models.CharField(max_length=200,blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class UserLowLevelConfAssociation (models.Model):
	psa = models.CharField(max_length=100,blank=False)
	target = models.ForeignKey('User',related_name='target_lspl')
	conf = models.CharField(max_length=60000,blank=False)
	timestamp = models.DateTimeField(auto_now=True)

class AdditionalInformation (models.Model):
	user = models.ForeignKey('User')
	subject_file = models.CharField(max_length=100)
	target_file = models.CharField(max_length=100)
	content_file = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now=True)

class MSPLPSAAssociation (models.Model):
	user_id = models.ForeignKey('User')
	psa_id = models.CharField(max_length=100,blank=False)
	mspl = models.ForeignKey('UserMSPLAssociation')
	timestamp = models.DateTimeField(auto_now=True)
	
class ExecutedPSA(models.Model):
	psa_id=models.CharField(max_length=100, blank=False, default= '0')
	user_id=models.ForeignKey('User') 
	timestamp = models.DateTimeField(auto_now=True)

class ReconciliationReport(models.Model):
	user = models.ForeignKey('User')
	ned_info=models.CharField(max_length=100, blank=False, default='Information about the NED')
	reconciliation_report=models.CharField(max_length=60000, blank=False, default='<HTML>')
	timestamp = models.DateTimeField(auto_now=True)
	latest = models.BooleanField(default=False)

class UserSFA(models.Model):
	user = models.ForeignKey('User')
	mspl = models.ForeignKey('UserMSPLAssociation')
	sfa_report = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now=True)

class UserIFA(models.Model):
	user = models.ForeignKey('User')
	ifa_report = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now=True)

class UserMIFA(models.Model):
	user = models.ForeignKey('User')
	mifa_report = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now=True)

