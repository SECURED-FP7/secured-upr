#from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from models import User, Group, UserGroupAssociation, UserPSA, PSAGroupAssociation, UserHSPLAssociation, UserMSPLAssociation, UserSGAssociation, UserAGAssociation, UserRAGAssociation, UserLowLevelConfAssociation, AdditionalInformation, MSPLPSAAssociation, ExecutedPSA, ReconciliationReport, UserSFA, UserIFA, UserMIFA
from serializers import UserSerializer, UserCreatorSerializer, PSAGroupAssociationSerializer, UserTypeSerializer,UserOptProfileSerializer, GroupSerializer, UserGroupAssociationSerializer, UserPSASerializer, UserHSPLAssociationSerializer, UserMSPLAssociationSerializer, UserSGAssociationSerializer, UserAGAssociationSerializer, UserRAGAssociationSerializer, UserLowLevelConfAssociationSerializer, AdditionalInformationSerializer, MSPLPSAAssociationSerializer, ExecutedPSASerializer, ReconciliationReportSerializer, UserSFASerializer, UserIFASerializer, UserMIFASerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
import uuid, logging, bcrypt, json, os
from ConfigParser import SafeConfigParser
from keystoneclient.v2_0 import client

import base64
#import parseOpenmano
from APIOpenmano import scenario_create
import APIOpenmano
from requests import post, delete

parser = SafeConfigParser()
parser.read('upr.conf')
logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))


tenant=parser.get('mano','tenant')
ipMano=parser.get('mano','ipMano')
portMano=parser.get('mano','portMano')
pathScenario=parser.get('mano','pathScenario')

urlbase='http://'+ipMano+':'+portMano+'/openmano/'
pathYaml=pathScenario+'/TVD/'
pathNed= pathScenario+'/NED/'


def check_token(request):

        if not parser.getboolean('Auth','auth'):
                return True
	username = os.getenv('OS_USERNAME',parser.get('keystone','admin_user'))
	auth_url = 'http://'+os.getenv('YOUR_IP',parser.get('general','your_ip')) +':'+ os.getenv('KEYSTONE_ADMIN_PORT',parser.get('keystone','admin_port'))+'/v2.0'
        password = os.getenv('OS_PASSWORD',parser.get('keystone','admin_pass'))
	if (request.method == "POST" or request.method == "PUT") and 'token' in request.data:
                auth_token = request.data['token']
		
	elif (request.method == "DELETE" or request.method == "GET") and 'token' in request.query_params:
		auth_token = request.query_params['token']
	
        else:
                return False

        admin_client = client.Client(username=username, auth_url=auth_url, password=password)
        try:
        	auth_result = admin_client.tokens.authenticate(token=auth_token)
                if not auth_result:
                	return False

                return True
        except: 
                return False



