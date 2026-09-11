OJO: La original esta en la otra rama

# Parte 1 — Diagnóstico

## 1.1 Los cuatro defectos. Para cada uno: qué está mal, en qué archivo y en qué líneas se manifiesta, y qué consecuencia tiene. Un defecto no es "falta una línea": es qué garantía se pierde por no tenerla.

### Defecto 1:
- Descripción: La instalación usa `pip install -r requirements.txt`, y ese archivo declara versiones abiertas como `requests>=2.31` la cual no es una version fijada. Aunque existe `requirements.lock` en el repositorio, el workflow nunca lo usa.
- Archivo: `.github/workflows/pipeline.yml`, pasos "Instalar dependencias" (es igual en el job `validar` y en `publicar`).
- Consecuencia: Se pierde reproducibilidad porque dos ejecuciones del mismo commit pueden instalar versiones distintas de las dependencias transitivas, así que si funcionó en una corrida no garantiza que funcione en la siguiente.

### Defecto 2:
- Descripción: No hay ningún mecanismo de caché para las dependencias. Cada corrida vuelve a descargar e instalar todo desde cero.
- Archivo: `.github/workflows/pipeline.yml`, pasos "Preparar Python" (ambos jobs)
- Consecuencia: Se pierde velocidad de feedback: cada ejecución paga el costo completo de descarga/instalación, inflando la duración del pipeline sin necesidad.

### Defecto 3:
- Descripción: El job `publicar` no depende del job `validar`, y el paso de análisis de SonarCloud no verifica el resultado del quality gate.
- Archivo: `.github/workflows/pipeline.yml`, job `publicar` y paso "Analisis de calidad" del job `validar` | 
- Consecuencia: Se pierde la garantía de calidad: aunque el análisis de SonarCloud falle o el código no cumpla el quality gate, el job `publicar` corre de todas formas porque no espera a `validar` ni revisa su resultado.

### Defecto 4:
- Descripción: El artefacto se publica siempre con el nombre fijo `paquete` sin versión, y la condición `if` no restringe la rama, por lo que cualquier push a cualquier rama dispara la publicación. | 
- Archivo: `.github/workflows/pipeline.yml`, job `publicar`: la condición `if:` y el paso "Publicar el paquete" (`name: paquete`)
- Consecuencia: Se pierde trazabilidad y control: no se puede saber qué versión del código corresponde a qué artefacto descargado, y se pueden publicar artefactos desde ramas de feature sin pasar por `main` ni por revisión.

## 1.2 El defecto que explica la duración. De los cuatro, cuál explica el tiempo que registraron en docs/linea-base.md. Sustenten con el número que midieron.

El defecto 2 (ausencia de caché) es el que explica el tiempo registrado en `docs/linea-base.md`, donde mis tres ejecuciones dieron **1m 4s, 1m 3s y 1m 6s** que son prácticamente el mismo tiempo en las tres corridas. Eso es justamente la firma de un pipeline sin caché: si hubiera caché de dependencias, la segunda y tercera corrida deberían ser notablemente más rápidas que la primera que llena la caché. Como no bajó, se sostiene que cada corrida reinstala todo desde cero.

## 1.3 El vínculo con su caso. Cuál de los cuatro defectos ataca la restricción del caso transversal de su grupo. Citen un dato del value stream map que levantaron en la Sesión 1.

Para el Caso 3, Seguros Pacífico Sur, el defecto vinculado es que el pipeline no se detenga si falla el análisis de calidad. La restricción del caso no es una espera visible sino retrabajo constante por defectos no atrapados a tiempo, sustentado en que el rendimiento acumulado de calidad es de apenas 11% y que 76 de 94 historias fueron devueltas al menos una vez. Un quality gate que no bloquea nada reproduce ese mismo patrón.

## 1.4 La métrica DORA. Qué métrica DORA esperan mover con la intervención y por qué. Solo dos son alcanzables sin despliegue: identifiquen cuáles y elijan una.

Sin llegar a desplegar a producción, las únicas dos métricas DORA que se puede mover con esta intervención son el tiempo de entrega del cambio y el porcentaje de fallas en el cambio; la frecuencia de despliegue y el tiempo de restauración del servicio requieren un despliegue real. Elijo el tiempo de entrega del cambio porque la corrección del defecto de caché tiene un efecto medible y directo sobre la duración del pipeline.

## 1.5 El proxy. Qué número concreto van a medir para sustentar que la métrica se movió. Decláralo antes de intervenir. Hagan commit de este archivo antes de tocar el workflow. La marca de tiempo del commit es parte de la evidencia.

