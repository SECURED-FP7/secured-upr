#!/usr/bin/python

import json
import upr_client
client=upr_client.UPRClient('http://10.95.211.18:8081')
user='ned'
r=client.delete_user(user_id=user)
if r.status_code == 204:
	print "Successfully Deleted"
else:
	print "Error:"+str(r.status_code)
	
