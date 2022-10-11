
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': "portfolio",
        'USER': "portfolio1",
        'PASSWORD': "portfolio",
        'HOST': 'localhost',
        'PORT': '5433'
    }
}
DEBUG = True
