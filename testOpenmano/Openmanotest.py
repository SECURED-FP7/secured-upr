

from requests import get, delete
import yaml, os
from ConfigParser import SafeConfigParser
import json
from subprocess import call
import urllib2 
#import upr_client
import requests

#c=upr_client.UPRClient(os.getenv('UPR_URL','http://195.235.93.146:8081'))
parser = SafeConfigParser()
parser.read('../upr.conf')
tenant=parser.get('mano','tenant')
remoteIp=parser.get('mano','ipMano')
remotePort=parser.get('mano','portMano')
urlbase='http://'+remoteIp+':'+remotePort+'/openmano/'
pathScenario=parser.get('mano','pathScenario')


nameVnf='linux_prueba'
nameScenario='prueba'


#VNF

def test_create_vnf():
	headers_req = {'Accept': 'application/json', 'content-type': 'application/json'}
	URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)

	pathlocal=os.getcwd()
	doc1=pathlocal+'/linux_prueba.yaml'
	doc2=pathlocal+'/PSA.yaml'

	dataset=yaml.load(open(doc1,'rb'))	
	mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
	assert str(mano_response)=='<Response [200]>'

	dataset=yaml.load(open(doc1,'rb'))	
	mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
	assert str(mano_response)=='<Response [409]>'


def test_delete_vnf():
	mano_response=delete(str(urlbase+tenant+'/vnfs/'+nameVnf))
	assert str(mano_response)=='<Response [200]>'



#SCENARIO

def test_create_scenario():
        headers_req = {'content-type': 'application/yaml'}
        URLrequest = "http://%s:%s/openmano/%s/scenarios" %(remoteIp, remotePort, tenant)

        pathlocal=os.getcwd()

        d=(open(pathlocal+'/'+nameScenario+'.yaml','rb'))
        dataset=d.read()
        d.close()
        mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
        assert str(mano_response)=='<Response [200]>'

        mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
        assert str(mano_response)=='<Response [409]>'



def test_delete_scenario():
        mano_response=delete(str(urlbase+tenant+'/scenarios/'+nameScenario))
        assert str(mano_response)=='<Response [200]>'




