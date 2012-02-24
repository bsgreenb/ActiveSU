from django.conf import settings

def get_site_name(request):
    return {
        'site_name' : settings.SITE_NAME
    }

if __name__ == '__main__':
    print settings.SITE_NAME
