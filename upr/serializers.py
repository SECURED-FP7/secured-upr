from django.forms import widgets
from rest_framework import serializers
from models import User, Group, PSAGroupAssociation, UserGroupAssociation, UserPSA, UserHSPLAssociation, UserMSPLAssociation, UserSGAssociation, UserAGAssociation, UserRAGAssociation, UserLowLevelConfAssociation, AdditionalInformation, MSPLPSAAssociation, ExecutedPSA, ReconciliationReport, UserSFA, UserIFA, UserMIFA



class UserSerializer (serializers.ModelSerializer):
	class Meta:
		model=User
		#fields = ('user_id','creator','optimization_profile','integrityLevel','type','is_cooperative', 'is_infrastructure','is_admin',)
		fields = ('user_id','creator','optimization_profile','integrityLevel','type','is_cooperative', 'is_infrastructure','is_admin','timestamp',)

class UserCreatorSerializer (serializers.ModelSerializer):
	class Meta:
		model=User
		fields = ('creator','timestamp',)

class UserTypeSerializer (serializers.ModelSerializer):
	class Meta:
		model=User
		fields = ('type','timestamp',)

class UserOptProfileSerializer (serializers.ModelSerializer):
	class Meta:
		model=User
		fields = ('optimization_profile','timestamp',)

class GroupSerializer (serializers.ModelSerializer):
	class Meta:
		model=Group

class PSAGroupAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model=PSAGroupAssociation
	
class UserGroupAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model=UserGroupAssociation
		fields = ('group',)


class UserPSASerializer (serializers.ModelSerializer):
	class Meta:
		model = UserPSA
		fields = ('psa_id','running_order','active','timestamp',)

class UserHSPLAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserHSPLAssociation

class UserMSPLAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserMSPLAssociation

class UserSGAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserSGAssociation

class UserAGAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserAGAssociation
		fields = ('editor','target','ag','timestamp',)

class UserRAGAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserRAGAssociation

class UserLowLevelConfAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = UserLowLevelConfAssociation

class AdditionalInformationSerializer (serializers.ModelSerializer):
	class Meta:
		model = AdditionalInformation

class MSPLPSAAssociationSerializer (serializers.ModelSerializer):
	class Meta:
		model = MSPLPSAAssociation

class ExecutedPSASerializer (serializers.ModelSerializer):
	class Meta:
		model = ExecutedPSA
"""
class MSPLSerializer (serializers.ModelSerializer):
	class Meta:
		model = MSPL
"""

class ReconciliationReportSerializer (serializers.ModelSerializer):
	class Meta:
		model =ReconciliationReport
		fields =('user','ned_info','reconciliation_report','timestamp',)

class UserSFASerializer (serializers.ModelSerializer):
        class Meta:
                model =UserSFA
		fields =('user','mspl','sfa_report','timestamp',)

class UserIFASerializer (serializers.ModelSerializer):
        class Meta:
                model =UserIFA
		fields =('user','ifa_report','timestamp',)

class UserMIFASerializer (serializers.ModelSerializer):
        class Meta:
                model =UserMIFA
		fields =('user','mifa_report','timestamp',)

