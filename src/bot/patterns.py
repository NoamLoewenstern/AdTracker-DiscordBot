import re

LIST_CAMPAIGNS = re.compile(r'^/(?P<platform>\w+?) camps$', re.IGNORECASE)
