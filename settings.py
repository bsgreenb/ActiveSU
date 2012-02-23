from settings_local import *

import platform

comp_name = platform.node()
if comp_name == 'textyard.com': #our production cloud site server's name
    from settings_production import *
else:
    from settings_development import *
