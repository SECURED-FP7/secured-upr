from requests import get, put, post, delete
import json
from subprocess import call
import urllib2, upr_client, os

c=upr_client.UPRClient(os.getenv('UPR_URL','http://195.235.93.146:8081'))
test_user='test_user'
test_pass='password'
test_integrity_level=2
test_is_cooperative=False
test_type='normal'
test_is_infrastructure=False
test_is_admin=False
test_creator='test_admin'
test_opt="MIN_TRANFER_COSTMIN_LATENCY"
test_psa='123'
test_group='test_group'
test_group_description='This is the description' 
sfa_report='sfa_report_prueba'
ifa_report='ifa_report_prueba'
mifa_report='mifa_report_prueba'


#User
def test_create_user():

	r=c.create_user(user_id=test_creator,password=test_pass, integrityLevel=test_integrity_level,
		type=test_type, is_cooperative=test_is_cooperative, is_infrastructure=test_is_infrastructure, 
		is_admin=True,creator=None,optimization_profile=test_opt)
	assert r.status_code==201
	

	r=c.create_user(user_id=test_user,password=test_pass, integrityLevel=test_integrity_level,
		type=test_type, is_cooperative=test_is_cooperative, is_infrastructure=test_is_infrastructure, 
		is_admin=test_is_admin,creator=test_creator,optimization_profile=test_opt)

	assert r.status_code==201
	data=json.loads(r.text)
	assert set(('user_id','integrityLevel','is_cooperative','is_infrastructure','is_admin','creator','optimization_profile','type')).issubset(data)

	r=c.create_user(user_id=test_user,password=test_pass, integrityLevel=test_integrity_level,
		type=test_type, is_cooperative=test_is_cooperative, is_infrastructure=test_is_infrastructure, 
		is_admin=test_is_admin,creator=test_creator)
	
	assert r.status_code==409

def test_user_list():
	r=c.get_user_list()
	data=json.loads(r.text)
	assert data[0]

	r=c.get_user_list(user_id=test_user)	
	data=json.loads(r.text)
	assert data['user_id']==test_user

	
def test_user_type():
	r=c.get_user_type(user_id=test_user)
	data=json.loads(r.text)
	assert data['type']==test_type

def test_user_creator():
	r=c.get_user_creator(user_id=test_user)
	data=json.loads(r.text)
	assert data['creator']==test_creator

def test_user_opt_profile():
	r=c.get_user_opt_profile(user_id=test_user)
	data=json.loads(r.text)
	assert data['optimization_profile']==test_opt

def test_created_users():
	r=c.get_created_users(user_id=test_creator)
	data=json.loads(r.text)
	assert test_user in data['users']

def test_auth_user():
	r=c.auth_user(user=test_user,password=test_pass)
	assert r.status_code==200

	r=c.auth_user(user=test_user,password=test_pass+'asdf')
	assert r.status_code==401

		

def test_update_user():
	r=c.update_user(user_id=test_user,is_cooperative=not test_is_cooperative)
	assert r.status_code==200
	data=json.loads(r.text)
	assert data['is_cooperative']!= test_is_cooperative


#User-PSA
def test_user_psa():
	"""
	data={}
	psas=[]
	psas=psas+[{'psa_id':test_psa,'active':True,'running_order':1}]
	data['PSAList']=psas
	r=c.put_user_psa(user_id=test_user,data=data)
	"""
	
	r=c.put_user_psa(user_id=test_user,psa_id=test_psa,active=True,running_order=1)

	assert r.status_code==201
	
	r=c.delete_user_psa(user_id=test_user, psa_id=test_psa)
	assert r.status_code==204


#HSPL

def test_hspl():
	r=c.put_user_hspl(user_id=test_user,hspl="Test HSPL",target=test_user)
	assert r.status_code==201
	r=c.get_hspl(target=test_user)
	data=json.loads(r.text)
	assert data[0]['target']==test_user
	r=c.delete_hspl(user_id=test_user,hspl_id=data[0]['id'])
	assert r.status_code==204
	



def test_create_group():
	r=c.create_group(name=test_group,description=test_group_description)
	assert r.status_code==201

	r=c.update_group(group=test_group,description=test_group_description+'asdfg')
	assert r.status_code==200

def test_user_group():
	r=c.associate_user_group(user_id=test_user,group=test_group)
	assert r.status_code==200

	r=c.delete_user_group(user=test_user,group=test_group)

	assert r.status_code==204
	
def test_psa_group():
	r=c.put_group_psa(group=test_group,psa_id=test_psa)
	assert r.status_code==201
	
	r=c.delete_group_psa(group=test_group,psa_id=test_psa)
	assert r.status_code==204
	

def test_delete_group():
	r=c.delete_group(group_id=test_group)
	assert r.status_code==204

