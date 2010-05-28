from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'testproject.testapp.views.index'),
    (r'^_wave/*', 'testproject.testbot.wave.OnWaveAnything')
)