class UserCreateView (APIView):
	"""
	Interacts with the User List
	"""
	def post(self,request):
		"""
		Create a new user. Field name must be unique.
	
		Example:	POST UPR_URL/v1/upr/users
		  headers: {
        	    'Accept': 'application/json',
        	    'Content-type': 'application/json'
        	   }
  		data:    {
            		"user_id":"example name",
			"creator":"example name",
            		"integrityLevel":2,
			"password":"alice_pass",
			"type": "normal",
			"optimization_profile": "MIN_TRANFER_COSTMIN_LATENCY",
			"is_admin": "true",
			"is_cooperative": "true",
			"is_infrastructure": "false"
           	}

                              
		Status codes:
			 201 CREATED, if OK
			 400 BAD REQUEST, if incorrect JSON		


		
		Returns JSON with the received data, except the password, which is salted and hashed before storing. 

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: user_id 
		      description: (required)
		      required: true
		      type: string
		    - name: password
		      description: (required)
		      required: true
		      type: string
    		    - name: integrityLevel 
		      description: (required)
		      required: true
		      type: string
		    - name: type
		      description: (required)
		      required: true
		      type: string
		    - name: is_admin
		      description: (required)
		      required: true
		      type: boolean
		    - name: is_cooperative
		      description: (required)
		      required: true
		      type: boolean
		    - name: is_infrastructure
		      description: (required)
		      required: true
		      type: boolean
		    - name: creator 
		      description: (NOT required)
		      required: false
		      type: string
		    - name: optimization_profile
		      description: (NOT required)
		      required: false
		      type: string



		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)


		if set(('user_id','integrityLevel','type','is_admin','is_cooperative',
		  'is_infrastructure','password')).issubset(request.data):
			try:
				user=User.objects.get(user_id=request.data['user_id'])
				logging.warning('%s %s: 409 CONFLICT',request.method,'/v1/upr/users/')
				logging.debug('Request data: %s',request.data)
				return Response(status=status.HTTP_409_CONFLICT)
			except ObjectDoesNotExist:
				pass
			if "/" in request.data['user_id']:
				logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/upr/users/')
	                        logging.debug('Request data: %s',request.data)
        	                return Response(status=status.HTTP_400_BAD_REQUEST)


			salt = bcrypt.gensalt()
			hash = bcrypt.hashpw(request.data['password'].encode('utf-8'),salt)
			user= User(user_id=request.data['user_id'],salt=salt,hash=hash,
				integrityLevel=request.data['integrityLevel'],
				type=request.data['type'],is_infrastructure=request.data['is_infrastructure'],
				is_admin=request.data['is_admin'],is_cooperative=request.data['is_cooperative'])
			user.creator=None
			if 'creator' in request.data and request.data['creator'] is not None:
				try:
					user.creator=User.objects.get(user_id=request.data['creator'])
				except ObjectDoesNotExist:
					logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/')
					logging.debug('Request data: %s',request.data)
					return Response(status=status.HTTP_404_NOT_FOUND)
			
			if 'optimization_profile' in request.data:
				user.optimization_profile=request.data['optimization_profile']

		
			user.save()
			ser= UserSerializer(user)
			logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/')
			logging.debug('Request data: %s',request.data)
			logging.debug('Response data: %s', ser.data)
			return Response(status=status.HTTP_201_CREATED,data =ser.data)
		else:
			logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/upr/users/')
			logging.debug('Request data: %s',request.data)
			return Response(status=status.HTTP_400_BAD_REQUEST)	
	def get(self,request):
		"""
		Returns JSON with information of all the users.	If 'user_id' is passed as a query param, returns only that user 
		token -- (NOT required)
		user_id -- (NOT required)
		
		Example: 	GET UPR_URL/v1/upr/users
			Return:
			[
    			{
        			"user_id": "admin",
        			"creator": null,
        			"optimization_profile": "MIN_TRANFER_COSTMIN_LATENCY",
        			"integrityLevel": 1,
        			"type": "Expert User",
        			"is_cooperative": false,
        			"is_infrastructure": false,
        			"is_admin": true
    			},{
        			"user_id": "alice",
        			"creator": "admin",
        			"optimization_profile": "MIN_TRANFER_COSTMIN_LATENCY",
        			"integrityLevel": 1,
        			"type": "Enthusiastic User",
        			"is_cooperative": false,
        			"is_infrastructure": false,
        			"is_admin": false
    			}
			]
			
				GET UPR_URL/v1/upr/users?user_id=alice

			Return:
				{
				    "user_id": "alice",
				    "creator": "admin",
				    "optimization_profile": "MIN_TRANFER_COSTMIN_LATENCY",
				    "integrityLevel": 1,
				    "type": "Enthusiastic User",
				    "is_cooperative": false,
				    "is_infrastructure": false,
				    "is_admin": false
				}
		"""
		
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		users=User.objects.all()
		serial = None
		if 'user_id' in request.query_params:
			try:
				users=users.get(user_id=request.query_params['user_id'])
				serial=UserSerializer(users)
				logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/?user_id='+request.query_params['user_id'])		
				logging.debug('Response data: %s',serial.data)

			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/?user_id='+request.query_params['user_id'])
				logging.debug('Request data: %s',request.data)
				return Response(status=status.HTTP_404_NOT_FOUND)

		else:
			serial = UserSerializer(users,many=True)
			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/')		
			logging.debug('Response data: %s',serial.data)

		return Response (status=status.HTTP_200_OK,data=serial.data)

class UserTypeView(APIView):
	def get(self,request,user_id):
		"""
		Returns the type of the user

		Example:	GET UPR_URL/v1/upr/users/alice/UserType
	
			Returns:
			 {
			 	"type": "Enthusiastic User"
			 }

		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/UserType/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/UserType/')
	                logging.debug('Response data: %s',UserTypeSerializer(User.objects.get(user_id=user_id)).data)
			return Response(status=status.HTTP_200_OK,data=UserTypeSerializer(User.objects.get(user_id=user_id)).data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/UserType/')
			return Response(status=status.HTTP_404_NOT_FOUND)
class UserCreatorView(APIView):
	def get(self,request,user_id):
		"""
		Returns the creator of the user

		Example:	GET UPR_URL/v1/upr/users/alice/Creator
			Returns:
			 {
			 	"creator": "admin"
			 }

		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/Creator/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/Creator/')
	                logging.debug('Response data: %s',UserCreatorSerializer(User.objects.get(user_id=user_id)).data)						
			return Response(status=status.HTTP_200_OK,data=UserCreatorSerializer(User.objects.get(user_id=user_id)).data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/Creator')
			return Response(status=status.HTTP_404_NOT_FOUND)
class OptProfileView(APIView):
	def get(self,request,user_id):
		"""
		Returns the optimization profile of the user

		Example:	GET UPR_URL/v1/upr/users/alice/OptProfile
			Returns:
			 {
			 	"optimization_profile": "MIN_TRANFER_COSTMIN_LATENCY"
			 }

		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/OptProfile/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/OptProfile/')
	                logging.debug('Response data: %s',UserOptProfileSerializer(User.objects.get(user_id=user_id)).data)

			return Response(status=status.HTTP_200_OK,data=UserOptProfileSerializer(User.objects.get(user_id=user_id)).data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/OptProfile/')
			return Response(status=status.HTTP_404_NOT_FOUND)


class UserGroupView(APIView):
	def get(self,request,user_id):
		"""
		Returns groups that contain the user identified by user_id.
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/Groups/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			user_groups=UserGroupAssociation.objects.filter(user=User.objects.get(user_id=user_id))
        	        serial = UserGroupAssociationSerializer(user_groups,many=True)
                        logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/Groups/')
	                logging.debug('Response data: %s',serial.data)
        	        return Response (status=status.HTTP_200_OK, data=serial.data)
	
        	        #return Response (status=status.HTTP_200_OK, data=data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/Groups/')
			return Response(status=status.HTTP_404_NOT_FOUND)

class CreatedUsersView(APIView):
	def get (self,request,user_id):
		"""
		Returns the users created by this user

		Example:	GET UPR_URL/v1/upr/users/admin/CreatedUsers
			Returns:
				 
    			 {
				"users": [
       					"alice",
       					"bob"
				]
			}

		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/CreatedUsers/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			users=User.objects.filter(creator=User.objects.get(user_id=user_id))
			user_names=[]

			for u in users:
				user_names=user_names+[u.user_id]
			data={}
			data['users']=user_names

			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/CreatedUsers/')
	                logging.debug('Response data: %s',data)
			return Response(status=status.HTTP_200_OK,data=data)
			
		except:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/CreatedUsers/')
			return Response(status=status.HTTP_404_NOT_FOUND)
			

class UserAuthView (APIView):
	def post(self, request):
		"""
		Tries to authenticate the user. 

		Example POST UPR_URL/v1/upr/users/auth/
			data={
			'username':'alice', 
			'password':'alice_pass'
			}
		Status codes:
			200 OK if success
			401 Unauthorized if not
                ---
                    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
                    - name: username
                      description: (required)
                      required: true
                    - name: password
                      description: (required)
                      required: true
                      
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/auth/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			if set(('username','password')).issubset(request.data):
				user=User.objects.get(user_id=request.data['username'])
				received_hash=bcrypt.hashpw(request.data['password'].encode('utf-8'),user.salt.encode('utf-8'))
				if user.hash == received_hash:
					logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/auth/')
		        	        logging.debug('Request data: %s',request.data)

					return Response(status=status.HTTP_200_OK)
				else:
					logging.warning('%s %s:401 UNAUTHORIZED ',request.method, '/v1/upr/users/auth/')
		        	        logging.debug('Request data: %s',request.data)

					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/upr/users/auth/')
	        	        logging.debug('Request data: %s',request.data)

				return Response(status=status.HTTP_400_BAD_REQUEST)		
		except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND ',request.method, '/v1/upr/users/auth/')
	        	        logging.debug('Request data: %s',request.data)

				return Response(status=status.HTTP_404_NOT_FOUND)		

class UserView (APIView):
	def put (self, request, user_id):
		"""
		Updates the information about the user identified by user_id. 


		Example PUT UPR_URL/v1/upr/users/alice/

			data={
				'integrityLevel':3,
				'is_admin'=true
			}
			returns JSON with the updated data

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: password
		      description: (NOT required)
		      required: false
		      type: string
    		    - name: integrityLevel 
		      description: (NOT required)
		      required: false
		      type: string
		    - name: type
		      description: (NOT required)
		      required: false
		      type: string
		    - name: is_admin
		      description: (NOT required)
		      required: false
		      type: boolean
		    - name: is_cooperative
		      description: (NOT required)
		      required: false
		      type: boolean
		    - name: is_infrastructure
		      description: (NOT required)
		      required: false
		      type: boolean
		    - name: creator 
		      description: (NOT required)
		      required: false
		      type: string
		    - name: optimization_profile
		      description: (NOT required)
		      required: false
		      type: string

                      
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			user=User.objects.get(user_id=user_id)
			if 'integrityLevel' in request.data:
				user.integrityLevel=request.data['integrityLevel']
			if 'type' in request.data:
				user.type=request.data['type']
			if 'password' in request.data:
				user.salt=bcrypt.gensalt()
				user.hash=bcrypt.hashpw(request['password'].encode('utf-8'),user.salt)
			if 'is_admin' in request.data:
				user.is_admin=request.data['is_admin']
			if 'is_cooperative' in request.data:
				user.is_cooperative=request.data['is_cooperative']
			if 'is_infrastructure' in request.data:
				user.is_infrastructure=request.data['is_infrastructure']
			if 'optimization_profile' in request.data:
				user.optimization_profile=request.data['optimization_profile']

			if 'creator' in request.data: 
				try:
					user.creator=User.objects.get(user_id=request.data['creator'])
				except ObjectDoesNotExist:
					logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id)
					logging.debug('Request data: %s',request.data)
					return Response(status=status.HTTP_404_NOT_FOUND)

			user.save()
			logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id)
			logging.debug('Request data: %s',request.data)		
			return Response(status=status.HTTP_200_OK,data=UserSerializer(user).data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id)
			logging.debug('Request data: %s',request.data)
			return Response(status=status.HTTP_404_NOT_FOUND)
		except:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id)
			logging.debug('Request data: %s',request.data)

			return Response (status=status.HTTP_400_BAD_REQUEST)
	def delete (self, request, user_id):
		"""
		Deletes the user identified by user_id
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			user= User.objects.get(user_id=user_id)
			try:
				target=user
                                target_id=user_id
				try:
					elements=UserAGAssociation.objects.filter(target=target)
					for e in elements:
                	                	editor_id=e.editor_id
                        	        	nameScenario1='AG-'+target_id+'-EDIT-'+editor_id
                                		try:
                                        		delete (str(urlbase+tenant+'/scenarios/'+nameScenario1))
	                                	except:
        	                                	pass
				except:
					pass
				try:
					nameNed1=UserRAGAssociation.objects.get(target=target).ned_info
					nameScenario2='RAG-'+nameNed1+'-'+target_id
                               		try:
                                       		delete (str(urlbase+tenant+'/scenarios/'+nameScenario2))
	                               	except:
        	                            	pass
					import os.path
					nameNed1=UserRAGAssociation.objects.get(target=target_id).ned_info
        	                       	nameNed=str('NED-'+nameNed1)
                	               	nameXMLNed=pathNed+nameNed
                      			if os.path.isfile(nameXMLNed):
	                                       	f=open(nameXMLNed,'r')
        	                               	lineas=f.readlines()
                	                       	f.close()
                        	               	f=open(nameXMLNed,'w')
                                	        f.write('')
	       	                                f.close()
        	       	                        f=open(nameXMLNed,'a')
                	       	                for linea in lineas:
                        	       	                if linea!='RAG-'+nameNed1+('-')+target_id+'\n':
                                	       	                f.write(linea)
	                                        f.close()
       		                                APIOpenmano.parseNed(nameXML=nameXMLNed,nameScenario=nameNed)
               		                        nameDOC=pathNed+'/yamls/' +nameNed
                       		                try:
                                	                delete (str(urlbase+tenant+'/scenarios/'+nameNed))
	       	                                except:
        	       	                                pass
                	                if os.path.isfile(nameXMLNed):
                        	                scenario_create(nameDOC+'.yaml')
                                	else:
                                        	pass
				except:
					pass
				target=user_id
				try:
					elements3= User.objects.filter(creator=target)
					for e1 in elements3:
						target3=e1.user_id
						elements31=UserAGAssociation.objects.filter(target=e1.user_id)
						for e in elements31:
							print e.target
							editor3=e.editor_id
                        	        		target3=e.target_id
                                			nameScenario1='AG-'+target3+'-EDIT-'+editor3
							print nameScenario1
        	                        		try:
                	                        		delete (str(urlbase+tenant+'/scenarios/'+nameScenario1))
                        	        		except:
                                	        		pass
				except:
					pass
				try:
					nameNed1=UserRAGAssociation.objects.get(target=target3).ned_info
					nameScenario2='RAG-'+nameNed1+'-'+target3
                	               	try:
                        	       		delete (str(urlbase+tenant+'/scenarios/'+nameScenario2))
                               		except:
                              			pass

					import os.path
					nameNed1=UserRAGAssociation.objects.get(target=target3).ned_info
	                               	nameNed=str('NED-'+nameNed1)
        	               	       	nameXMLNed=pathNed+nameNed
	                      		if os.path.isfile(nameXMLNed):
	                                    	f=open(nameXMLNed,'r')
       	        	                       	lineas=f.readlines()
               	        	               	f.close()
                       	        	       	f=open(nameXMLNed,'w')
	                               	        f.write('')
		       	                        f.close()
        		       	                f=open(nameXMLNed,'a')
                	    	                for linea in lineas:
                        	       	                if linea!='RAG-'+nameNed1+('-')+target3+'\n':
                                	       	                f.write(linea)
		                               	f.close()
	       	        	                APIOpenmano.parseNed(nameXML=nameXMLNed,nameScenario=nameNed)
        	       	                        nameDOC=pathNed+'/yamls/' +nameNed
        	               	       	        try:
	                                      	        delete (str(urlbase+tenant+'/scenarios/'+nameNed))
	       		                        except:
        	       	                                pass
                	       	        if os.path.isfile(nameXMLNed):
                                	        scenario_create(nameDOC+'.yaml')
		                        else:
        		                         pass
				except:
					pass

				try:
					elements2=UserAGAssociation.objects.filter(editor_id=target)
					for e in elements2:
						target_id2=e.target_id
						editor_id=e.editor_id
						nameScenario='AG-'+target_id2+'-EDIT-'+editor_id
        	                                try:
                	                                delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
                        	                except:
							pass
				except:
					pass
				try:
					import os.path
					nameNed1=UserRAGAssociation.objects.get(target=target_id2).ned_info
                                	nameNed=str('NED-'+nameNed1)
                                	nameXMLNed=pathNed+nameNed
                               		if os.path.isfile(nameXMLNed):
                                        	f=open(nameXMLNed,'r')
                                        	lineas=f.readlines()
                                        	f.close()
                                        	f=open(nameXMLNed,'w')
	                                        f.write('')
        	                                f.close()
                	                        f=open(nameXMLNed,'a')
                        	                for linea in lineas:
                                	                if linea!='RAG-'+nameNed1+('-')+target_id2+'\n':
                                        	                f.write(linea)
	                                        f.close()
        	                                APIOpenmano.parseNed(nameXML=nameXMLNed,nameScenario=nameNed)
                	                        nameDOC=pathNed+'/yamls/' +nameNed
                        	                try:
	                                                delete (str(urlbase+tenant+'/scenarios/'+nameNed))
        	                                except:
                	                                pass
                                        if os.path.isfile(nameXMLNed):
                                                scenario_create(nameDOC+'.yaml')
                                        else:
                                                pass
				except:
					pass
				try:
					nameNed1=UserRAGAssociation.objects.get(target=target_id2).ned_info
					nameScenario='RAG-'+nameNed1+'-'+target_id2
                	               	try:
                                	       	delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
	                               	except:
        	                               	pass
				except:
					pass
			except:
				pass

			user.delete()
                        logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id)
			return Response(status=status.HTTP_204_NO_CONTENT)
		except:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id)
			return Response(status=status.HTTP_404_NOT_FOUND)

class UserPSAView (APIView):
	def get (self, request, user_id):
		"""
		Returns JSON with the PSAs associated with the user identified by user_id. Accepts parameter 'is_active'

			Example 
			 GET UPR_URL/v1/upr/users/alice/PSA/
			 Returns: 
			  [
				{
					"psa_id": 12345 
					"active": "True"
					"running_order" : 2
				},
				{
					"psa_id": 54321 
					"active": "False"
					"running_order" : 1			
				}
			  ] 
			
			 GET UPR_URL/v1/upr/users/alice/PSA/?is_active=yes
			 Returns: 
			  [
				{
					"psa_id": 12345 
					"active": "True"
					"running_order" : 2
				}
			  ] 
			
		token -- (NOT required)
		is_active -- (NOT required)

		"""

		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			user=User.objects.get(user_id=user_id)
			userPSA=UserPSA.objects.all().filter(user=user)
			if 'is_active' in request.query_params:
				userPSA=userPSA.filter(active=request.query_params['is_active'])
				logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/PSA?is_active='+request.query_params['is_active'])

                        else:
				logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/PSA')

			serial=UserPSASerializer(userPSA,many=True)
	
			logging.debug('Response data: %s',serial.data)
			return Response (status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSA')
			return Response (status=status.HTTP_404_NOT_FOUND)

	def put (self, request, user_id):
		"""

		Associates PSAs to the user identified by user_id. 

		Example PUT UPR_URL/v1/upr/users/alice/PSA/
		 data=	{'PSAList':[
				{
					'psa_id'='12345',
					'active':true,
                        		'running_order':2
				},
				{
					'psa_id'='54321',
					'active':false,
					'running_order':1
				}
			   ]
			}
		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string



		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/PSA')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			user=User.objects.get(user_id=user_id)
		except:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSA')
			return Response(status=status.HTTP_404_NOT_FOUND)
		if 'PSAList' in request.data:
			data=json.loads(request.data['PSAList'])
			for PSA in data:
				if 'psa_id' in PSA:
					userPSA=None
					created=False
					try:
						userPSA=UserPSA.objects.get(psa_id=PSA['psa_id'],user=User.objects.get(user_id=user_id))
					except ObjectDoesNotExist:
						userPSA=UserPSA(psa_id=PSA['psa_id'],user=User.objects.get(user_id=user_id))
						created=True
					if userPSA is not None:
						if 'active' in PSA:
							userPSA.active=PSA['active']
						if 'running_order' in PSA:
							userPSA.running_order=PSA['running_order']
						if 'mspl' in PSA:
							userPSA.mspl = PSA['mspl']
						userPSA.save()
				else:
        		                logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/PSA')
	                	        logging.debug('Request data: %s',request.data)
					return Response(status=status.HTTP_400_BAD_REQUEST)						
 			if created:
	                        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/PSA')
                                logging.debug('Request data: %s',request.data)
				return Response (status=status.HTTP_201_CREATED)
			else:
                                logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/PSA')
                                logging.debug('Request data: %s',request.data)
				return Response (status=status.HTTP_200_OK)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/PSA')
                        logging.debug('Request data: %s',request.data)
			return Response(status=status.HTTP_400_BAD_REQUEST)
	def delete (self, request, user_id):
		"""
		Deletes an User-PSA association. The psa_id is passed as a query_param.
		
		token -- (NOT required)
		psa_id -- (required)	
			
		Example DELETE UPR_URL/v1/upr/users/alice/PSA/?psa_id=12345

		Returns HTTP 204 No Content, if OK
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/PSA')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if 'psa_id' in request.query_params:
			try:
				userPSA = UserPSA.objects.get(psa_id=request.query_params['psa_id'],user=user_id)
				userPSA.delete()
                                logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/PSA?psa_id='+request.query_params['psa_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			except OnjectDoesNotExist:
                                logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSA?psa_id='+request.query_params['psa_id'])
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/PSA')
			return Response (status=status.HTTP_400_BAD_REQUEST)	

class HSPLView(APIView):
	def get (self, request):
		"""
		Retrieve HSPL. If 'target' and/or 'editor' are passed as a param, filter accordingly
		
		token -- (NOT required)
		target -- (NOT required)
		editor -- (NOT required)

		Example GET UPR_URL/v1/upr/users/HSPL?target=alice

		Returns [ 
			{ "hspl":"Example of hspl",
             		  "hspl_id": 1234,
			 "target": 'alice',
			 "editor": "alice"
           		},
			{  "hspl":"Example of hspl2",
             		  "hspl_id": 12345,
			 "target": 'alice',
			 "editor": "bob"
        		}
  		]

		GET UPR_URL/v1/users/HSPL?target=alice&editor=bob

                Returns [
                        {  "hspl":"Example of hspl2",
                          "hspl_id": 12345,
                         "target": 'alice',
                         "editor": "bob"
                        }
                ]

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/HSPL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			userHSPL = UserHSPLAssociation.objects.all()
			if 'target' in request.query_params:
				userHSPL=userHSPL.filter(target=User.objects.get(user_id=request.query_params['target']))		
				
			if 'editor' in request.query_params:
				userHSPL=userHSPL.filter(editor=User.objects.get(user_id=request.query_params['editor']))		

			
			serial = UserHSPLAssociationSerializer(userHSPL,many=True)
                        
			if set(('target','editor')).issubset(request.query_params):
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/HSPL/?target='+request.query_params['target']
				+'&editor='+request.query_params['editor'])
                        elif 'target' in request.query_params:
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/HSPL/?target='+request.query_params['target'])

			elif 'editor' in request.query_params:
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/HSPL/?editor='+request.query_params['editor'])
			else:
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/HSPL/')

			logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/HSPL/')
			return Response (status=status.HTTP_404_NOT_FOUND)

	def delete (self, request):
		"""
		Delete an HSPL. 'hspl_id' must be passed as a param
		
		token -- (NOT required)
		hspl_id -- (required)
		
		Example: DELETE UPR_URL/v1/upr/users/HSPL?hspl_id=1234

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/HSPL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)


		if 'hspl_id' in request.query_params:
			try:
				hspl = UserHSPLAssociation.objects.get(id=request.query_params['hspl_id'])
				hspl.delete()
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/HSPL/?hspl_id='+request.query_params['hspl_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/HSPL/?hspl_id='+request.query_params['hspl_id'])
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/HSPL/')
			return Response(status=status.HTTP_400_BAD_REQUEST)			
	
class UserHSPLView (APIView):
			
	def put (self, request, user_id):
		"""
		Create a new User-HSPL association, of which user_id is the editor.
		
		Example PUT UPR_URL/v1/upr/users/alice/HSPL
		
		data: {
			'hspl':'string e.g, "Son ; is/are not authorized to access ; Internet traffic ; (specific URL ,www.youtube.com) ; (time period, 07:00-21:00)'
			'target':'bob'
		}
		
		Return: {

			'id'=4321			
                        'hspl':'string e.g, "Son ; is/are not authorized to access ; Internet traffic ; (specific URL ,www.youtube.com) ; (time period, 07:00-21:00)'
                        'target':'bob',
			'editor':'alice'
		}
		
		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: target
		      description: (required)
		      required: true
		      type: string
		    - name: hspl
		      description: (required)
		      required: true
		      type: string


		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/HSPL')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('hspl','target')).issubset(request.data):
			try:
				hspl=UserHSPLAssociation(hspl=request.data['hspl'],
					target=User.objects.get(user_id=request.data['target']),
					editor=User.objects.get(user_id=user_id))
				hspl.save()
				serial= UserHSPLAssociationSerializer(hspl)
        	                logging.info('%s %s: 200 OK ',request.method, '/v1/upr/users/'+user_id+'/HSPL')
	                        logging.debug('Request data: %s',request.data)
	                        logging.debug('Response data: %s',serial.data)
				return Response(status=status.HTTP_201_CREATED,data=serial.data)
	
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/HSPL')
	                        logging.debug('Request data: %s',request.data)
				return Response (status=status.HTTP_404_NOT_FOUND)
					
		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/HSPL')
                        logging.debug('Request data: %s',request.data)
			return Response (status=status.HTTP_400_BAD_REQUEST)

			



