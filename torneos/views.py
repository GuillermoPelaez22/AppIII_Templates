from django.shortcuts import render
from django.db.models import Q, Prefetch, Count, Min, Max
from .models import Torneo, Equipo, Partido, Resultado, Usuario, Inscripcion


def index(request):
    return render(request, 'index.html')


# Vista: muestra todos los torneos con su deporte, su organizador y su sede (ManyToOne),
# los equipos inscritos con su capitán (ManyToMany) y los partidos del torneo
# (relación reversa) con sus equipos local y visitante (ManyToOne)
def lista_torneos(request):
    torneos = (Torneo.objects
               .select_related('deporte', 'organizador', 'sede')
               .prefetch_related('equipos__capitan',
                                 'partido_set__equipo_local',
                                 'partido_set__equipo_visitante')
               .all())
    """
    SELECT *
    FROM torneos_torneo t
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario u ON t.organizador_id = u.id
    INNER JOIN torneos_ubicacion s ON t.sede_id = s.id;

    -- prefetch_related lanza una consulta extra por cada relación:
    -- 1) equipos de los torneos (tabla intermedia torneos_inscripcion) y su capitán
    -- 2) partidos de los torneos
    -- 3) equipo local y equipo visitante de cada partido
    """
    return render(request, 'torneo/lista.html', {'torneos': torneos})


# Vista: muestra un torneo concreto con su deporte, su organizador y su sede (ManyToOne),
# sus reglas (OneToOne), los equipos inscritos con sus miembros (ManyToMany), las
# inscripciones con sus datos (tabla intermedia) y sus partidos (relación reversa)
def dame_torneo(request, id_torneo):
    torneo = (Torneo.objects
              .select_related('deporte', 'organizador', 'sede', 'reglastorneo')
              .prefetch_related('equipos__miembros',
                                'inscripcion_set__equipo',
                                'partido_set__equipo_local',
                                'partido_set__equipo_visitante')
              .get(id=id_torneo))
    """
    SELECT *
    FROM torneos_torneo t
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario u ON t.organizador_id = u.id
    INNER JOIN torneos_ubicacion s ON t.sede_id = s.id
    LEFT JOIN torneos_reglastorneo r ON r.torneo_id = t.id
    WHERE t.id = id_torneo;

    -- prefetch_related lanza una consulta extra por cada relación:
    -- 1) equipos del torneo (tabla intermedia torneos_inscripcion)
    -- 2) miembros de cada equipo (tabla intermedia torneos_equipo_miembros)
    -- 3) inscripciones del torneo (tabla intermedia) y su equipo
    -- 4) partidos del torneo
    -- 5) equipo local y equipo visitante de cada partido
    """
    return render(request, 'torneo/detalle.html', {'torneo': torneo})


# Vista: muestra los partidos jugados entre dos años, ordenados por fecha, con su torneo
# y su deporte, sus equipos local y visitante y su resultado (ManyToOne y OneToOne),
# y los miembros de cada equipo (ManyToMany)
def partidos_jugados(request, anyo_inicio, anyo_fin):
    partidos = (Partido.objects
                .select_related('torneo__deporte', 'equipo_local', 'equipo_visitante',
                                'resultado')
                .prefetch_related('equipo_local__miembros', 'equipo_visitante__miembros')
                .filter(estado='jugado',
                        fecha_hora__year__gte=anyo_inicio,
                        fecha_hora__year__lte=anyo_fin)
                .order_by('fecha_hora'))
    """
    SELECT *
    FROM torneos_partido p
    INNER JOIN torneos_torneo t ON p.torneo_id = t.id
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN torneos_equipo ev ON p.equipo_visitante_id = ev.id
    LEFT JOIN torneos_resultado r ON r.partido_id = p.id
    WHERE p.estado = 'jugado'
      AND YEAR(p.fecha_hora) >= anyo_inicio
      AND YEAR(p.fecha_hora) <= anyo_fin
    ORDER BY p.fecha_hora ASC;

    -- prefetch_related lanza una consulta extra por cada relación:
    -- 1) miembros del equipo local (tabla intermedia torneos_equipo_miembros)
    -- 2) miembros del equipo visitante (tabla intermedia torneos_equipo_miembros)
    """
    return render(request, 'partido/jugados.html',
                  {'partidos': partidos, 'anyo_inicio': anyo_inicio,
                   'anyo_fin': anyo_fin})


