#!/usr/bin/python

import json
import upr_client
client=upr_client.UPRClient('http://10.95.211.18:8081')
first_user='first_user'
first_pass='password'
first_integrity_level=2
first_is_cooperative=False
first_type='normal'
first_is_infrastructure=False
first_is_admin=False
first_opt="MIN_TRANFER_COSTMIN_LATENCY"
#r=client.get_user_creator(user_id=first_user, password=first_pass, integrityLevel=first_integrity_level, type=first_type, is_cooperative=first_is_cooperative, is_infrastructure=first_is_infrastructure, is_admin=first_is_admin)
r=client.create_user(user_id=first_user,password=first_pass, integrityLevel=first_integrity_level, type=first_type, is_cooperative=first_is_cooperative, is_infrastructure=first_is_infrastructure, is_admin=True,creator=None,optimization_profile=first_opt)
data=json.loads(r.text)
print data