El número concreto que se va a medir es la duración total del job validar en GitHub Actions. La línea base es un promedio de aproximadamente 1 minuto 4 segundos sobre las tres ejecuciones registradas antes de intervenir el workflow. Ese valor queda declarado como punto de comparación antes de aplicar la corrección del defecto de caché.

# Parte 2 — Intervención
HECHO

# Parte 3 — Inyección de falla
HECHO

# Parte 4 — Cierre

## 4.1 Medición posterior

Tras aplicar la corrección de caché, se ejecutó el workflow tres veces en main sin modificar archivos, siguiendo el mismo procedimiento de la línea base. El job validar registró 56s, 1m2s y 54s, con un promedio de 57.3 segundos, frente al promedio base de 58.3 segundos (57s, 58s y 1m) medido antes de intervenir el pipeline.

### Linea base de ejecucion
| Ejecucion | Duracion (jov, validar) | URL |
|---|---|---|
| 1 | 57s | [https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34502985174](https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34502985174/job/102958102670) |
| 2 | 58s | [https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34503224087](https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34503224087/job/102958883101) |
| 3 | 1m | [https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34503345649/job/102959281585](https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34503345649/job/102959281585) |

### Medición posterior
| Ejecucion | Duracion (jov, validar) | URL |
|---|---|---|
| 1 | 56s | https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34558497545/job/103136173043 |
| 2 | 1m 2s | https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34558593620/job/103136456415 |
| 3 | 54s | https://github.com/darkJCdark/INF384-lab2-20206234/actions/runs/34558612120/job/103136515176 |

La diferencia es de apenas un segundo, alrededor de 1.7%, una variación que no permite concluir una mejora real y que se explica mejor como ruido normal entre ejecuciones del mismo pipeline. Esto no invalida la corrección: agregar caché de pip y fijar las dependencias con requirements.lock sigue siendo necesario para la reproducibilidad, que era el problema de fondo señalado en el defecto 2. Lo que muestran los números es que, en un proyecto de este tamaño, la instalación de dependencias no es el paso que más pesa dentro del job validar; el análisis de SonarCloud y la ejecución de pruebas ocupan la mayor parte del tiempo y no se ven afectados por la caché. El proxy elegido sigue siendo el correcto para sustentar la métrica DORA declarada, aunque el efecto medido en la duración sea marginal.

## 4.2 Justificación de la versión

Se declaró la versión 1.2.1 en VERSION y pyproject.toml, como incremento de parche sobre 1.2.0. La sustentan los commits registrados desde ese tag: todos con prefijo fix: (corrección del pipeline, corrección de validaciones y de tarifas), sin ningún feat que agregue funcionalidad nueva ni cambios incompatibles. Según Conventional Commits, una serie de correcciones sin nuevas funcionalidades corresponde a un incremento de parche, no de versión menor o mayor.

## 4.3 Lo que no se resolvió

El pipeline no verifica que la versión declarada en VERSION/pyproject.toml corresponda realmente al tipo de cambios del historial. Nada impide que alguien olvide bumpear la versión, o que la suba como parche cuando en realidad el commit incluye un feat:, y el pipeline la publicaría igual sin detectar la inconsistencia. Para resolverlo, haría falta un paso adicional que calcule automáticamente la versión esperada a partir de los mensajes de commit desde el último tag y falle el job si el valor declarado en VERSION no coincide con el calculado.

## 4.4 Declaración de uso de IA generativa, conforme al sílabo.

### A. Partes del laboratorio donde se usó:

- Diagnóstico de los cuatro defectos del pipeline (Parte 1). Se empleó la IA para identificar rápidamente los errores presentes en .github/workflows/pipeline.yml a partir de su lectura completa, contrastándolos contra las cuatro condiciones exigidas en el enunciado. A partir de ese diagnóstico inicial, se contextualizó y ajustó la solución con los conocimientos propios adquiridos en clase, para vincular los defectos con el caso transversal asignado y con las métricas DORA revisadas en la Sesión 1.

- Diseño de la función sin cobertura de la Parte 3. Se generó con IA la función calcular_descuento_por_volumen, de más de 15 líneas y con lógica condicional real, agregada a src/despachos/pedidos.py para provocar deliberadamente la caída de cobertura sobre código nuevo y así verificar que el quality gate detiene el pipeline.

### B. Propósito:

Acelerar el análisis del workflow existente, apoyar la redacción de docs/diagnostico.md y la corrección del pipeline en la Parte 2, y generar el código de prueba de la Parte 3.

### C. Verificación:

Todos los cambios sugeridos fueron revisados, aplicados y probados manualmente en el propio fork, incluyendo la ejecución del pipeline para confirmar que las correcciones funcionan y que la falla inyectada efectivamente detiene el análisis de calidad.
