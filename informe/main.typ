
#import "@preview/basic-report:0.4.0": *
#import "@preview/dashy-todo:0.1.3": todo
#import "@preview/subpar:0.2.2"

#let todo-inline = todo.with(position:"inline")
#let missing-fig = rect.with(fill: tiling(" missing figure "), width: 100%, height: 3in, stroke: stroke(paint: red, thickness: 7pt))

#show: it => basic-report(
  doc-category: "Reporte de laboratorio",
  doc-title: "Réplica Hill 2002",
  author: "María Luz Stewart Harris",
  affiliation: "Instituto Balseiro",
  // logo: image("assets/aerospace-engineering.png", width: 2cm),
  // <a href="https://www.flaticon.com/free-icons/aerospace" title="aerospace icons">Aerospace icons created by gravisio - Flaticon</a>
  language: "es",
  compact-mode: true,
  it
)

#let run_soa_i_100_coupler_30_dir = "data/single_ring_laser/experiment_A/"
#let run_soa_i_50_coupler_30_dir = "data/single_ring_laser/experiment_B/"
#let run_soa_i_50_coupler_25_dir = "data/single_ring_laser/experiment_C/"

#let run_soa_i_100_coupler_30 = toml(run_soa_i_100_coupler_30_dir + "/conditions.toml")
#let run_soa_i_50_coupler_30 = toml(run_soa_i_50_coupler_30_dir + "/conditions.toml")
#let run_soa_i_50_coupler_25 = toml(run_soa_i_50_coupler_25_dir + "/conditions.toml")

= Único anillo con láser externo

== Setup utilizado
La figura @fig:single_ring_setup muestra el setup utilizado. Los componentes utilizados se detallan en la @sec:single_ring_setup_componentes. Con este setup, las configuraciones disponibles son:#footnote([No se incluye a la corriente o potencia del láser externo como una configuración de setup se varía con un barrido dentro de cada corrida del experimento])

+ Corriente del SOA
+ Temperatura del SOA
+ Posición del acoplador variable
+ Frecuencia central del filtro pasabanda sintonizable (_tbf_)
+ Temperatura del láser externo


#figure(
  image("assets/hill2002_single_ring_setup.pdf"),
  caption: [Setup de único anillo utilizado]
)<fig:single_ring_setup>

== Experimentos realizados

Se realizaron 3 iteraciones del experimento en las que se cambiaron las configuraciones del setup (ver  @tab:single_ring_setup_configs).

#figure(
  table(
    columns: (1fr, 1fr, 1fr, 1fr),

    [*Configuración de setup*],[*Experimento A*], [*Experimento B*], [*Experimento C*],
    ..for (k, _) in run_soa_i_100_coupler_30.SetupConfig {
      (
        k, 
        str(run_soa_i_100_coupler_30.SetupConfig.at(k)),
        str(run_soa_i_50_coupler_30.SetupConfig.at(k)),
        str(run_soa_i_50_coupler_25.SetupConfig.at(k)),
      )
    }
  )
)<tab:single_ring_setup_configs>

La posición del acoplador variable permite introducir pérdidas a la entrada del SOA. Aplica tanto al láser externo como al láser de anillo.

#figure(
  table(
    columns: (1fr, 1fr, 1fr),
    align: center,
    [*Posición*], [*Transmitancia*], [*¿Medida o\
    extrapolada?*],
    "30", "0.16", "Medida",
    "25", "0.10", "Extrapolada",
    "20", "0.04", "Medida",
  ),
  caption: [Transmitancia del acoplador variable para distinas posiciones.],
)<tab:transmitancia_acoplador>

== Resultados

#todo-inline([Link a los resultados (donde los subo?)])

