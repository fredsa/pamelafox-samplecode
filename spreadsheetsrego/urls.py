from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^cancel', 'views.request_cancel'),
  (r'^reallycancel', 'views.cancel'),
  (r'^addevent', 'views.add_event'),
  (r'^', 'views.main_page'),
)