class GroupListView (APIView):
	def get(self, request):
		"""
		Returns all groups.
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		groups = Group.objects.all()
		serial = GroupSerializer(groups,many=True)
                logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/')
                logging.debug('Response data: %s',serial.data)

		return Response (status=status.HTTP_200_OK, data=serial.data) 

	def post(self, request):
		"""
		Creates a new Group. 
		
		Example: PUT UPR_URL/v1/upr/groups
		data:{
			'name':'group',
			'description':'This is a group'		
		}

		Returns:{

			'name':'group',
                        'description':'This is a group'

		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: name
		      description: (required)
		      required: true
		      type: string
		    - name: description
		      description: (required)
		      required: true
		      type: string

		"""	
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('name','description')).issubset(request.data):
			group=Group(name=request.data['name'],description=request.data['description'])
			group.save()
			serial= GroupSerializer(group)
			logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/groups/')
                        logging.debug('Request data: %s',request.data)
	                logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_201_CREATED,data=serial.data)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/groups/')
                        logging.debug('Request data: %s',request.data)
			return Response(status=status.HTTP_400_BAD_REQUEST)

class GroupView (APIView):
	
	def put(self, request, group_id):
		"""
		Updates the description of a group identified by group_id or creates it if it doesn't exist. If creating, expects 'description' in the data

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: description
		      description: (NOT required) 
		      required: false
		      type: string

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/groups/'+group_id)
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		group=None
		created=False
		try:
			group=Group.objects.get(name=group_id)
			if 'description' in request.data:
				group.description=request.data['description']

		except ObjectDoesNotExist:
			group=Group(name=group_id)
			created=True
			if 'description' in request.data:
				group.description=request.data['description']
			else:
        	                logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/groups/'+group_id)
	                        logging.debug('Request data: %s',request.data)
				return Response(status=status.HTTP_400_BAD_REQUEST)
		group.save() 
		serial = GroupSerializer(group)
		if created:
			logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/groups/'+group_id)
                        logging.debug('Request data: %s',request.data)
                        logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_201_CREATED, data=serial.data)
		else:
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/'+group_id)
                        logging.debug('Request data: %s',request.data)
                        logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_200_OK, data=serial.data)

	def delete (self, request, group_id):
		"""
		Deletes the group identified by group_id
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			group=Group.objects.get(name=group_id)
			group.delete()
                        logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/groups/'+group_id+'/')
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/groups/'+group_id+'/')
			return Response(status=status.HTTP_404_NOT_FOUND)
 
class GroupUserView (APIView):
	def get (self, request, group_id):
		"""
		Returns JSON with the User-Groups association.
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/users')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		ser=UserGroupAssociationSerializer(UserGroupAssociation.objects.all().filter(group_id=group_id),many=True)
                logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/'+group_id+'/users')
		logging.debug('Response data: %s',ser.data)
		return Response(status=status.HTTP_200_OK,data=ser.data)

	def put (self, request, group_id):
		"""
		Associates a User and a Group 

		Example PUT UPR_URL/v1/upr/groups/groupname/users

		data: {
			'user_id':'alice'
		}
		
		Return: {
			'id':7654,
			'user'='alice',
			'group':'groupname'	
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: user_id
		      description: (required)
		      required: true
		      type: string

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/users')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		user=None
		group=None
		if 'user_id' in request.data:
			try:
				user=User.objects.get(user_id=request.data['user_id'])
				group=Group.objects.get(name=group_id)
				userGroup=None
				try:
					userGroup=UserGroupAssociation.objects.get(user=user,group=group)
				except ObjectDoesNotExist:
					userGroup = UserGroupAssociation(user=user,group=group)		
					userGroup.save()
				ser=UserGroupAssociationSerializer(userGroup)
        		        logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/'+group_id+'/users')
		                logging.debug('Request data: %s',request.data)
		                logging.debug('Response data: %s',ser.data)

				return Response(status=status.HTTP_200_OK,data=ser.data)
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/groups/'+group_id+'/users')
                                logging.debug('Request data: %s',request.data)

				return Response(status=status.HTTP_404_NOT_FOUND)	
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
	def delete (self, request, group_id):
		"""
		Removes the user passed as a param from the group identified by group_id 
		token -- (NOT required)		
		user_id -- (required)

		Example DELETE UPR_URL/v1/upr/groups/groupname/users?user_id=alice
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/users')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if 'user_id' in request.query_params:
			try:
				user=User.objects.get(user_id=request.query_params['user_id'])
				group=Group.objects.get(name=group_id)
				userGroup=UserGroupAssociation.objects.get(user=user,group=group)
				userGroup.delete()
                                logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/groups/'+group_id+'/users/?user_id='+request.query_params['user_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			except ObjectDoesNotExist:
                                logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/groups/'+group_id+'/users/?user_id='+request.query_params['user_id'])
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/groups/'+group_id+'/users/')
			return Response(status=HTTP_400_BAD_REQUEST)


