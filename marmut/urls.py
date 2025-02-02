"""
URL configuration for marmut project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('auth/', include('authentication.urls')),
    path('', include('main.urls')),
    path('playlist/', include('playlist.urls')),
    path('subscription/', include('subscription.urls')),
    path('download/', include('download.urls')),
    path('podcast/', include('podcast.urls')),
    path('chart/', include('chart.urls')),
    path('album/', include('album.urls')),
    path('song/', include('song.urls')),
    path('royalti/', include('royalti.urls')),
    path('search/', include('search.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