# Vista: muestra los torneos cuyo nombre o descripción contienen un texto, ordenados
# del más nuevo al más antiguo, con su deporte y su organizador (ManyToOne), los equipos
# inscritos con su capitán (ManyToMany) y las inscripciones (tabla intermedia)
def buscar_torneos(request, texto):
    torneos = (Torneo.objects
               .select_related('deporte', 'organizador')
               .prefetch_related('equipos__capitan', 'inscripcion_set__equipo')
               .filter(Q(nombre__contains=texto) | Q(descripcion__contains=texto))
               .order_by('-fecha_inicio'))
    """
    SELECT *
    FROM torneos_torneo t
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario u ON t.organizador_id = u.id
    WHERE t.nombre LIKE '%texto%'
       OR t.descripcion LIKE '%texto%'
    ORDER BY t.fecha_inicio DESC;

    -- prefetch_related lanza una consulta extra por cada relación:
    -- 1) equipos del torneo (tabla intermedia torneos_inscripcion) y su capitán
    -- 2) inscripciones del torneo (tabla intermedia) y su equipo
    """
    return render(request, 'torneo/buscar.html', {'torneos': torneos, 'texto': texto})


# Vista: muestra el último resultado registrado en cualquier partido de un torneo,
# con el partido, el torneo y su deporte (ManyToOne), los equipos local y visitante
# y el perfil del capitán de cada uno (OneToOne)
def ultimo_resultado(request, id_torneo):
    resultados = (Resultado.objects
                  .select_related('partido__torneo__deporte',
                                  'partido__equipo_local__capitan__perfilusuario',
                                  'partido__equipo_visitante__capitan__perfilusuario')
                  .filter(partido__torneo=id_torneo)
                  .order_by('-partido__fecha_hora')[:1])
    """
    SELECT *
    FROM torneos_resultado r
    INNER JOIN torneos_partido p ON r.partido_id = p.id
    INNER JOIN torneos_torneo t ON p.torneo_id = t.id
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN torneos_usuario cl ON el.capitan_id = cl.id
    LEFT JOIN torneos_perfilusuario pl ON pl.usuario_id = cl.id
    INNER JOIN torneos_equipo ev ON p.equipo_visitante_id = ev.id
    INNER JOIN torneos_usuario cv ON ev.capitan_id = cv.id
    LEFT JOIN torneos_perfilusuario pv ON pv.usuario_id = cv.id
    WHERE p.torneo_id = id_torneo
    ORDER BY p.fecha_hora DESC
    LIMIT 1;
    """
    return render(request, 'resultado/ultimo.html',
                  {'resultados': resultados, 'id_torneo': id_torneo})


# Vista: muestra los usuarios que no pertenecen a ningún equipo (tabla intermedia
# automática vacía), con su perfil (OneToOne) y los equipos que capitanean y los
# torneos que organizan (relación reversa)
def usuarios_sin_equipo(request):
    usuarios = (Usuario.objects
                .select_related('perfilusuario')
                .prefetch_related('equipos_capitaneados', 'torneos_organizados')
                .filter(equipos=None))
    """
    SELECT *
    FROM torneos_usuario u
    LEFT JOIN torneos_perfilusuario pu ON pu.usuario_id = u.id
    LEFT JOIN torneos_equipo_miembros em ON em.usuario_id = u.id
    WHERE em.id IS NULL;

    -- prefetch_related lanza una consulta extra por cada relación reversa:
    -- 1) equipos capitaneados por el usuario
    -- 2) torneos organizados por el usuario
    """
    return render(request, 'usuario/sin_equipo.html', {'usuarios': usuarios})


