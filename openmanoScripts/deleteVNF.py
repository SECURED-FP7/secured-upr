from requests import get, delete
import yaml
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('../upr.conf')
tenant=parser.get('mano','tenant')
remoteIp=parser.get('mano','ipMano')
remotePort=parser.get('mano','portMano')
urlbase='http://'+remoteIp+':'+remotePort+'/openmano/'

mano_response=get(urlbase+tenant+'/vnfs')
print mano_response
content=mano_response.json()
print yaml.safe_dump(content, indent=4, default_flow_style=False)
list= yaml.safe_dump(content, indent=4, default_flow_style=False)
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
 response=delete(str(urlbase+tenant+'/vnfs/'+t[0]))
 print t
 print response
