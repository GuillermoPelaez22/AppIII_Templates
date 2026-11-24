# TorneoHub - Templates

## Estructura de plantillas
- `includes/menu.html`: menú de navegación superior con los enlaces de la web.
- `includes/pie.html`: pie de página.
- `principal.html`: plantilla base. Incluye el menú y el pie con `{% include %}`, tiene los blocks `cabecera` y `contenido`, y carga `static/css/estilo.css`, `static/javascript/tutorial.js` y el logotipo `static/imagenes/imagen.svg` con `{% static %}`.
- Todas las páginas heredan de `principal.html` con `{% extends %}`.
- En las plantillas de lista, el contenido del `for` está en su propia plantilla incluida con `{% include %}`: `torneo/torneo.html`, `torneo/torneo_buscado.html`, `partido/partido_jugado.html`, `partido/partido_equipo.html`, `resultado/resultado.html`, `usuario/usuario_sin_equipo.html` e `inscripcion/inscripcion.html`.

## Template tags usados
| Tag | Dónde |
|---|---|
| `if-elif-else` | `torneo/torneo.html` (cuota de inscripción), `partido/partido_jugado.html` (quién gana) |
| `for…empty` | todas las listas, por ejemplo `torneo/lista.html` |
| `with` | `torneo/torneo.html`, `partido/partido_jugado.html` |
| `cycle` | `torneo/torneo.html`, `partido/partido_jugado.html`, `usuario/usuario_sin_equipo.html` |
| `firstof` | `torneo/torneo.html` (descripción) |
| `include` | `principal.html` y las plantillas de lista |
| `now` | `includes/pie.html` |
| `url` | `includes/menu.html` e `index.html` |

## Operadores usados en los if
| Operador | Dónde |
|---|---|
| `==` | `torneo/torneo.html` (cuota == 0), `inscripcion/inscripcion.html` |
| `!=` | `inscripcion/inscripcion.html` (observaciones != '') |
| `>` | `torneo/torneo.html` (total > 0), `partido/partido_jugado.html` |
| `>=` | `torneo/torneo.html` (cuota alta, torneo completo) |
| `<` | `partido/partido_jugado.html` (gana el visitante) |
| `and` | `torneo/torneo.html`, `partido/partido_jugado.html`, `usuario/usuario_sin_equipo.html` |
| `or` | `inscripcion/inscripcion.html` |
| `not` | `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `in` | `torneo/torneo.html` ('copa' in nombre) |

## Template filters usados
| Filtro | Dónde |
|---|---|
| `date` | fechas de todas las plantillas (`d/m/Y`, `d/m/Y H:i` y `j \d\e F \d\e Y`) |
| `time` | `partido/partido_jugado.html` |
| `upper` | `torneo/torneo.html` |
| `lower` | `torneo/torneo.html`, `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `title` | `torneo/torneo.html`, `usuario/usuario_sin_equipo.html` |
| `capfirst` | `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `length` | `torneo/torneo.html`, `partido/partido_jugado.html` |
| `pluralize` | `torneo/torneo.html`, `partido/partido_jugado.html` |
| `default` | `torneo/torneo.html`, `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `truncatechars` | `partido/partido_jugado.html`, `inscripcion/inscripcion.html` |
| `join` | `inscripcion/inscripcion.html` |
| `cut` | `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `linebreaksbr` | `usuario/usuario_sin_equipo.html` |
| `yesno` | `usuario/usuario_sin_equipo.html`, `inscripcion/inscripcion.html` |
| `floatformat` | `torneo/torneo.html`, `usuario/usuario_sin_equipo.html` |

## Formato de fechas
Se usa `date` con `d/m/Y` para fechas, `d/m/Y H:i` para fecha y hora, y `j \d\e F \d\e Y` (por ejemplo, "15 de marzo de 2026") en la lista de torneos. En `settings.py`: `LANGUAGE_CODE = 'es'` y `TIME_ZONE = 'Europe/Madrid'`.