#set par(justify: true)
#subpar.grid(
  columns: (1fr),
  rows: (2.5in, 2.5in),
  gutter: -2pt,
  caption: [Potencia de ambos láseres (de anillo y externo) a la salida del SOA en función de la potencia de salida del láser externo. Izquierda: láser de anillo. Centro: láser externo. Derecha: Ganancia del SOA (calculada como el cociente de las potencias del láser externo a la salida y a la entrada del SOA.)],
  label: <fig:ring_power>,
  figure(
    caption: [Experimento A],
    stack(
      dir: ltr,
      image(run_soa_i_100_coupler_30_dir + "/ring_laser_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_100_coupler_30_dir + "/ext_laser_in_ring_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_100_coupler_30_dir + "/soa_gain.svg", width: 2.5in)
    )
  ),<fig:power_soa_I_100_coupler_30>,
  figure(
    caption: [Experimento B],
    stack(
      dir: ltr,
      image(run_soa_i_50_coupler_30_dir + "/ring_laser_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_50_coupler_30_dir + "/ext_laser_in_ring_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_50_coupler_30_dir + "/soa_gain.svg", width: 2.5in),
    )
  ),<fig:power_soa_I_50_coupler_30>,
  figure(
    caption: [Experimento C],
    stack(
      dir: ltr,
      image(run_soa_i_50_coupler_25_dir + "/ring_laser_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_50_coupler_25_dir + "/ext_laser_in_ring_vs_ext_laser_power.svg", width: 2.5in),
      image(run_soa_i_50_coupler_25_dir + "/soa_gain.svg", width: 2.5in),
    )
  ),<fig:power_soa_I_50_coupler_25>,
)

== Análisis de resultados

=== Experimentos B y C

Para los casos B y C ($I_"SOA" = 50$mA), la potencia del láser de anillo decae linealmente mientras se aumenta la potencia de salida del láser externo (@fig:power_soa_I_50_coupler_30 y @fig:power_soa_I_50_coupler_25). Esto es debido al efecto no lineal de XGM. Según lo postulado por #todo([citar a Hill]), la pendiente con la disminuye la potencia es igual a $-1/T$, siendo $T$ la transmitancia desde la salida del SOA hasta su entrada. 
En consecuencia, al bajar $T$ introduciendo pérdidas en el lazo la pendiente debería disminuir. 

#figure(
  table(
    columns: (1fr,0.6fr,1fr, 1fr, 0.5fr),
    align: center+horizon,
    [*Experimento*], [*$I_("SOA")$*], [*Transmitancia\
    acoplador*], [*m*], [*T (calc)*],
    "A", "100mA", "0.16", "No apreciable", [-],
    "B", "50mA", "0.16", [$-1.3$], [0.76],
    "C", "50mA", "0.10", [$-3.0$], [0.33],
  ),
  caption: [Pendiente $m$ de la potencia de láser de anillo para los 3 casos y transmitancia de salida a entrada del SOA $T$ estimada a partir de la pendiente],
)<tab:ring_laser_power_pendiente>

Las mediciones (@tab:ring_laser_power_pendiente) se corresponden parcialmente con esta relación entre pendiente y $T$. Por un lado, se observa que el caso con menor transmitancia en el acoplador, y por lo tanto, menor $T$, (experimento C) tiene mayor pendiente que el que tiene mayor transmitancia en el acoplador (experimento B). Sin embargo, al estimar $T$ a partir de la pendiente se obtiene una transmitancia que es mayor a la transmitancia del acoplador, lo cual es un error debido a que $T$ es el producto de transmitancias de elementos sin ganancia que siempre son menores a 1, incluyendo la transmitancia del acoplador:

$ 
  T = T_"acoplador" dot T_"conectores" dot T _"filtro" dot  T _"PC" dot ... \
  => T < T_"acoplador"
$

Por otro lado, al modificar únicamente la transmitancia del acoplador, se debería cumplir que la relación $ -m dot T_"acoplador" = T_"acoplador" / T$ se mantenga constante:

$
  T &= (T_"acoplador" dot T_"conectores" dot T _"filtro" dot  T _"PC" dot ...) \

  => T_"acoplador"/T &= 1/(T_"conectores" dot T _"filtro" dot  T _"PC" dot ...) = k "(constante)"

$

Sin embargo, la relación no es constante entre los experimentos B y C (@tab:T_over_T_coupler). Esto indica que el error no es (únicamente) producto de un error de escala, como podría suceder por ejemplo si se debiese a utilizar un tap de cierta transmitancia y luego por error al convertir la potencia de salida del tap por la potencia real del sistema, utilizar otra transmitancia.

#figure(
  table(
    columns: (1fr,1fr),
    align: center+horizon,
    [*Experimento*], [*$T_"acoplador"/T$*],
    "B", [0.21],
    "C", [0.3],
  ),
  caption: [Pendiente $m$ de la potencia de láser de anillo para los 3 casos y transmitancia de salida a entrada del SOA $T$ estimada a partir de la pendiente],
)<tab:T_over_T_coupler>


// $
//   m_C/m_B = (-1 / T_C)/ (-1/ T_B) = T_B / T_C = (T_"acoplador"_B dot T_"conectores" dot T _"filtro" dot  T _"PC" dot ...) / (T_"acoplador"_C dot T_"conectores" dot T _"filtro" dot  T _"PC" dot ...) = T_"acoplador"_B/T_"acoplador"_C \
//   => m_C/m_B = T_"acoplador"_B/T_"acoplador"_C
// $