class GroupPSAView (APIView):
	def get (self, request, group_id):
		"""
		Retrieves a JSON containing all the PSAs associated with the group identified by group_id
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/PSA')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		ser=PSAGroupAssociationSerializer(PSAGroupAssociation.objects.all().filter(group_id=group_id),many=True)
                logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/'+group_id+'/PSA')
		logging.debug('Request data: %s',request.data)
		return Response(status=status.HTTP_200_OK,data=ser.data)


	def put (self, request, group_id):
		"""
		Associate an PSA with the group identified by group_id
		
		Example: PUT UPR_URL/v1/upr/groups/groupname/PSA

		data:{
			'psa_id':123
		}
		Return:{
			'id'=234
			'psa_id':123
			'group':'groupname'
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: psa_id
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/PSA')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if 'psa_id' in request.data:
                        try:
                                group=Group.objects.get(name=group_id)
                               	groupPSA=None
                                try:
                                        groupPSA=PSAGroupAssociation.objects.get(psa_id=request.data['psa_id'],group=group)
                                except ObjectDoesNotExist:
                                        groupPSA = PSAGroupAssociation(psa_id=request.data['psa_id'],group=group)
                                        groupPSA.save()
                                ser=PSAGroupAssociationSerializer(groupPSA)
		                logging.info('%s %s: 200 OK',request.method, '/v1/upr/groups/'+group_id+'/PSA')
                                logging.debug('Request data: %s',request.data)
                                logging.debug('Response data: %s',ser.data)
                                return Response(status=status.HTTP_201_CREATED,data=ser.data)
                        except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/groups/'+group_id+'/PSA')
                                logging.debug('Request data: %s',request.data)
                                return Response(status=status.HTTP_404_NOT_FOUND)
                else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/groups/'+group_id+'/PSA')
                        logging.debug('Request data: %s',request.data)
                        return Response(status=status.HTTP_400_BAD_REQUEST)


	def delete (self, request, group_id):
		"""
		Removes the PSA passed as a param from the group identified by group_id 		
		token -- (NOT required)		
		psa_id -- (required)

		Example: DELETE UPR_URL/v1/upr/groups/groupname/PSA?psa_id=123
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/groups/'+group_id+'/PSA')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if 'psa_id' in request.query_params:
                        try:
                                group=Group.objects.get(name=group_id)
                                userPSA=PSAGroupAssociation.objects.get(psa_id=request.query_params['psa_id'],group=group)
                                userPSA.delete()
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/groups/'+group_id+'/PSA/?psa_id='+request.query_params['psa_id'])
                                return Response(status=status.HTTP_204_NO_CONTENT)
                        except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/groups/'+group_id+'/PSA/?psa_id='+request.query_params['psa_id'])
                                return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/groups/'+group_id+'/PSA')
                        return Response(status=HTTP_400_BAD_REQUEST)



class MSPLView (APIView):
	def get(self, request):
		"""
		Retrieve MSPL list. Filter parameters are passed as query params (internalID, target, editor and/or is_reconciled)
		
		token -- (NOT required)
		internalID -- (NOT required)
		target -- (NOT required)
		editor -- (NOT required)
		capability -- (NOT required)
		is_reconciled -- (NOT required)

		Example: GET UPR_URL/v1/upr/MSPL
		Returns [
		{
			'mspl_id'=2,
			'mpsl':'<xml...>',
			'internalID'='43',
			'target':'bob',
			'editor':'alice',
			'capability':'filter',
			'is_reconciled':true
			
		},{
                        'mspl_id'=3,
                        'mpsl':'<xml...>',
                        'internalID'='42',
                        'target':'charlie',
                        'editor':'bob',
                        'capability':'filter',
                        'is_reconciled':false

                }
		]
		
		GET UPR_URL/v1/upr/MSPL?internalID=42
                Returns [

                {
                        'mspl_id'=3,
                        'mpsl':'<xml...>',
                        'internalID'='42',
                        'target':'charlie',
                        'editor':'bob',
                        'capability':'filter',
                        'is_reconciled':false

                }
                ]

		GET UPR_URL/v1/upr/MSPL?target=charlie
                Returns [
                {
                        'mspl_id'=3,
                        'mpsl':'<xml...>',
                        'internalID'='42',
                        'target':'charlie',
                        'editor':'bob',
                        'capability':'filter',
                        'is_reconciled':false

                }
                ]

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/MPSL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:

			if set(('target','editor','is_reconciled','capability')).issubset(request.query_params):
				target= User.objects.get(user_id=request.query_params['target'])
				editor= User.objects.get(user_id=request.query_params['editor'])
				is_reconciled = (request.query_params['is_reconciled']=='true')
				mspl = UserMSPLAssociation.objects.get(target=target,editor=editor,
					capability=request.query_params['capability'],is_reconciled=is_reconciled)
			
				serial=UserMSPLAssociationSerializer(mspl)
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/MSPL/')
        	                logging.debug('Response data: %s',serial.data)
	
				return Response (status=status.HTTP_200_OK,data=serial.data)



			mspl= UserMSPLAssociation.objects.all()
			if 'internalID' in request.query_params:	
				mspl=mspl.filter(internalID=request.query_params['internalID'])
			if 'target' in request.query_params:
				mspl=mspl.filter(target=User.objects.get(user_id=request.query_params['target']))
			if 'editor' in request.query_params:
				mspl=mspl.filter(editor=User.objects.get(user_id=request.query_params['editor']))
			if 'is_reconciled' in request.query_params:
				is_reconciled = (request.query_params['is_reconciled']=='true')
				mspl=mspl.filter(is_reconciled=is_reconciled)
			if 'capability' in request.query_params:
				mspl=mspl.filter(capability=request.query_params['capability'])
        	        
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/MSPL/')
			
	                logging.debug('Request params: %s',str(request.query_params))
	                logging.debug('Response data: %s',UserMSPLAssociationSerializer(mspl,many=True).data)

			return Response (status=status.HTTP_200_OK,data=UserMSPLAssociationSerializer(mspl,many=True).data)
		except ObjectDoesNotExist:
        	        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/MSPL/')

			return Response (status=status.HTTP_404_NOT_FOUND)

	def post (self, request):
		"""
		Creates a new MSPL. 

		Example POST UPR_URL/v1/upr/MSPL
		data: {
		'target':'alice',
		'editor':'bob',
		'capability':'filter',
		'is_reconciled':false,
		'mspl':'<xml...>'
		}
		Returns {
                'mspl_id':2,
		'target':'alice',
                'editor':'bob',
                'capability':'filter',
                'is_reconciled':false,
                'mspl':'<xml...>',
		'internalID':null
                }

		POST UPR_URL/v1/upr/MSPL
                data: {
                'target':'alice',
                'editor':'bob',
                'capability':'filter',
                'is_reconciled':false,
                'mspl':'<xml...>',
		'internalID':'33'
                }
                Returns {
                'mspl_id':2,
                'target':'alice',
                'editor':'bob',
                'capability':'filter',
                'is_reconciled':false,
                'mspl':'<xml...>',
                'internalID':'33'
                }
		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: target
		      description: (required)
		      required: true
		      type: string
		    - name: editor
		      description: (required)
		      required: true
		      type: string
		    - name: capability
		      description: (required)
		      required: true
		      type: string
		    - name: is_reconciled
		      description: (required)
		      required: true
		      type: string
		    - name: mspl
		      description: (required)
		      required: true
		      type: string
		    - name: internalID
		      description: (NOT required) 
		      required: false
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/MPSL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		user = None
		if set(('target','editor','capability','is_reconciled','mspl')).issubset(request.data):
			editor=None
			target=None
			try:
				editor= User.objects.get(user_id=request.data['editor'])
				target= User.objects.get(user_id=request.data['target'])
			except ObjectDoesNotExist:
				return Response (status=status.HTTP_404_NOT_FOUND)
			try:
                                mspl = UserMSPLAssociation.objects.get(editor=editor,target=target,is_reconciled=request.data['is_reconciled'],
                                        capability=request.data['capability'])
                        	mspl.mspl=request.data['mspl']
			except ObjectDoesNotExist:

				mspl = UserMSPLAssociation(mspl=request.data['mspl'],editor=editor, target=target, 
					is_reconciled=request.data['is_reconciled'],
					capability=request.data['capability'])
			if 'internalID' in request.data:
				mspl.internalID=request.data['internalID']
			mspl.save()
       		        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/MSPL/')
	                logging.debug('Request data: %s',request.data)
	                logging.debug('Response data: %s',UserMSPLAssociationSerializer(mspl).data)

			return Response (status=status.HTTP_201_CREATED,data=UserMSPLAssociationSerializer(mspl).data)			
		else:
       		        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/MSPL')
	                logging.debug('Request data: %s',request.data)
	      		return Response (status=status.HTTP_400_BAD_REQUEST)	
	def delete (self, request):
		"""
		Deletes an MSPL
		token -- (NOT required)
		mspl_id -- (option 1)
		target -- (option 2)
		editor -- (option 2)
		is_reconciled -- (option 2)
		capability -- (option 2)

		Example DELETE UPR_URL/v1/upr/MSPL?mspl_id=3
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/MPSL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			if 'mspl_id' in request.query_params:
				UserMSPLAssociation.objects.get(mspl_id=request.query_params['mspl_id']).delete()			
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/MSPL/?mspl_id='+request.query_params['mspl_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			elif set(('target','editor','is_reconciled','capability')).issubset(request.query_params):
				target= User.objects.get(user_id=request.query_params['target'])
				editor= User.objects.get(user_id=request.query_params['editor'])
				is_reconciled = (request.query_params['is_reconciled'].lower()=='true')
				mspl = UserMSPLAssociation.objects.get(target=target,editor=editor,
					capability=request.query_params['capability'],is_reconciled=is_reconciled)
				#mspl = UserMSPLAssociation.objects.get(target=target,editor=editor,
				#	capability=request.query_params['capability'],is_reconciled=request.query_params['is_reconciled'])
				mspl.delete()
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/MSPL/?target='+request.query_params['target']
					+'&editor='+request.query_params['editor']+'&is_reconciled='+request.query_params['is_reconciled']+
					'&capability='+request.query_params['capability'])
				return Response (status=status.HTTP_204_NO_CONTENT)
			else:
       			        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/MSPL')
				return Response(status=status.HTTP_400_BAD_REQUEST)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/MSPL/')
                        logging.debug('Request params: %s',str(request.query_params))
                        return Response (status=status.HTTP_404_NOT_FOUND)				
