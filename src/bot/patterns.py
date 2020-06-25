import re

LIST_CAMPAIGNS = re.compile(r'^/(?P<platform>\w+?) camps$', re.IGNORECASE)
OUTPUT_FORMAT = re.compile(r'/output:(?P<output_format>\w+)', re.IGNORECASE)
