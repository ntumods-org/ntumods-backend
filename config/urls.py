"""
URL configuration for ntumods project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title='NTUMODS BACKEND API',
        default_version='1.0.0',
        description='''
            Swagger auto-generated documentation for NTUMods Backend API.
            Easily try all the API endpoints here.
        '''
    ), public=True
)

urlpatterns = [
    # swagger documentation
    path('', schema_view.with_ui('swagger'), name='swagger'),
    # django admin page
    path('admin/', admin.site.urls),

    # other apps
    path('courses/', include('apps.courses.urls')),
    path('optimizer/', include('apps.optimizer.urls')),
    path('scraper/', include('apps.scraper.urls')),
]