class UserMSPLPSAView(APIView):
	def put(self,request,user_id):
		"""
		Create a new User-MSPL-PSA association

		Example PUT UPR_URL/v1/upr/users/alice/MSPL
		data:
		{
		'psa_id':'123',
		'mspl_id':3
		}
		Returns:
		{
		'id':2,
		'psa_id':'123',
		'mspl':3,
		'user_id':'alice'
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: psa_id
		      description: (required)
		      required: true
		      type: string
		    - name: mspl_id
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/MPSL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		user = None
		try:
			user= User.objects.get(user_id=user_id)
		except ObjectDoesNotExist:
       		        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
	               	return Response (status=status.HTTP_404_NOT_FOUND)
 
		if 'MSPL' in request.data:
			data=json.loads(request.data['MSPL'])
			for mspl in data:
				if set(('psa_id','mspl_id')).issubset(mspl):
					
					try:
						user_mspl=UserMSPLAssociation.objects.get(mspl_id=mspl['mspl_id'])
						mspl_psa = MSPLPSAAssociation(mspl=user_mspl,psa_id=mspl['psa_id'],user_id=user)
						mspl_psa.save()
		       		        	logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
	                			logging.debug('Request data: %s',request.data)
				                logging.debug('Response data: %s',MSPLPSAAssociationSerializer(mspl_psa).data)

						return Response (status=status.HTTP_201_CREATED, data=MSPLPSAAssociationSerializer(mspl_psa).data)
					except ObjectDoesNotExist:
						logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
                                                logging.debug('Request data: %s',request.data)
						return Response (status=status.HTTP_404_NOT_FOUND)
 
				else:
					logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
                                        logging.debug('Request data: %s',request.data)
					return Response (status=status.HTTP_400_BAD_REQUEST)
				
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
                        logging.debug('Request data: %s',request.data)
			return Response (status=status.HTTP_400_BAD_REQUEST)

	def get(self,request,user_id):
		"""
		Retrieve User-MSPL-PSA associations of the given user
		token -- (NOT required)
		"""	
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/MPSL/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
	
		try:
			serial=MSPLPSAAssociationSerializer(
				MSPLPSAAssociation.objects.filter(user_id=User.objects.get(user_id=user_id)),many=True)
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
                        logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/MSPL/')
			return Response (status=status.HTTP_404_NOT_FOUND)

class UserAGView(APIView):
	"""
	Retrieve AG with target the given user
	
	token -- (NOT required)
	editor -- (NOT required)

	"""
	def get(self,request,user_id):	
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/AG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			target=User.objects.get(user_id=user_id)
			if 'editor' in request.query_params:
				user_ag = UserAGAssociation.objects.get(target=target,editor=User.objects.get(user_id=request.query_params['editor']))
				serial = UserAGAssociationSerializer(user_ag)
		        	logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/AG/?editor='+request.query_params['editor'])

			else:
				user_ag= UserAGAssociation.objects.filter(target=target)
				serial=UserAGAssociationSerializer(user_ag,many=True)
		        	logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/AG/')
	                logging.debug('Response data: %s',serial.data)

			return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/AG/')

			return Response (status=status.HTTP_404_NOT_FOUND)
	
	def delete(self,request,user_id):
		
		"""
		Deletes the AG with target user_id and editor specified via params.		

		token -- (NOT required)
		editor -- (required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/AG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			if 'editor' in request.query_params:	
				target=User.objects.get(user_id=user_id)
                                target_id=user_id
                                editor_id=request.query_params['editor']

                                nameScenario='AG-'+target_id+'-EDIT-'+editor_id
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
                                except:
                                        pass

				UserAGAssociation.objects.get(target=target,editor=User.objects.get(user_id=request.query_params['editor'])).delete()
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/AG/?editor='+request.query_params['editor'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			else:
				logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/AG/')
	                        return Response (status=status.HTTP_400_BAD_REQUEST)

		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/AG/')
			return Response (status=status.HTTP_404_NOT_FOUND)
	
		

class AGView(APIView):
	def post(self,request):	
		"""
		Creates a new AG


		Example POST UPR_URL/v1/users/AG

		data:{
			'target_id':'alice',
			'editor_id':'bob',
			'application_graph':'Example AG'
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: target_id
		      description: (required)
		      required: true
		      type: string
		    - name: editor_id
		      description: (required)
		      required: true
		      type: string
		    - name: application_graph
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/AG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('target_id','editor_id','application_graph')).issubset(request.data):
			try:
				target=User.objects.get(user_id=request.data['target_id'])
				editor=User.objects.get(user_id=request.data['editor_id'])
				try:
					user_ag=UserAGAssociation.objects.get(target=target,editor=editor)
					user_ag.ag=request.data['application_graph']
				except ObjectDoesNotExist:
					user_ag=UserAGAssociation(target=target,editor=editor,ag=request.data['application_graph'])
				user_ag.save()
				serial=UserAGAssociationSerializer(user_ag)

                                target_id=request.data['target_id']
                                editor_id=request.data['editor_id']

                                nameScenario='AG-'+target_id+'-EDIT-'+editor_id

                                nameDOC=pathYaml+nameScenario+'.yaml'
                                nameXML=pathYaml+nameScenario+'.xml'

                                f=open(nameXML,'w')
                                try:
                                        f.write(base64.b64decode(user_ag.ag))
                                except:
                                        pass
                                f.close()

                                f=open(nameDOC,'w')
                                f.write('')
                                f.close()
                                try:
                                        APIOpenmano.parseAG(nameXML,nameScenario,nameDOC)
                                        #parseOpenmano.parseAG(nameXML,nameScenario,nameDOC)
                                except:
                                        pass
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
                                except:
                                        pass
                                try:
                                        scenario_create(nameDOC)
                                except:
                                        print 'formato xml no valido'

       			        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/AG/')
		                logging.debug('Request data: %s',request.data)
		                logging.debug('Response data: %s',serial.data)

				return Response(status=status.HTTP_201_CREATED,data=serial.data)
			except ObjectDoesNotExist:
       			        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/AG/')
		                logging.debug('Request data: %s',request.data)

				return Response (status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/AG/')
                        logging.debug('Request data: %s',request.data)

			return Response (status=status.HTTP_400_BAD_REQUEST)

class UserSGView(APIView):
	"""
	Retrieve SG with target the given user
	
	token -- (NOT required)
	editor -- (NOT required)

	"""
	def get(self,request,user_id):	
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/SG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			target=User.objects.get(user_id=user_id)
			if 'editor' in request.query_params:
				user_sg = UserSGAssociation.objects.get(target=target,editor=User.objects.get(user_id=request.query_params['editor']))
				serial = UserSGAssociationSerializer(user_sg)
		        	logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/SG/?editor='+request.query_params['editor'])

			else:
				user_sg= UserSGAssociation.objects.filter(target=target)
				serial=UserSGAssociationSerializer(user_sg,many=True)
		        	logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/SG/')
	                logging.debug('Response data: %s',serial.data)

			return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/SG/')

			return Response (status=status.HTTP_404_NOT_FOUND)
	
	def delete(self,request,user_id):
		
		"""
		Deletes the SG with target user_id and editor specified via params.		

		token -- (NOT required)
		editor -- (required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/SG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			if 'editor' in request.query_params:	
				target=User.objects.get(user_id=user_id)
                                target_id=user_id
                                editor_id=request.query_params['editor']


				UserSGAssociation.objects.get(target=target,editor=User.objects.get(user_id=request.query_params['editor'])).delete()
				logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/SG/?editor='+request.query_params['editor'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			else:
				logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/SG/')
	                        return Response (status=status.HTTP_400_BAD_REQUEST)

		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/SG/')
			return Response (status=status.HTTP_404_NOT_FOUND)
	
		

class SGView(APIView):
	def post(self,request):	
		"""
		Creates a new SG


		Example POST UPR_URL/v1/users/SG

		data:{
			'target_id':'alice',
			'editor_id':'bob',
			'service_graph':'Example SG'
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: target_id
		      description: (required)
		      required: true
		      type: string
		    - name: editor_id
		      description: (required)
		      required: true
		      type: string
		    - name: service_graph
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/SG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('target_id','editor_id','service_graph')).issubset(request.data):
			try:
				target=User.objects.get(user_id=request.data['target_id'])
				editor=User.objects.get(user_id=request.data['editor_id'])
				try:
					user_sg=UserSGAssociation.objects.get(target=target,editor=editor)
					user_sg.sg=request.data['service_graph']
				except ObjectDoesNotExist:
					user_sg=UserSGAssociation(target=target,editor=editor,sg=request.data['service_graph'])
				user_sg.save()
				serial=UserSGAssociationSerializer(user_sg)

                                target_id=request.data['target_id']
                                editor_id=request.data['editor_id']


       			        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/SG/')
		                logging.debug('Request data: %s',request.data)
		                logging.debug('Response data: %s',serial.data)

				return Response(status=status.HTTP_201_CREATED,data=serial.data)
			except ObjectDoesNotExist:
       			        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/SG/')
		                logging.debug('Request data: %s',request.data)

				return Response (status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/SG/')
                        logging.debug('Request data: %s',request.data)

			return Response (status=status.HTTP_400_BAD_REQUEST)
			
class UserRAGView(APIView):
	def get(self,request,user_id):	
		"""
	        Retrieve Reconciled AG with target the given user
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/RAG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			target=User.objects.get(user_id=user_id)
			serial=UserRAGAssociationSerializer(UserRAGAssociation.objects.get(target=target))
		        logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/RAG/')
	                logging.debug('Response data: %s',serial.data)
			return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/RAG/')

			return Response (status=status.HTTP_404_NOT_FOUND)
	def delete(self,request,user_id):	
		"""
	        Delete Reconciled AG with target the given user
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/RAG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			target=User.objects.get(user_id=user_id)

                        target_id=user_id
                        nameNed1=UserRAGAssociation.objects.get(target=target).ned_info
                        nameNed=str('NED-'+nameNed1)
                        nameXMLNed=pathNed+nameNed

                        import os.path
                        if os.path.isfile(nameXMLNed):
                                print "El fichero existe"
                                f=open(nameXMLNed,'r')
                                lineas=f.readlines()
                                f.close()
                                f=open(nameXMLNed,'w')
                                f.write('')
                                f.close()
                                f=open(nameXMLNed,'a')
                                for linea in lineas:
                                        if linea!='RAG-'+nameNed1+('-')+target_id+'\n':
                                                f.write(linea)
                                f.close()
                                #parseOpenmano.parseNed(nameXMLNed,nameNed)
                                APIOpenmano.parseNed(nameXML=nameXMLNed,nameScenario=nameNed)
                                nameDOC=pathNed+'/yamls/' +nameNed
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+nameNed))
                                except:
                                        pass

	                        if os.path.isfile(nameXMLNed):
        	                        scenario_create(nameDOC+'.yaml')
				else:
					pass
                                nameScenario='RAG-'+nameNed1+'-'+target_id
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
                                except:
                                        pass

                        else:
                                print "El fichero no existe"

			UserRAGAssociation.objects.filter(target=target).delete()

                        logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/RAG/')
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/RAG/')
			return Response (status=status.HTTP_404_NOT_FOUND)
	

class RAGView(APIView):
	def post(self,request):
                """
                Creates a new Reconciled AG


  
                 Example POST UPR_URL/v1/users/RAG
 
                 data:{
                        'target_id':'alice',
                        'ned_info':'Information about the NED',
                        'reconcile_application_graph':'Example reconcile application graph'
                 }

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: target_id
		      description: (required)
		      required: true
		      type: string
		    - name: ned_info
		      description: (required)
		      required: true
		      type: string
		    - name: reconcile_application_graph
		      description: (required)
		      required: true
		      type: string
                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/RAG/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('target_id','ned_info','reconcile_application_graph')).issubset(request.data):
			try:
				target=User.objects.get(user_id=request.data['target_id'])
				try:
					user_rag=UserRAGAssociation.objects.get(target=target)
					user_rag.ned_info=request.data['ned_info']
					user_rag.asg=request.data['reconcile_application_graph']
				except ObjectDoesNotExist:
					user_rag=UserRAGAssociation(target=target,ned_info=request.data['ned_info'],asg=request.data['reconcile_application_graph'])
		
				user_rag.save()
				serial=UserRAGAssociationSerializer(user_rag)
                                target_id=request.data['target_id']
                                nameNED=request.data['ned_info']
                                nameScenario='RAG-'+nameNED+('-')+target_id
                                nameDOC=pathYaml+nameScenario+'.yaml'
                                nameXMLTvd=pathYaml+nameScenario+'.xml'
                                nameXMLNed=pathNed+'NED-'+nameNED
                                nameXMLNed2=pathNed+'/yamls/'+'NED-'+nameNED

                                f=open(nameXMLTvd,'w')

                                
                                try:
                                        f.write(base64.b64decode(user_rag.asg))
                                except:
                                        pass
                                f.close()
                                f=open(nameDOC,'w')
                                f.write('')
                                f.close()
                                try:
                                        #parseOpenmano.parseAG(nameXMLTvd,nameScenario,nameDOC)
                                        APIOpenmano.parseAG(nameXMLTvd,nameScenario,nameDOC)
                                except:
                                        pass
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
                                except:
                                        pass
                                try:
                                        scenario_create(nameDOC)
                                except:
                                        pass
                                g=open(nameXMLNed,'a')
                                g.write(nameScenario+'\n')
                                g.close()
                                try:
                                        #parseOpenmano.parseNed(nameXMLNed,'NED-'+nameNED)
                                        APIOpenmano.parseNed(nameXMLNed,'NED-'+nameNED)
                                except:
                                        pass
                                try:
                                        delete (str(urlbase+tenant+'/scenarios/'+'NED-'+nameNED))
                                except:
                                        pass
                                try:
                                        scenario_create(nameXMLNed2+'.yaml')
                                except:
                                        print 'formato xml no valido'


				logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/RAG/')
                                logging.debug('Request data: %s',request.data)
                                logging.debug('Response data: %s',serial.data)
				return Response(status=status.HTTP_201_CREATED,data=serial.data)
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/RAG/')
                                logging.debug('Request data: %s',request.data)
				return Response (status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/RAG/')
                        logging.debug('Request data: %s',request.data)

			return Response (status=status.HTTP_400_BAD_REQUEST)


class SFAView(APIView):
	def get (self, request, user_id):
		"""
		Returns JSON with the sfa_report associated with an user and a MSPL

		Example GET
		Returns:{
			'user_id': 'father',
			'mspl_id': '12345',
			'sfa_report': 'html',
			'timestamp': '2015-11-27T11:23:07Z',
		}
		
		mspl_id -- (required)
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/sfa_report/'+mspl_id)

		try:
			mspl_id=request.query_params['mspl_id']
			serial=UserSFASerializer(UserSFA.objects.get(user_id=user_id,mspl_id=mspl_id))
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/sfa_report/?mspl_id='+request.query_params['mspl_id'])

                        logging.debug('Response data: %s',serial.data)	

			return Response(status=status.HTTP_200_OK,data=serial.data) 
                except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/sfa_report/?mspl_id='+request.query_params['mspl_id'])
                        return Response (status=status.HTTP_404_NOT_FOUND)


	def delete (self, request, user_id):
		"""
		Deletes a sfa_report

		Example: DELETE /v1/upr/users/{user_id}/sfa_report/?mspl_id={mspl_id}
		
		mspl_id -- (required)
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/sfa_report/sfa_report/?mspl_id='+request.query_params['mspl_id'])

		try:
			mspl_id=request.query_params['mspl_id']
			UserSFA.objects.get(user_id=user_id, mspl_id=mspl_id).delete()
			logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/sfa_report/sfa_report/?mspl_id='+request.query_params['mspl_id'])
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
       		        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/sfa_report/?mspl_id='+request.query_params['mspl_id'])
			return Response (status=status.HTTP_404_NOT_FOUND) 
 


        def post(self,request,user_id):
                """
		Creates or Update an entry in the sfa_report table, and associates the report to the user and MSPL
		

		Example
     		headers: {
			'Accept': 'application/json',
			'Content-type': 'application/json'
              	}
     		data: {
             		'mspl_id': '12345',
             		'sfa_report':'html...'
           	}
		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: mspl_id
		      description: (required)
		      required: true
		      type: string
		    - name: sfa_report
		      description: (required)
		      required: true
		      type: string		


		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/sfa_report/')

		try:
			mspl = UserMSPLAssociation.objects.get(target_id=user_id, mspl_id=request.data['mspl_id'] )
			try:
		                sfa=UserSFA.objects.get(user_id=user_id, mspl_id=request.data['mspl_id'])
				sfa.sfa_report=request.data['sfa_report']
                                sfa.save()
				serial=UserSFASerializer(sfa)
       	                        logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/sfa_report/')
               	                return Response (status=status.HTTP_200_OK,data=serial.data)

			except ObjectDoesNotExist:
				sfa=UserSFA(user_id=user_id, mspl_id=request.data['mspl_id'], sfa_report=request.data['sfa_report'])
                	        sfa.save()
				serial=UserSFASerializer(sfa)
	                        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/sfa_report/')
				return Response (status=status.HTTP_201_CREATED,data=serial.data)
		except ObjectDoesNotExist:
			return Response (status=status.HTTP_404_NOT_FOUND)


class UserIFAView(APIView):
        def get (self, request, user_id):
                """
		Returns JSON with the ifa_report associated with an user
		
		Example: GET /v1/upr/users/{user_id}/ifa_report/
  			'user_id' : 'father', 
		Returns:
		{
			'user_id': 'father', }
			'ifa_report' : 'html...',
			'timestamp' : '2015-11-27T11:23:07Z'
		}

                token -- (NOT required)

                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ifa_report/')



                try:
                        serial=UserIFASerializer(UserIFA.objects.get(user_id=user_id))
                        logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'ifa_report/')
                        logging.debug('Response data: %s',serial.data)

                        return Response(status=status.HTTP_200_OK,data=serial.data)
                except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/ifa_report/')
                        return Response (status=status.HTTP_404_NOT_FOUND)



        def delete (self, request, user_id):
                """
                Deletes a ifa_report report

		Example: DELETE /v1/upr/users/{user_id}/ifa_report/

                token -- (NOT required)
                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ifa_report/')

		try:
			UserIFA.objects.get(user_id=user_id).delete()
			logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'ifa_report/')
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
       		        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/ifa_report/')
	               	return Response (status=status.HTTP_404_NOT_FOUND) 



                return Response (status=status.HTTP_404_NOT_FOUND)

        def post(self,request,user_id):
                """
		Creates or Update an entry in the ifa_report table, and associates the report  to the user

                Example
		headers: {
			'Accept': 'application/json',
			'Content-type': 'application/json'
		}
		data: {
			'ifa_report' : 'html...'
           	}
                ---
                    parameters:
                    - name: token
                      description: (NOT required)
                      required: false
                      type: string
                    - name: ifa_report
                      description: (required)
                      required: true
                      type: string
                
                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ifa_report/')

		try:
			user = User.objects.get(user_id=user_id)
			try:
		                ifa=UserIFA.objects.get(user_id=user_id)
				ifa.ifa_report=request.data['ifa_report']
                                ifa.save()
				serial=UserIFASerializer(ifa)
       	                        logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/ifa_report/')
               	                return Response (status=status.HTTP_200_OK,data=serial.data)

			except ObjectDoesNotExist:
				ifa=UserIFA(user_id=user_id, ifa_report=request.data['ifa_report'])
                	        ifa.save()
				serial=UserIFASerializer(ifa)
	                        logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/ifa_report/')
				return Response (status=status.HTTP_201_CREATED,data=serial.data)
		except ObjectDoesNotExist:
			return Response (status=status.HTTP_404_NOT_FOUND)




