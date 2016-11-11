import yaml, requests, os



from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('../upr.conf')
tenant=parser.get('mano','tenant')
remoteIp=parser.get('mano','ipMano')
remotePort=parser.get('mano','portMano')
pathScenario=parser.get('mano','pathScenario')

dir1= pathScenario+'/TVD'
dir2= pathScenario+'/NED'
dir3= pathScenario+'/NED/yamls'


os.mkdir(dir1)
os.mkdir(dir2)
os.mkdir(dir3)


headers_req = {'Accept': 'application/json', 'content-type': 'application/json'}
URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)

pathlocal=os.getcwd()
doc1=pathlocal+'/linux.yaml'
doc2=pathlocal+'/PSA.yaml'
doc3=pathlocal+'/TVD.yaml'

dataset=yaml.load(open(doc1,'rb'))
mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)

dataset=yaml.load(open(doc2,'rb'))
mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)

dataset=yaml.load(open(doc3,'rb'))
mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)


