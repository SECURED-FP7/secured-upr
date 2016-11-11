

from requests import get, delete
import yaml, os
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('../upr.conf')
tenant=parser.get('mano','tenant')
remoteIp=parser.get('mano','ipMano')
remotePort=parser.get('mano','portMano')
urlbase='http://'+remoteIp+':'+remotePort+'/openmano/'
pathScenario=parser.get('mano','pathScenario')



filelist = [ f for f in os.listdir(pathScenario+'/TVD/')]
for f in filelist:
    os.remove(pathScenario+'/TVD/'+f)

filelist = [ f for f in os.listdir(pathScenario+'/NED/')]
for f in filelist:
	if f == 'yamls':
		pass
	else:
    		os.remove(pathScenario+'/NED/'+f)

filelist = [ f for f in os.listdir(pathScenario+'/NED/yamls/')]
for f in filelist:
    os.remove(pathScenario+'/NED/yamls/'+f)



mano_response=get(urlbase+tenant+'/scenarios')
content = mano_response.json()

list=yaml.safe_dump(content, indent=4, default_flow_style=False)
g=list.split(' ')

i=0
b=0
name={}
for a in g:
 i=i+1
 if a=='name:':
  #print g[i]
  name[int(b)]=g[i]
  b=b+1
 else:
  pass



for g in name:
 t=name[g].split('\n')
 response=delete(str(urlbase+tenant+'/scenarios/'+t[0]))
 print t
 print response