class UserMIFAView(APIView):
        def get (self, request, user_id):
                """
                Returns JSON with the mifa_report associated with an user

		Example: GET /v1/upr/users/{user_id}/mifa_report/
			'user_id' : 'father',
		Returns:
		{
			'user_id': 'father', }
			'mifa_report' : 'html...',
			'timestamp' : '2015-11-27T11:23:07Z'
		}

                token -- (NOT required)

                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/mifa_report/')



                try:
                        serial=UserMIFASerializer(UserMIFA.objects.get(user_id=user_id))
                        logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'mifa_report/')
                        logging.debug('Response data: %s',serial.data)

                        return Response(status=status.HTTP_200_OK,data=serial.data)
                except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'mifa_report/')
                        return Response (status=status.HTTP_404_NOT_FOUND)


        def delete (self, request, user_id):
                """
                Deletes a mifa_report report

		Example: DELETE /v1/upr/users/{user_id}/mifa_report/

                token -- (NOT required)
                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/mifa_report/')

		try:
			UserMIFA.objects.get(user_id=user_id).delete()
			logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'mifa_report/')
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
       		        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/mifa_report/')
	               	return Response (status=status.HTTP_404_NOT_FOUND) 



                return Response (status=status.HTTP_404_NOT_FOUND)

        def post(self,request,user_id):
                """
                Creates or Update an entry in the mifa_report table, and associates the report  to the user

		Example
		headers: {
			'Accept': 'application/json',
			'Content-type': 'application/json'
		}
		data: {
			'mifa_report' : 'html...'
		}
                ---
                    parameters:
                    - name: token
                      description: (NOT required)
                      required: false
                      type: string
                    - name: mifa_report
                      description: (required)
                      required: true
                      type: string

                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/mifa_report/')

                try:
                        user = User.objects.get(user_id=user_id)
                        try:
                                mifa=UserMIFA.objects.get(user_id=user_id)
                                mifa.mifa_report=request.data['mifa_report']
                                mifa.save()
                                serial=UserMIFASerializer(mifa)
                                logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/mifa_report/')
                                return Response (status=status.HTTP_200_OK,data=serial.data)

                        except ObjectDoesNotExist:
                                mifa=UserMIFA(user_id=user_id, mifa_report=request.data['mifa_report'])
                                mifa.save()
                                serial=UserMIFASerializer(mifa)
                                logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/mifa_report/')
                                return Response (status=status.HTTP_201_CREATED,data=serial.data)
                except ObjectDoesNotExist:
                        return Response (status=status.HTTP_404_NOT_FOUND)









class UserLowLevelView(APIView):
	def post(self,request,user_id):	
                """
                Creates a new User-Low Level Config association.

                Example POST UPR_URL/v1/users/alice/PSAConf

                data:{
                        'psa_id':'123',
                        'configuration':'Low Level Configuration'
                }

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: psa_id
		      description: (required)
		      required: true
		      type: string
		    - name: configuration
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/PSAConf/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if set(('psa_id','configuration')).issubset(request.data):
			try:
				target=User.objects.get(user_id=user_id)
				user_low=None
				try:
					user_low=UserLowLevelConfAssociation.objects.get(target=target,psa=request.data['psa_id'])
					user_low.conf=request.data['configuration']
				except ObjectDoesNotExist:
					user_low=UserLowLevelConfAssociation(target=target,psa=request.data['psa_id'],conf=request.data['configuration'])
				user_low.save()
				serial=UserLowLevelConfAssociationSerializer(user_low)
				logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
                                logging.debug('Request data: %s',request.data)
                                logging.debug('Response data: %s',serial.data)
				return Response(status=status.HTTP_201_CREATED,data=serial.data)
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
                                logging.debug('Request data: %s',request.data)
				return Response (status=status.HTTP_404_NOT_FOUND)
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
                        logging.debug('Request data: %s',request.data)
			return Response (status=status.HTTP_400_BAD_REQUEST)
			
	def get(self,request,user_id):
		"""
		Retrieve Low Level configs associated with the given user. Can filter further if psa_id is passed as a param.
		token -- (NOT required)		
		psa_id -- (NOT required)

		Example: GET UPR_URL/v1/users/alice/PSAConf
		Returns [{
 		 "psa_id":"123",
		 "configuration":  "zip"    
		},{
 		 "psa_id":"456",
 		 "configuration":  "zip"    
		}]

		GET UPR_URL/v1/users/alice/PSAConf?psa_id=123
                Returns {
                 "psa_id":"123",
                 "configuration":  "zip"
                }

		"""		
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/PSAConf/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			low_level=UserLowLevelConfAssociation.objects.filter(target=User.objects.get(user_id=user_id))
			if 'psa_id' in request.query_params:
				low_level=low_level.get(psa=request.query_params['psa_id'])
				serial=UserLowLevelConfAssociationSerializer(low_level)
                                logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/PSAConf/?psa_id='+request.query_params['psa_id'])
                                logging.debug('Response data: %s',serial.data)
				return Response(status=status.HTTP_200_OK,data=serial.data)
			else:
				serial=UserLowLevelConfAssociationSerializer(low_level,many=True)
                                logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
                                logging.debug('Response data: %s',serial.data)
				return Response(status=status.HTTP_200_OK,data=serial.data)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
                        logging.debug('Request data: %s',request.data)

			return Response(status=status.HTTP_404_NOT_FOUND)

	def delete(self,request,user_id):
		"""
		Deletes the Low Level config of the given user for the given PSA. Needs param psa_id.
		token -- (NOT required)
		psa_id -- (required)
	
		"""	
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/PSAConf/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			low_level=UserLowLevelConfAssociation.objects.filter(target=User.objects.get(user_id=user_id))

			if 'psa_id' in request.query_params:
				low_level=low_level.get(psa=request.query_params['psa_id'],target=User.objects.get(user_id=user_id))
				low_level.delete()
	                        logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/PSAConf/?psa_id='+request.query_params['psa_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)
			else:
	                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
				return Response(status=status.HTTP_400_BAD_REQUEST)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/PSAConf/')
			return Response(status=status.HTTP_404_NOT_FOUND)
		

		

