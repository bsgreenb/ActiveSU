<<<<<<< HEAD
def get_site_name(request):
    return {
        'site_name' : 'ActiveSU'
    }
=======
from django.conf import settings

def get_site_name(request):
    return {
        'site_name' : settings.SITE_NAME
    }

if __name__ == '__main__':
    print settings.SITE_NAME
<<<<<<< HEAD
>>>>>>> a02d13173ff0014c5b7f1c2e134ab3d871d0dc5b
=======
>>>>>>> a02d13173ff0014c5b7f1c2e134ab3d871d0dc5b
