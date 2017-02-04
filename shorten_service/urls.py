from django.conf.urls import url 
 
from . import views 

app_name = 'shorten_service' 
urlpatterns = [ 
     # ex: /shorten/
     url(r'^$', views.index, name='index'),
     # ex: /shorten/manage/<short_url>
     url(r'^manage/(?P<short_url>[a-zA-Z0-9\_\-^aiueoAIUEOl10]{7})/$', views.manage_url, name='manage_url'),
     # ex: /shorten/<short_url> -- redirect to long url
     url(r'^(?P<short_url>[a-zA-Z0-9\_\-^aiueoAIUEOl10]{7})/$', views.redirect_url, name='redirect_url'),
     # ajax validate
     url(r'^ajax/validate_url/$', views.validate_url, name='validate_url'),

     # ajax encode 
     url(r'^ajax/encode_url/$', views.encode_url, name='encode_url'),
]