class ExecutePSAView(APIView):
	def put(self,request,user_id):
		"""
		Create a new executed PSA
		Example PUT UPR_URL/v1/upr/users/alice/ExecutePSA/
		data:{
		'psa_id':'123'
		}

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: psa_id
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ExecutePSA/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		if 'psa_id' in request.data:
			try:
				ex=ExecutedPSA(psa_id=request.data['psa_id'],user_id=User.objects.get(user_id=user_id))			
				ex.save()		
				logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
                                logging.debug('Request data: %s',request.data)
                                logging.debug('Response data: %s',ExecutedPSASerializer(ex).data)
				return Response(status=status.HTTP_201_CREATED,data=ExecutedPSASerializer(ex).data)
			except ObjectDoesNotExist:
	                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
				return Response (status=status.HTTP_404_NOT_FOUND)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
			return Response (status=status.HTTP_400_BAD_REQUEST)

	def get(self,request,user_id):
		"""
		Retrieve executed PSAs of the given user
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ExecutePSA/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			ex=ExecutedPSA.objects.filter(user_id=User.objects.get(user_id=user_id))			
			data={}
			psas=[]
			for psa in ex:
				psas=psas+[psa.psa_id]
			data['psa_id']=psas
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
                        logging.debug('Response data: %s',str(data))
			return Response(status=status.HTTP_200_OK,data=data)
		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
			return Response (status=status.HTTP_404_NOT_FOUND)
		


	def delete(self,request,user_id):
		"""
		Delete an executed PSA.
		
		token -- (NOT required)
		psa_id -- (required)

		Example DELETE UPR_URL/v1/upr/users/alice/ExecutePSA/?psa_id=123

		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/ExecutePSA/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		if 'psa_id' in request.query_params:
			try:
				ex=ExecutedPSA.objects.filter(psa_id=request.query_params['psa_id'],user_id=User.objects.get(user_id=user_id))
				ex.delete()
                                logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/?psa_id='+request.query_params['psa_id'])
				return Response(status=status.HTTP_204_NO_CONTENT)

			except ObjectDoesNotExist:
                                logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/?psa_id='+request.query_params['psa_id'])
				return Response (status=status.HTTP_404_NOT_FOUND)

		else:
                        logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/ExecutePSA/')
			return Response (status=status.HTTP_400_BAD_REQUEST)
		
	
class ReconciliationReportView(APIView):


	def get(self,request,user_id):
		"""
		Get reconciliation report. Accepts ned_info as param

		token -- (NOT required)
		ned_info -- (NOT required)
		
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			rr=ReconciliationReport.objects.filter(user=User.objects.get(user_id=user_id),latest=True)
			if 'ned_info' in request.query_params:
				rr=rr.get(ned_info=request.query_params['ned_info'])
				ser= ReconciliationReportSerializer(rr)
				logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/?ned_info='
				+request.query_params['ned_info'])
        	                logging.debug('Response data: %s',ser.data)
	                        return Response(status=status.HTTP_200_OK,data=ser.data)
			ser= ReconciliationReportSerializer(rr,many=True)
			logging.info('%s %s: 200 OK',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        logging.debug('Response data: %s',ser.data)
                        return Response(status=status.HTTP_200_OK,data=ser.data)

		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
			return Response (status=status.HTTP_404_NOT_FOUND)
			
	def post(self,request,user_id):
		"""
		Create a new reconciliation report

		---
		    parameters:
		    - name: token
		      description: (NOT required)
		      required: false
		      type: string
		    - name: ned_info
		      description: (required)
		      required: true
		      type: string
		    - name: reconciliation_report
		      description: (required)
		      required: true
		      type: string
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		user=None
		try:
			user=User.objects.get(user_id=user_id)
		except ObjectDoesNotExist:
			logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response (status=status.HTTP_404_NOT_FOUND)
		if set(('ned_info','reconciliation_report')).issubset(request.data):
 			rr=None
			
			try:
				old=ReconciliationReport.objects.get(user=user,ned_info=request.data['ned_info'],latest=True)
				old.latest=False
				old.save()
			except ObjectDoesNotExist:
				pass

			
			rr=ReconciliationReport(user=user,ned_info=request.data['ned_info'],
				reconciliation_report=request.data['reconciliation_report'],latest=True)

			ser= ReconciliationReportSerializer(rr)
			rr.save()
			logging.info('%s %s: 201 CREATED',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        logging.debug('Response data: %s',ser.data)
                        return Response(status=status.HTTP_201_CREATED,data=ser.data)	
		else:
			logging.warning('%s %s: 400 BAD REQUEST',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response (status=status.HTTP_400_BAD_REQUEST)	

	def delete(self,request,user_id):
		"""
		Deletes a reconciliation report		
		token -- (NOT required)
		ned_info -- (NOT required)
		
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
                        user=User.objects.get(user_id=user_id)
			rr=ReconciliationReport.objects.filter(user=user)
			if 'ned_info' in request.query_params:
				rr=rr.get(ned_info=request.query_params['ned_info'])			
			rr.delete()
			logging.info('%s %s: 204 NO CONTENT',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        
			if 'ned_info' in request.query_params:
				logging.debug('ned_info=%s',request.query_params['ned_info'])
			return Response(status=status.HTTP_204_NO_CONTENT)

                except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method, '/v1/upr/users/'+user_id+'/reconciliation_report/')
                        return Response (status=status.HTTP_404_NOT_FOUND)

