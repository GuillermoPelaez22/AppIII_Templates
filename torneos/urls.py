from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('torneos/', views.lista_torneos, name='lista_torneos'),
    path('torneo/<int:id_torneo>/', views.dame_torneo, name='dame_torneo'),
    path('partidos/jugados/<int:anyo_inicio>/<int:anyo_fin>/', views.partidos_jugados, name='partidos_jugados'),
    path('torneos/buscar/<str:texto>/', views.buscar_torneos, name='buscar_torneos'),
    path('torneo/<int:id_torneo>/ultimo-resultado/', views.ultimo_resultado, name='ultimo_resultado'),
    re_path(r'^usuarios/sin-equipo/$', views.usuarios_sin_equipo, name='usuarios_sin_equipo'),
    path('usuario/<int:id_usuario>/', views.ficha_usuario, name='ficha_usuario'),
    path('torneo/<int:id_torneo>/estadisticas/', views.estadisticas_torneo, name='estadisticas_torneo'),
    path('inscripciones/observaciones/<str:texto>/', views.inscripciones_observaciones, name='inscripciones_observaciones'),
    path('equipo/<int:id_equipo>/partidos/', views.ultimos_partidos_equipo, name='ultimos_partidos_equipo'),
    path('error/400/', views.mi_error_400, name='error_400'),
    path('error/403/', views.mi_error_403, name='error_403'),
    path('error/500/', views.mi_error_500, name='error_500'),
]
