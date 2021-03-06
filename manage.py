#!/usr/bin/env python
import os
import sys

version='1.2'

if __name__ == "__main__":
    if sys.argv[1]=="runserver":
	import logging
	from ConfigParser import SafeConfigParser
        parser = SafeConfigParser()
        parser.read('upr.conf')
        logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))
	logging.info('Running UPR with version %s',version)



    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "upr.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
