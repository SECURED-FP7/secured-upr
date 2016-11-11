
import argparse
import requests
from ConfigParser import SafeConfigParser
from requests import post, delete

parser = SafeConfigParser()
parser.read('upr.conf')
tenant=parser.get('mano','tenant')
remoteIp=parser.get('mano','ipMano')
remotePort=parser.get('mano','portMano')

pathScenario=parser.get('mano','pathScenario')

urlbase='http://'+remoteIp+':'+remotePort+'/openmano/'
pathYaml=pathScenario+'/TVD/'
pathNed= pathScenario+'/NED/'




def _print_verbose(mano_response, verbose_level=0):
    content = mano_response.json()
    result = 0 if mano_response.status_code==200 else mano_response.status_code
    if type(content)!=dict or len(content)!=1:
        #print "Non expected format output"
        #print str(content)
        return result

    val=content.values()[0]
    if type(val)==str:
        #print val
        return result
    elif type(val) == list:
        content_list = val
    elif type(val)==dict:
        content_list = [val]
    else:
        #print "Non expected dict/list format output"
        #print str(content)
        return result

    #print content_list
    if verbose_level==None:
        verbose_level=0
    if verbose_level >= 3:
        print yaml.safe_dump(content, indent=4, default_flow_style=False)
        return result
    id=''
    if mano_response.status_code == 200:
        for content in content_list:
            myoutput = "%s %s" %(content['uuid'].ljust(38),content['name'].ljust(20))
            id= content['uuid'].ljust(38)

            if verbose_level >=1:
                myoutput += " " + content['created_at'].ljust(20)
                if verbose_level >=2:
                    new_line='\n'
                    if 'type' in content and content['type']!=None:
                        myoutput += new_line + "  Type: " + content['type'].ljust(29)
                        new_line=''
                    if 'type' in content and content['type']!=None:
                        myoutput += new_line + "  Type: " + content['type'].ljust(29)
                        new_line=''
                    if 'description' in content and content['description']!=None:
                        myoutput += new_line + "  Description: " + content['description'].ljust(20)
            print myoutput
    else:
        print content['error']['description']
    #return id
    return result


def scenario_create(scenario): 
	d=(open(scenario,'rb'))
	dataset=d.read()
	d.close()
	#print dataset
	headers_req = {'content-type': 'application/yaml'}
	URLrequest = "http://%s:%s/openmano/%s/scenarios" %(remoteIp, remotePort, tenant)
	mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
	r = _print_verbose(mano_response)
	#print r
	return r