=== Experimento A


#todo-inline[Exper A no se ve XGM pero sí se ve que cambia la pendiente de Plaser ext despues del soa en funcion de antes del SOA]

#todo-inline([Tiene sentido que con corriente mas alta vea menos, porque la velocidad a la que se excitan los e- es mayor entonces hay menos XGM])

#todo-inline[SOA gain < 1? Imposible, indica claramente un error de medición. Sospecho fuertemente del acoplador variable ]

== Limitaciones y posibles mejoras


#table(
  columns: (1fr,1fr),
  [*Limitación*], [*Posible mejora*],
  [Al reducir $T$ aumentando la atenuación del acoplador variable también se aumenta la atenuación que afecta al láser de entrada antes de llegar al SOA. Por lo tanto, a la misma potencia de salida del láser externo, la potencia con la que llega a la entrada del SOA es dependiente de la atenuación del acoplador configurada. Esto hace que sea más difícil comparar resultados entre iteraciones del experimento con diferentes $T$.],
  [Agregar una atenuación variable en una posición del lazo de forma tal que no afecte a la potencia del láser externo que llega al SOA. ],
  [No hay una medición de la potencia del láser externo a la entrada del SOA, sino que debe estimarse a partir de la potencia de salida del láser externo y la atenuación del acoplador variable. A su vez, estas dos variables tampoco son medidas sino que son estimadas: 
  - La potencia del láser externo es estimada a partir de la corriente y temperatura configuradas.#footnote([La calibración de potencia de salida en función de corriente y temperatura para el láser utilizado se realizó con mediciones de hasta 80mA únicamente, y el barrido de corriente para este experimento llega hasta los 150 mA. Para estimar la potencia de salida con corrientes mayores a 80mA, se extrapola asumiendo una pendiente constante entre potencia y corriente una vez que se supera una corriente umbral.])
  - La atenuación del acoplador variable es estimada a partir de la posición configurada.#footnote([Las mediciones previas de atenuación en función de la posición del atenuador variable indicaron que hay histéresis y variaciones temporales consierables, haciendo que sea menos confiable la estimación.])],
  [Hacer una medición directa de la potencia de salida del láser externo con un tap y no agregar atenuación antes de llegar a la entrada del SOA.],
  [$T$ depende fuertemente de la atenuación del acoplador, que cuando fue calibrado se observó que era difícil de controlar debido a que presentaba histéresis y un drift temporal considerable.#footnote([Por ejemplo, con el acoplador configurado en posición 10, la transmitancia de la salida TP subió de -46.50 dB a -26.15 dB en 15 minutos de funcionamiento continuo.])],[Utilizar un atenuador variable con menos histéresis y drift temporal o en su defecto atenuadores constantes que se puedan cambiar de acuerdo a la prueba que se quiera realizar.],
  [Para hacer barrido en un rango de potencias de salida de láser externo, primero hay que estimar qué corriente de láser corresponde a cada potencia del rango.],[ Mantener el láser en condiciones de operación fijas (corriente y temperatura) y modular su potencia con un modulador externo.],
)

#todo-inline([Efecto de ignorar el control de polarización])


= Dos anillos interconectados con láser externo

== Setup

#figure(
  image("assets/hill2002_two_rings_setup.pdf"),
  caption: [Setup de dos anillos (versión A).]
)<fig:two_rings_setup>

#figure(
  image("assets/hill2002_two_rings_setup_B.pdf"),
  caption: [Setup de dos anillos (versión B).]
)<fig:two_rings_setup_B>

#figure(
  image("assets/hill2002_two_rings_setup_C.pdf"),
  caption: [Setup de dos anillos (versión C).]
)<fig:two_rings_setup_C>


= Anexo

== Único anillo con láser externo

=== Parámetros del setup<sec:single_ring_setup_componentes>

#table(
  columns: (2fr,3fr),

  [*Parámetro del setup*],[*Description*],
  ..for (k, v) in run_soa_i_100_coupler_30.SetupDescription {
    (k, str(v))
  }
)



=== Conversión entre corriente y potencia del laser externo
#todo-inline([toda esta seccion, modelo utilizado para aproximar la curva (no tiene en cuenta el codo, asume que es lineal)])

=== Script de automación
#todo-inline([Link a git])