# Vista: muestra la ficha de un usuario con su perfil (OneToOne), los torneos que
# organiza (relación reversa), los equipos que capitanea (relación reversa) y los
# equipos de los que es miembro (ManyToMany)
def ficha_usuario(request, id_usuario):
    usuario = (Usuario.objects
               .select_related('perfilusuario')
               .prefetch_related('equipos_capitaneados',
                                 Prefetch('torneos_organizados',
                                          queryset=Torneo.objects
                                          .select_related('deporte', 'sede')
                                          .order_by('-fecha_inicio')),
                                 Prefetch('equipos',
                                          queryset=Equipo.objects
                                          .select_related('capitan')
                                          .order_by('-fecha_creacion')))
               .get(id=id_usuario))
    """
    SELECT *
    FROM torneos_usuario u
    LEFT JOIN torneos_perfilusuario pu ON pu.usuario_id = u.id
    WHERE u.id = id_usuario;

    -- prefetch_related lanza una consulta extra por cada relación:
    -- 1) equipos capitaneados por el usuario
    -- 2) torneos organizados por el usuario con su deporte y su sede,
    --    ordenados por fecha de inicio descendente:
    SELECT *
    FROM torneos_torneo t
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_ubicacion s ON t.sede_id = s.id
    WHERE t.organizador_id = id_usuario
    ORDER BY t.fecha_inicio DESC;
    -- 3) equipos de los que es miembro (tabla intermedia torneos_equipo_miembros)
    --    con su capitán, ordenados por fecha de creación descendente:
    SELECT *
    FROM torneos_equipo e
    INNER JOIN torneos_equipo_miembros em ON em.equipo_id = e.id
    INNER JOIN torneos_usuario c ON e.capitan_id = c.id
    WHERE em.usuario_id = id_usuario
    ORDER BY e.fecha_creacion DESC;
    """
    return render(request, 'usuario/ficha.html', {'usuario': usuario})


# Vista: muestra las estadísticas de un torneo usando aggregate (número de partidos,
# fecha del primero y del último, número de resultados y número de inscripciones con
# la fecha de la primera y la última), junto con los datos del torneo, su deporte,
# su organizador y su sede (ManyToOne) y sus inscripciones con su equipo (tabla intermedia)
def estadisticas_torneo(request, id_torneo):
    torneo = (Torneo.objects
              .select_related('deporte', 'organizador', 'sede')
              .prefetch_related('inscripcion_set__equipo')
              .get(id=id_torneo))
    """
    SELECT *
    FROM torneos_torneo t
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario u ON t.organizador_id = u.id
    INNER JOIN torneos_ubicacion s ON t.sede_id = s.id
    WHERE t.id = id_torneo;
    -- más una consulta extra por la relación del prefetch_related
    -- (inscripciones de la tabla intermedia y su equipo)
    """

    estadisticas_partidos = (Partido.objects
                             .filter(torneo=id_torneo)
                             .aggregate(total=Count('id'),
                                        primero=Min('fecha_hora'),
                                        ultimo=Max('fecha_hora')))
    """
    SELECT COUNT(id), MIN(fecha_hora), MAX(fecha_hora)
    FROM torneos_partido
    WHERE torneo_id = id_torneo;
    """

    estadisticas_resultados = (Resultado.objects
                               .filter(partido__torneo=id_torneo)
                               .aggregate(total=Count('id')))
    """
    SELECT COUNT(r.id)
    FROM torneos_resultado r
    INNER JOIN torneos_partido p ON r.partido_id = p.id
    WHERE p.torneo_id = id_torneo;
    """

    estadisticas_inscripciones = (Inscripcion.objects
                                  .filter(torneo=id_torneo)
                                  .aggregate(total=Count('id'),
                                             primera=Min('fecha_inscripcion'),
                                             ultima=Max('fecha_inscripcion')))
    """
    SELECT COUNT(id), MIN(fecha_inscripcion), MAX(fecha_inscripcion)
    FROM torneos_inscripcion
    WHERE torneo_id = id_torneo;
    """

    return render(request, 'torneo/estadisticas.html',
                  {'torneo': torneo,
                   'estadisticas_partidos': estadisticas_partidos,
                   'estadisticas_resultados': estadisticas_resultados,
                   'estadisticas_inscripciones': estadisticas_inscripciones})


