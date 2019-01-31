from django.conf.urls import url
from analysis.views import (
    test, update_local_to_server,
)
#     analysis, test, update_local_to_server,

urlpatterns = [
    url(r'^test/', test),
    url(r'^update/', update_local_to_server),
]
