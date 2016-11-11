#Openmano tools:

In this directory you have some tools for interact with Openmano.

* Delete all Scenarios.

		python deleteScenario.py

* Delete all the VNFs: 

		python deleteVNF.py
**Note:** This command will allow you delete all the VNFs, **only** if you don't have any OpenMANO scenario created.

* Create a initial set of needed VNFs for graphical representation: linux, PSA and TVD 

		python createVNF.py
