Client to be used in other components

*Dependencies*

Install requests

	pip install requests

*Usage*

First copy upr_client.py  where you need it, import upr_client in your file and create an UPRClient object

	import upr_client
	client=upr_client.UPRClient('http://UPR_IP:UPR_PORT')

Now you can use the methods of he class

	response=client.get_user_list()
	creator=client.get_user_creator(user_id='alice')
	...
