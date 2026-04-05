from django.contrib import admin
from django.urls import path, include, re_path # re_path add kiya
from django.conf import settings
from django.views.static import serve # serve add kiya

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# 👇 YEH NAYA CODE ADD KARNA HAI 👇
# Yeh Django ko force karega ki Live server par bhi Media (PDF) files dikhaye
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