def parseAG(nameXML, nameScenario, nameDoc=None):
	import os
	from requests import get

	if nameDoc is None:
		nameDoc = nameScenario+'.yaml'
	from xml.dom import minidom
	try:
		ag = minidom.parse(nameXML)
		PSAlist = ag.getElementsByTagName('PSA')
	except:
		print 'format error xml'
		return

	string1="""description:     Complex network scenario consisting of """
	string1b=""" PSAS connected
topology: 
  nodes: 
    PC:                  # vnf/net name in the scenario
      graph:
         x: 0
         y: 142 
      type:      VNF          # VNF, network, external_network (if it is a datacenter network)
      VNF model: linux        # VNF name as introduced in OPENMANO DB
    MOVIL:                  # vnf/net name in the scenario
      graph:
         x: 120
         y: 142
      type:      VNF          # VNF, network, external_network (if it is a datacenter network)
      VNF model: linux        # VNF name as introduced in OPENMANO DB
"""   
		
	modelVFN2="""
      type:      VNF
      VNF model: """
	string2="""
    bridge1:
      graph:
         x: 217
         y: 264
      type:      network
      model:     bridge_net
    default: 
      graph:
         x: 16
         y: 464
      type:      external_network # Datacenter net
      model:     default

  connections: 
"""


	tam=len(PSAlist)
	f=open(nameDoc,'a')
	f.write('\n---\nname:            '+nameScenario+'\n')
	f.write(string1+str(tam)+string1b)
	lim=500
	lim1=lim/tam
	vy=lim1/2
	vx=570

	for s in PSAlist:
		nombre1=s.attributes['name'].value
		f.write('    '+nombre1+':\n')
                f.write('      graph:\n')
                f.write('        x: '+str(vx)+'\n')
                f.write('        y: '+str(vy))
		f.write(modelVFN2)
		
		print urlbase+tenant+'/vnfs/'+str(nombre1)
		r=get (urlbase+tenant+'/vnfs/'+str(nombre1))
		print r
		t='<Response [200]>'
		if str(r) == t:
			f.write(nombre1+'\n')
		else: 
			f.write ('PSA \n')
                vy=vy+lim1


		


	f.write(string2)
	a=len(PSAlist)
	for i in range(1, a):
		f.write('    dataconn'+str(i)+':\n      nodes: \n      -   '+PSAlist[i-1].attributes['name'].value+': xe1\n      -   '+PSAlist[i].attributes['name'].value+': xe0\n')





	f.write('    bridgeconn1:\n      nodes: \n      -   bridge1: null\n      -   PC:  eth0\n      -   MOVIL: eth0\n      -   '+PSAlist[0].attributes['name'].value+':  xe0\n    ')
	b=a-1
	f.write('mngmt-net:\n      nodes: \n      -   default: null\n      -   '+PSAlist[b].attributes['name'].value+':  xe1\n')
	f.close()
	os.remove(nameXML)
	return




def parseNed(nameXML, nameScenario, nameDOC=None):
	import os
	from requests import delete

	if nameDOC is None:
		nameDOC = pathNed+'yamls/'+nameScenario+'.yaml'
	f=open(nameXML, 'r')
	g=f.read()
	f.close()
	G=g.split('\n')
	tam=len(G)
	if tam==1:
		try:
			delete (str(urlbase+tenant+'/scenarios/'+nameScenario))
		except:
			pass
		try:
			os.remove(nameXML)
		except:
			pass

		return
	else:
		pass	


	string1="""description:     Complex network scenario consisting of """
	string1b=""" TVD connected
topology:
  nodes:
    PC:                  # vnf/net name in the scenario
      graph:
        x: 1
        y: 294
      type:      VNF          # VNF, network, external_network (if it is a$
      VNF model: linux        # VNF name as introduced in OPENMANO DB
    """

	string2="""
    bridge_net:
      graph:
        x: 166
        y: 323
      type:      network
      model:     bridge_net
    default:
      graph:
         x: 16
         y: 464
      type:      external_network # Datacenter net
      model:     default

  connections:
"""
	modelTVD="""
      type:      VNF
      VNF model: TVD
    """

	f=open(nameDOC,'w')
	f.write('')
	f.close()

	f=open(nameDOC,'a')
	f.write('\n---\nname:            '+nameScenario+'\n')
	f.write(string1+str(tam-1)+string1b)
	lim=700
	lim1=lim/tam
	vy=lim1/2
	vx=550
	for i in range(1, tam):
		f.write(G[i-1]+':\n')
		f.write('      graph:\n')
		f.write('        x: '+str(vx)+'\n')
		f.write('        y: '+str(vy))
		f.write(modelTVD)
		vy=vy+lim1


	a=0
	f.write(string2)
	for i in range(1, tam):
		f.write('    connection '+str(a)+':\n      type: link \n '+'     nodes: \n      - '+G[i-1]+': xe0\n      - '+'bridge_net: "0"\n')
		a=a+1
		f.write('    connection '+str(a)+':\n      type : link \n '+'     nodes: \n      - '+G[i-1]+': xe1\n      - '+'bridge_net: "0"\n')
		a=a+1


	f.write('    connection '+str(a)+':\n      type : link \n '+'     nodes: \n      - PC: eth0\n      - '+'bridge_net: "0"\n')

	return