# Vista: muestra las inscripciones (tabla intermedia) cuyas observaciones contienen un
# texto, de la más reciente a la más antigua, con el equipo y el perfil de su capitán
# (OneToOne), el torneo con su deporte y su organizador (ManyToOne) y los miembros
# del equipo (ManyToMany)
def inscripciones_observaciones(request, texto):
    inscripciones = (Inscripcion.objects
                     .select_related('equipo__capitan__perfilusuario',
                                     'torneo__deporte', 'torneo__organizador')
                     .prefetch_related('equipo__miembros')
                     .filter(observaciones__contains=texto)
                     .order_by('-fecha_inscripcion'))
    """
    SELECT *
    FROM torneos_inscripcion i
    INNER JOIN torneos_equipo e ON i.equipo_id = e.id
    INNER JOIN torneos_usuario c ON e.capitan_id = c.id
    LEFT JOIN torneos_perfilusuario pc ON pc.usuario_id = c.id
    INNER JOIN torneos_torneo t ON i.torneo_id = t.id
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario o ON t.organizador_id = o.id
    WHERE i.observaciones LIKE '%texto%'
    ORDER BY i.fecha_inscripcion DESC;

    -- prefetch_related lanza una consulta extra para los miembros de los equipos
    -- (tabla intermedia torneos_equipo_miembros)
    """
    return render(request, 'inscripcion/observaciones.html',
                  {'inscripciones': inscripciones, 'texto': texto})


# Vista: muestra los 5 últimos partidos de un equipo (como local o como visitante),
# ordenados del más reciente al más antiguo, con el capitán del equipo y su perfil
# (OneToOne), el torneo con su deporte y su organizador, los dos equipos y el resultado
# (ManyToOne y OneToOne) y los equipos inscritos en el torneo (ManyToMany)
def ultimos_partidos_equipo(request, id_equipo):
    equipo = (Equipo.objects
              .select_related('capitan__perfilusuario')
              .get(id=id_equipo))
    """
    SELECT *
    FROM torneos_equipo e
    INNER JOIN torneos_usuario c ON e.capitan_id = c.id
    LEFT JOIN torneos_perfilusuario pc ON pc.usuario_id = c.id
    WHERE e.id = id_equipo;
    """

    partidos = (Partido.objects
                .select_related('torneo__deporte', 'torneo__organizador',
                                'equipo_local', 'equipo_visitante', 'resultado')
                .prefetch_related('torneo__equipos')
                .filter(Q(equipo_local=id_equipo) | Q(equipo_visitante=id_equipo))
                .order_by('-fecha_hora')[:5])
    """
    SELECT *
    FROM torneos_partido p
    INNER JOIN torneos_torneo t ON p.torneo_id = t.id
    INNER JOIN torneos_deporte d ON t.deporte_id = d.id
    INNER JOIN torneos_usuario o ON t.organizador_id = o.id
    INNER JOIN torneos_equipo el ON p.equipo_local_id = el.id
    INNER JOIN torneos_equipo ev ON p.equipo_visitante_id = ev.id
    LEFT JOIN torneos_resultado r ON r.partido_id = p.id
    WHERE p.equipo_local_id = id_equipo
       OR p.equipo_visitante_id = id_equipo
    ORDER BY p.fecha_hora DESC
    LIMIT 5;

    -- prefetch_related lanza una consulta extra para los equipos inscritos en los
    -- torneos (tabla intermedia torneos_inscripcion)
    """
    return render(request, 'partido/ultimos_equipo.html',
                  {'equipo': equipo, 'partidos': partidos})


# Vista: página personalizada para el error 400 (petición incorrecta)
def mi_error_400(request, exception=None):
    return render(request, 'errores/400.html', status=400)


# Vista: página personalizada para el error 403 (acceso prohibido)
def mi_error_403(request, exception=None):
    return render(request, 'errores/403.html', status=403)


# Vista: página personalizada para el error 404 (página no encontrada)
def mi_error_404(request, exception=None):
    return render(request, 'errores/404.html', status=404)


# Vista: página personalizada para el error 500 (error interno del servidor)
def mi_error_500(request):
    return render(request, 'errores/500.html', status=500)
