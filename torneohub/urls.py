from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('torneos.urls')),
]

handler400 = 'torneos.views.mi_error_400'
handler403 = 'torneos.views.mi_error_403'
handler404 = 'torneos.views.mi_error_404'
handler500 = 'torneos.views.mi_error_500'
