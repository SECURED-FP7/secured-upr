from upr.models import UserRAGAssociation
from upr.models import UserAGAssociation
from upr.serializers import UserRAGAssociationSerializer
from upr.serializers import UserAGAssociationSerializer
rag=UserRAGAssociation.objects.all()
ser=UserRAGAssociationSerializer(rag,many=True)
AG=UserAGAssociation.objects.all()
ser1=UserAGAssociationSerializer(AG,many=True)
import base64
#import parseOpenmano
import os
from requests import post, put, delete
import APIOpenmano
from APIOpenmano import scenario_create


from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('upr.conf')
tenant=parser.get('mano','tenant')
ipMano=parser.get('mano','ipMano')
portMano=parser.get('mano','portMano')
pathScenario=parser.get('mano','pathScenario')

urlbase='http://'+ipMano+':'+portMano+'/openmano/'
pathTVD=pathScenario+'/TVD/'
pathNed= pathScenario+'/NED/'


for r in rag:
 nameNED='NED-'+r.ned_info
 nameXMLNed=pathNed+nameNED
 g=open(nameXMLNed,'w')
 g.write('')
 g.close()



for r in AG:
 nameScenario='AG-'+r.target_id+'-EDIT-'+r.editor_id
 nameDOC=pathTVD+nameScenario+'.yaml'
 nameXMLTvd=pathTVD+nameScenario+'.xml'
 nameEDITOR=r.editor_id
 f=open(nameXMLTvd,'w')
 try:
  f.write(base64.b64decode(r.ag))
 except:
  f.write('')
 #print (base64.b64decode(r.ag))
 f.close()
 f=open(nameDOC,'w')
 f.write('')
 f.close()
 APIOpenmano.parseAG(nameXMLTvd,nameScenario,nameDOC)
 try:
  delete(str(urlbase+tenant+'/scenarios/'+nameScenario))
 except:
  pass
 try:
  scenario_create(nameDOC)
  #os.remove(nameDOC)

 except:
  pass




for r in rag:
 nameScenario='RAG-'+r.ned_info+('-')+r.target_id
 nameDOC=pathTVD+nameScenario+'.yaml'
 nameXMLTvd=pathTVD+nameScenario+'.xml'
 nameNED='NED-'+r.ned_info
 nameXMLNed=pathNed+nameNED
 f=open(nameXMLTvd,'w')
 f.write(base64.b64decode(r.asg))
 f.close()
 f=open(nameDOC,'w')
 f.write('')
 f.close()
 #parseOpenmano.parseAG(nameXMLTvd,nameScenario,nameDOC)
 APIOpenmano.parseAG(nameXMLTvd,nameScenario,nameDOC)
 try:
  print str(urlbase+tenant+'/scenarios/'+nameScenario)
  delete(str(urlbase+tenant+'/scenarios/'+nameScenario))
 except:
  pass
 try:
  scenario_create(nameDOC)
  os.remove(nameDOC)
 except:
  pass
 g=open(nameXMLNed,'a')
 g.write(nameScenario+'\n')
 g.close()



ficheros = os.listdir(pathNed)
print ficheros
for element in ficheros:
 print element
 if element != 'yamls':
  #parseOpenmano.parseNed(pathNed+element,element)
  APIOpenmano.parseNed(pathNed+element,element)
  nameDOC=pathNed+ 'yamls/' +element
  #print nameDOC
  try:
   delete(str(urlbase+tenant+'/scenarios/'+element))
  except:
   pass
  try:  
   scenario_create(nameDOC+'.yaml')
  except:
   pass



