from django.conf import settings
 
def config_settings(request):
    return {
        'site_name' : settings.SITE_NAME,
    }