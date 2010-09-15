from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^importer/', include('importer.urls')),
)
