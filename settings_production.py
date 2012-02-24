DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'NAME': 'activity', #or path to db file if using sqlite3
        'USER': 'activity', #not used with sqlite3
        'PASSWORD': 'Mopyard1', #not used with sqlite3
        'HOST': '', #empty string makes it localhost
        'PORT': '', #empty string makes it default
    }
}