#MSPL

def test_mspl():
	r=c.create_mspl(target=test_user,editor=test_user,capability='filter',is_reconciled=False,mspl='Example MSPL',internalID=9)
	assert r.status_code==201
	data=json.loads(r.text)
	mspl_id=data["mspl_id"]
	
	r=c.put_user_mspl_psa(user_id=test_user,psa_id=test_psa,mspl_id=mspl_id)
	assert r.status_code==201
	
	r=c.delete_mspl(mspl_id=mspl_id)

	assert r.status_code==204
	


#AG
def test_ag():
	r=c.post_ag(target_id=test_user,editor_id=test_user,ag='Example AG')	

	assert r.status_code==201

	r=c.get_user_ag(target=test_user,editor=test_user)
	data=json.loads(r.text)
	assert data['ag']=='Example AG'

	r=c.delete_user_ag(target=test_user,editor=test_user)
	assert r.status_code==204

#RAG
def test_rag():
	r=c.post_rag(target_id=test_user,ned_info='NED Info',rag='Example RAG')	

	assert r.status_code==201

	r=c.get_user_rag(user_id=test_user)
	data=json.loads(r.text)
	assert data['asg']=='Example RAG'

	r=c.delete_user_rag(user_id=test_user)
	assert r.status_code==204

	r=c.get_user_rag(user_id=test_user)
	assert r.status_code==404


#Low Level
def test_low_level():
	r=c.post_psaconf(user_id=test_user,psa_id=test_psa,configuration='Example Configuration')	

	assert r.status_code==201

	r=c.get_user_psaconf(user_id=test_user,psa_id=test_psa)
	data=json.loads(r.text)
	assert data['conf']=='Example Configuration'

	r=c.delete_user_psaconf(user_id=test_user,psa_id=test_psa)
	assert r.status_code==204

	r=c.get_user_psaconf(user_id=test_user,psa_id=test_psa)
	assert r.status_code==404

def test_executed_psa():
	r=c.put_executed_psa(user_id=test_user,psa_id=test_psa)
	assert r.status_code==201

	r=c.delete_executed_psa(user_id=test_user,psa_id=test_psa)
	assert r.status_code==204

#Reconciliation Report
def test_reconciliation_report():
	test_ned_info='NED1'
	test_report='Test Report'
	r=c.post_reconciliation_report(user_id=test_user,ned_info=test_ned_info,reconciliation_report=test_report)
	assert r.status_code==201

	r=c.get_reconciliation_report(user_id=test_user)
	data=json.loads(r.text)
	assert data[0]['reconciliation_report']==test_report


	r=c.get_reconciliation_report(user_id=test_user,ned_info=test_ned_info)
	data=json.loads(r.text)
	assert data['reconciliation_report']==test_report
	
	r=c.delete_reconciliation_report(user_id=test_user,ned_info=test_ned_info)
	assert r.status_code==204


#SFA_REPORT
def test_sfa_report():
	r=c.create_mspl(target=test_user,editor=test_user,capability='filter',is_reconciled=False,mspl='Example MSPL',internalID=9)
	assert r.status_code==201
	data=json.loads(r.text)
	mspl_id=data["mspl_id"]

        r=c.post_sfa(user_id=test_user, mspl_id=mspl_id, sfa_report=sfa_report)
        assert r.status_code==201

        r=c.post_sfa(user_id=test_user, mspl_id=mspl_id, sfa_report='new_sfa')
        assert r.status_code==200

        r=c.get_sfa(user_id=test_user, mspl_id=mspl_id)
        assert r.status_code==200


        r=c.delete_sfa(user_id=test_user, mspl_id=mspl_id)
        assert r.status_code==204

        r=c.delete_mspl(mspl_id=mspl_id)
        assert r.status_code==204

#IFA_REPORT
def test_ifa_report():
        r=c.post_ifa(user_id=test_user, ifa_report=ifa_report)
        assert r.status_code==201

        r=c.post_ifa(user_id=test_user, ifa_report='new_ifa')
        assert r.status_code==200

        r=c.get_ifa(user_id=test_user)
        data=json.loads(r.text)
        assert r.status_code==200

        r=c.delete_ifa(user_id=test_user)
        assert r.status_code==204

#MIFA_REPORT
def test_mifa_report():
        r=c.post_mifa(user_id=test_user, mifa_report=mifa_report)
        assert r.status_code==201

        r=c.post_mifa(user_id=test_user, mifa_report='new_ifa')
        assert r.status_code==200

        r=c.get_mifa(user_id=test_user)
        data=json.loads(r.text)
        assert r.status_code==200

        r=c.delete_mifa(user_id=test_user)
        assert r.status_code==204



def test_delete_user():
	r=c.delete_user(user_id=test_creator)
	assert r.status_code==204

