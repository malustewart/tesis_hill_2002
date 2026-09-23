
#import "@preview/basic-report:0.4.0": *
#import "@preview/dashy-todo:0.1.3": todo
#import "@preview/subpar:0.2.2"

#show link: it => {
  underline(text(fill:blue, font:"Consolas",it))
}
#show link: emph
#show link: set text(blue)
// #show link: {
//   underline
//   set text(blue)
// }



#let numbered_eq(content) = math.equation(
    block: true,
    numbering: "(1)",
    content,
)

#let numbered_eq_box(eq_label, content) = align(center)[
  #rect[
    #numbered_eq(content) #label(eq_label)
  ]
]


#let annex(body) = {
  pagebreak()
  counter(heading).update(0)
  set heading(numbering: "A.1.")
  body
}

#let todo-inline = todo.with(position:"inline")
#let pregunta  = (..args) => grid(columns:(1fr, 9fr), align:horizon)[
  #text(size:3em)[❔]
][
  #text(size: 1.5em, style:"italic", weight:"extralight", fill:olive)[#todo(position:"inline", stroke:7pt + olive, ..args)]
]
#let missing-fig = rect.with( width: 100%, height: 3in, stroke: stroke(paint: red, thickness: 7pt))

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

#pagebreak()
#outline()
#outline(title: "TODOs", target: figure.where(kind: "todo"))

#pagebreak()
= Introducción

Este informe presenta y analiza los resultados de laboratorio obtenidos al replicar @Hill_Frietman_de_Waardt_Khoe_Dorren_2002.

= Setup

#figure(
  image("assets/hill2002_two_rings_setup_D.pdf"),
  caption: [Setup de dos anillos.]
)<fig:two_rings_setup_d>

 - $lambda_1$: Longitud de onda del láser de anillo 1, sintonizada mediante $"tbf"_1$.
 - $lambda_2$: Longitud de onda del láser de anillo 2, sintonizada mediante $"tbf"_2$.
 - $lambda_"ext"$: Longitud de onda del láser externo.

Los filtros $"tbf"_1$ y $"tbf"_2$ son sintonizados tal que el espectro de los 3 láseres esté lo más cercano posible sin superponerse. De esta forma, toda la potencia a la salida del filtro $"tbf"_1$ corresponde al láser de anillo 1, y toda la potencia a la salida del filtro $"tbf"_2$ corresponde al láser de anillo 2.

Las 4 transmitancias utilizadas como parámetros del sistema son:

 - $T_11$: Transmitancia entre la salida del SOA 1 y la entrada del SOA 1 para $lambda_1$.
 - $T_12$: Transmitancia entre la salida del SOA 1 y la entrada del SOA 2 para $lambda_1$
 - $T_21$: Transmitancia entre la salida del SOA 2 y la entrada del SOA 1 para $lambda_2$.
 - $T_22$: Transmitancia entre la salida del SOA 2 y la entrada del SOA 2 para $lambda_2$.

Las transmitancias $T_"ij"$ son medidas a lazo abierto con un láser sintonizable a $lambda=lambda_i$. Por ejemplo, para medir $T_12$:
+ Se desconectan los puntos "TP SOA OUT 1" y "TP SOA IN 2".
+ Se conecta un láser de $lambda=lambda_1$ y potencia conocida a "TP SOA OUT 1".
+ Se mide la potencia en "TP SOA IN 2".
+ Se calcula la transmitancia como el cociente entre la potencia de salida en "TP SOA IN 2" y la de entrada en "TP SOA OUT 1" 

Las 3 potencias medidas son:

 - $P_"ring"_1$: potencia del láser de anillo a la salida del SOA 1 (punto "TP SOA OUT 1" en la @fig:two_rings_setup_d).
 - $P_"ring"_2$: potencia del láser de anillo a la salida del SOA 2 (punto "TP SOA OUT 2" en la @fig:two_rings_setup_d).
 - $P_"ext"$: potencia del láser externo a la entrada del SOA 1 (punto "TP SOA IN 1" en la @fig:two_rings_setup_d).

Notar que $P_"ring"_"i" != P_"out"_"i"$, donde $P_"out"_"i"$ es la potencia de salida total a la salida del SOA i, sino únicamente la parte de esa potencia de $lambda_"i"$:
$
  P_"out"_1 &= P_"ring"_1 + G_1 dot (P_"ext" + T_21 P_"ring"_2) \
  P_"out"_2 &= P_"ring"_2 + G_2 dot T_12 P_"ring"_1 \
$

donde $G_"i"$ es la ganancia del SOA i.

Las potencias $P_"ring"_"i"$ son calculadas como la potencia total a la salida del $"tbf"_"i"$ (únicamente en $lambda_"i"$, medida con el $"PD"_"i"$ a través del $"tap"_"i"$) compensada por las pérdidas en el $"tbf"_"i"$ y el aislador $"i"$:

$
  P_"ring"_"i" = P_"PD"_"i"/(T_"tap"_"i" dot T_"tbf"_"i" dot T_"aislador"_"i")
$


= Análisis estacionario

== 1 anillo

Para un único anillo con transmitancia $T$ entre la salida y la entrada del SOA, la relación entre $P_"ring"$ y $P_"ext"$ en estado estacionario es descripta por la @eq:Pring_vs_Pext_y_T (deducción en la @sec:Pring_vs_ext_single_ring).

#numbered_eq_box("eq:Pring_vs_Pext_y_T")[
  $
    P_"tot" &= 1/(1-T) ln(G_0)P_"sat" \
    P_"ring" &= cases(
      P_"tot" - P_"ext"/T "   si" P_"ext" < T P_"tot",
      0 "              si" P_"ext" >= T P_"tot",
    )
  $
]

De @eq:Pring_vs_Pext_y_T, se espera que:
+ Si $P_"ext"=0 => P_"ring" = P_"tot"= 1/(1-T) ln(G_0)P_"sat"$
+ $P_"ring"$ decrece linealmente con pendiente $-1/T$ al aumentar $P_"ext"$, hasta que $P_"ring"=0$
+ Si $P_"ext" >= T P_"tot" => P_"ring" = 0$

La @fig:stat_1_basic muestra la relación entre $P_"ring"$ y $P_"ext"$ para un sistema de 1 anillo con $T=-9.99"dB"$ y el $P C_1$ posicionado tal que se maximice $P_"tot"$.

#subpar.grid(
  figure(image("assets/plots/stat_1_basic_vs_ext_smooth.png"), caption: []), <fig:stat_1_basic_vs_t>,
  figure(image("assets/plots/stat_1_basic_vs_t_smooth.png"), caption: []), <fig:stat_1_basic_vs_ext>,
  columns: (1fr),
  gutter: 1em,
  caption: [$P_"ring"$ y $P_"ext"$ para un sistema de 1 anillo con $T=-9.99"dB"$ y el PC posicionado tal que se maximice $P_"tot"$.
],
  label: <fig:stat_1_basic>
)

=== Dependencia con T
En esta sección se asume que el PC se encuentra posicionado tal que se maximice $P_"tot"$.

De acuerdo a la @eq:Pring_vs_Pext_y_T), al reducir $T$: 
+ disminuye $P_"tot"$
+ la pendiente negativa de la recta $P_"ring" (P_"ext")$ se vuelve más pronunciada

La @fig:stat_1_multiple_T muestra 3 mediciones con diferente $T$, en donde se observa que se cumplen los dos puntos anteriores.

Los valores de $P_"tot"$ y de pendiente medidos no coinciden exactamente con los valores esperados de acuerdo a la @eq:Pring_vs_Pext_y_T. La @fig:stat_1_T_vs_Ptot superpone:
 - $T$ medida
 - $T$ estimada en función de la pendiente (@sec:Pring_vs_ext_single_ring)
 - $T$ estimada en función de $P_"tot"$ (@sec:Gdb_vs_Pout_SOA)

Las estimaciones de $T$ difieren de la medición por entre $1"dB"$ y $tilde 7"dB"$. La @sec:mejoras presenta posibles explicaciones para ambas discrepancias.

#figure(
  image("assets/plots/stat_1_moving_att_smooth.png"),
  caption: [
    Variación de curva $P_"ring"$ vs. $P_"ext"$ ante modificaciones de $T$ para un sistema de 1 anillo con el PC posicionado tal que se maximice $P_"tot"$.
  ]
) <fig:stat_1_multiple_T>


#figure(
  image("assets/plots/stat_1_moving_att_T_med_vs_est.png"), 
  caption: [
    $T$ medida y estimada para casos de la @fig:stat_1_multiple_T
  ],
)<fig:stat_1_T_vs_Ptot>


=== Efecto del posicionamiento del PC <sec:stat_1_efecto_PC>
En esta sección se asume que la $T$ es constante.

La posición del PC afecta a la curva $P_"ring"$ vs. $P_"ext"$ de forma similar a modificar $T$ (@fig:stat_1_multiple_PC_pos). Una posible explicación es que dependiendo de la posición del PC la transmitancia efectiva varíe en función de cuánto rota la polarización al dar una vuelta entera por el anillo. En el caso de que la rotación de polarización en una vuelta del anillo sea múltiplo de $2 pi$, la interferencia es máxima y se obtiene la mayor $P_"ring"$ posible para el $T$ medido a lazo abierto.

#figure(
  image("assets/plots/stat_1_moving_PC_smooth.png"),
  caption: [
    Variación de curva $P_"ring"$ vs. $P_"ext"$ ante modificaciones de la posición del PC para un sistema de 1 anillo con $T=-9.99"dB"$.
  ]
) <fig:stat_1_multiple_PC_pos>


== 2 anillos
#figure(
  image("assets/Hill2002_ring_vs_ext_tworings.PNG"),
  caption: [Comportamiento esperado de sistema de 2 anillos interconectados (obtenida de @Hill_Frietman_de_Waardt_Khoe_Dorren_2002).]
)<fig:stat_2_hill>

=== Sistema con $T_"ii" = T_"ij"$

De acuerdo a @Hill_Frietman_de_Waardt_Khoe_Dorren_2002, para obtener una transición con forma de escalón se debe cumplir que $T_"ii" = T_"ij"$ (@fig:stat_2_hill a). Para medir el sistema en esta condición, se configuraron los atenuadores para conseguir que $T_11 approx T_12$ y $T_21 approx T_22$ (@tab:2_ring_manual_T)#footnote[Debido a asimetrías en el acoplador, no existe configuración de atenuadores que logre $T_"ii"=T_"ij"$ de forma exacta (ver @sec:desbalance_acop)] y se posicionaron los $"PC"_1$ y $"PC"_2$ tal que se maximizaran $P_"tot"_1$ y $P_"tot"_2$ respectivamente.

La @fig:stat_2_T_manual_PC_max muestra la medición de $P_"ring"_1$ y $P_"ring"_2$ vs. $P_"ext"$ con esta configuración. El sistema no presenta una transición de escalón como la que se observa en la @fig:stat_2_hill a, sino su transición se corresponde al caso de la @fig:stat_2_hill b. Notablemente, $P_"ring"_2$ nunca 


#figure(
  table(
    columns: 2,
    align: left + horizon,
    stroke: 0.4pt,
    [$T_11$],[$-9.14 "dB"$],
    [$T_12$],[$-9.43 "dB"$],
    [$T_21$],[$-15.17 "dB"$],
    [$T_22$],[$-15.25 "dB"$],
  ),
  caption: [Transmitancias de sistema de 2 anillos para casos A, B, C y D.]
)<tab:2_ring_manual_T>

#figure(
  image("assets/plots/stat_2_manual_T_config_PC_max_smooth.png"), 
  caption: [$P_"ring"_(1,2)$ vs. $P_"ext"$ para sistema de 2 anillos con $T_"ij"$ de la @tab:2_ring_manual_T y $"PC"_(1,2)$ en posición de máxima $P_"tot"$ (caso A).]
)<fig:stat_2_T_manual_PC_max>


Si se mantiene las $T$ previas y se modifica la posición de los PCs, el comportamiento del sistema se modifica significativamente.

La @tab:2_ring_manual_T_trans_comparison resume las caracteristicas de transición (definidas en la @fig:2_ring_P_trans_naming) y las $P_"tot"_"i"$ de 4 casos de posiciones de PC:
- *Caso A*: $"PC"_1$ y $"PC"_2$ posicionados para maximizar $P_"tot"_1$ y $P_"tot"_2$ respectivamente (@fig:stat_2_T_manual_PC_max).
- *Caso B*: $"PC"_1$ desplazado respecto al caso A (@fig:stat_2_T_manual_PC1).
- *Caso C*: $"PC"_2$ desplazado respecto al caso A (@fig:stat_2_T_manual_PC2).
- *Caso D*: $"PC"_1$ y $"PC"_1$ desplazados respecto al caso A (@fig:stat_2_T_manual_PC1_and_PC2).

En ninguno de los 4 casos hubo coincidencia entre los valores de $P_"trans min"$, $P_"trans max"$ y $Delta P_"trans"$ esperados de acuerdo a lo propuesto en @Hill_Frietman_de_Waardt_Khoe_Dorren_2002.

El desplazamiento del PC1 no afecta a $P_"tot"_2$ pero sí reduce $P_"tot"_1$, tal como se evidencia por la comparación entre los casos A y B. A su vez, la transición es más cercana a un escalón debido a la reducción de $Delta P_"trans"$. La modificación de $P_"tot"_1$, $P_"trans min"$, $P_"trans max"$ y $Delta P_"trans"$ pero no de $P_"tot"_2$ coincide a grandes rasgos con lo esperado si se redujera únicamente $T_11$ y se mantuvieran $T_12, T_21$ y $T_22$. Esto es consistente con la hipótesis de la @sec:stat_1_efecto_PC de reducción de $T$ al mover el PC debido a pérdidas por interferencia causadas por rotación de polarización. En el caso de dos anillos, un cambio en la posición del $"PC"_"i"$ afectaría únicamente a $T_"ii"$:
 - El camino caracterizado por $T_"ij"$ (salida del SOA $"i"$ hasta entrada del SOA $"j"$) incluye al $"PC"_"i"$ pero no es parte de un lazo cerrado debido a que inicialmente el $"tbf"_"i"$ rechaza cualquier onda que no sea de $lambda = lambda_"i"$, y luego a la salida del SOA $"j"$ el $"tbf"_"j"$ únicamente transmite ondas de $lambda = lambda_"j"$.
 - Los caminos caracterizados por $T_"ji"$ y $T_"jj"$ no pasan por el $"PC"_"i"$.

Comparando el caso A y el caso C, se observa que el cambio de posición de $"PC"_2$ afecta a $P_"tot"_2$ pero no a $P_"tot"_1$. Por otro lado, $Delta P_"trans"$ se reduce principalmente por un desplazamiento de $P_"trans min"$ y en menor medida también por un pequeño desplazamiento de $P_"trans max"$. Similar a lo analizado en la comparación del caso A con el caso B, los cambios observados coinciden a grandes rasgos con lo esperado si se redujera $T_22$.

En el caso D se observa que se modifican $P_"tot"_1$, $P_"tot"_2$, $P_"trans min"$, $P_"trans max"$ y $Delta P_"trans"$ con respecto al caso A.

#figure(
  image("assets/Hill2002_P_trans_naming.png"),
  caption: [Características relevadas de las transiciones del sistema de 2 anillos con el valor correspondiente de acuerdo a @Hill_Frietman_de_Waardt_Khoe_Dorren_2002.]
)<fig:2_ring_P_trans_naming>


#figure(
  table(
    columns: 5,
    align: center + horizon,
    stroke: 0.4pt,
  [*Caso*],[*A*],[*B*],[*C*],[*D*],
  [*Posición $"PC"_1$*],      [MAX],   [No MAX], [MAX],    [No MAX],
  [*Posición $"PC"_2$*],      [MAX],   [MAX],    [No MAX], [No MAX],
  [*$P_"tot"_1$ [mW]*],       [5.98],  [4.96], [5.98], [4.54],
  [*$P_"tot"_2$ [mW]*],       [ 2.13], [2.13], [1.21], [1.84],
  [*$P_"trans min"$ [mW]*],   [-0.35], [0.40], [1.25], [0.55],
  [*$P_"trans max"$ [mW]*],   [ 1.75], [0.50], [1.70], [0.65],
  [*$Delta P_"trans"$ [mW]*], [ 2.10], [0.10], [0.45], [0.10],
  ),
  caption: [Características de las transiciones del sistema para 4 casos con mismas $T_"ij"$ y diferentes posiciones de PCs. Los valores de $P_"trans min"$ negativos corresponden al cruce por cero de la proyección de la curva $P_"ring"_2$ vs. $P_"ext"$ en los casos que $P_"ring"_2(P_"ext") > 0$]
)<tab:2_ring_manual_T_trans_comparison>


#figure(
  image("assets/plots/stat_2_manual_T_config_moved_PC1_smooth.png"), 
  caption: [Caso A comparado con mismo sistema luego de mover $"PC"_1$ (caso B).]
)<fig:stat_2_T_manual_PC1>

#figure(
  image("assets/plots/stat_2_manual_T_config_moved_PC2_smooth.png"), 
  caption: [Caso A comparado con mismo sistema luego de mover $"PC"_2$ (caso C).]
)<fig:stat_2_T_manual_PC2>

#figure(
  image("assets/plots/stat_2_manual_T_config_moved_PC1_and_PC2_smooth.png"), 
  caption: [Caso A comparado con mismo sistema luego de mover $"PC"_1$ y $"PC"_2$ (caso D).]
)<fig:stat_2_T_manual_PC1_and_PC2>

=== Efecto de la frecuencia y la forma de onda de $P_"ext"$

La @fig:stat_2_sin_vs_triangle_vs_ext compara la respuesta del sistema para un láser externo modulado con el mismo periodo pero diferente forma de onda. Las curvas $P_"ring"_1$ y $P_"ring"_2$ vs $P_"ext"$ muestran mayor histéresis para la modulación senoidal que para la triangular, especialmente en el anillo 2. En la @fig:stat_2_sin_vs_triangle_vs_t_sin, @fig:stat_2_sin_vs_triangle_vs_t_triangle se observa que $(d P_"ext")/(d t)$ alcanza valores más altos.


La @fig:stat_2_diff_mod_freq compara la respuesta del sistema para un láser externo modulado con diferente periodo. Al disminuir el periodo de modulación, la respuesta de ambos anillos presenta más histéresis. De las 3 mediciones, se grafica la de periodo de $1$ms en la @fig:stat_2_sin_vs_triangle_vs_t_sin.


#figure(
  image("assets/plots/stat_2_senoid_diff_mod_freq_smooth.png"), 
  caption: [2 anillos, senoidal, diferente freq de modulacion]
)<fig:stat_2_diff_mod_freq>


#subpar.grid(
  figure(image("assets/plots/stat_2_1ms_diff_mod_shape_smooth.png"), caption: [$P_"ring"_(1,2)$ vs $P_"ext"$.]), <fig:stat_2_sin_vs_triangle_vs_ext>,
  figure(image("assets/plots/stat_2_1ms_diff_mod_shape_vs_t_sin_smooth.png"), caption: [Modulación de láser externo con señal senoidal.]), <fig:stat_2_sin_vs_triangle_vs_t_sin>,
  figure(image("assets/plots/stat_2_1ms_diff_mod_shape_vs_t_triangle_smooth.png"), caption: [Modulación de láser externo con señal triangular.]), <fig:stat_2_sin_vs_triangle_vs_t_triangle>,
  columns: (1fr),
  gutter: 1em,
  caption: [Respuesta de sistema de dos anillos ante láser externo modulado con la misma frecuencia y diferente forma.],
  label: <fig:stat_2_sin_vs_triangle> 
)


=== Ajuste de $T$ y $"PC"$ para transición de escalón

// #figure(
//   image("assets/plots/stat_2_PC_max_att_a_ojo_smooth.png"), 
//   caption: [PC max, attenuators a ojo]
// )<fig:stat_2_PC_max_att_a_ojo> 


Se realizó un ajuste manual de los atenuadores y los $"PC"$ observando en tiempo real las curvas $P_"ring"_1$ y $P_"ring"_2$ vs. $P_"ext"$ y buscando obtener la transición lo más cercana a un escalón posible. La @fig:stat_2_PC_y_att_a_ojo muestra la medición correspondiente.

#figure(
  table(
    columns: 2,
    align: center + horizon,
    stroke: 0.4pt,
    [$P_"tot"_1$],[$5.14$ mW],
    [$P_"tot"_2$],[$3.15$ mW],
    [$T_11$],[$-9.94 "dB"$],
    [$T_12$],[$8.98 "dB"$],
    [$T_21$],[$9.90 "dB"$],
    [$T_22$],[$8.64 "dB"$],
  ),
  caption: [Transmitancias y $P_"tot"_"i"$ del sistema de 2 anillos configurado para asemejar la transición a un escalón.]
)<tab:2_ring_PC_y_att_a_ojo>-

#figure(
  image("assets/plots/stat_2_att_y_PC_a_ojo_smooth.png"),
  caption: []
)<fig:stat_2_PC_y_att_a_ojo> 


= Análisis transitorio

#todo-inline[Comentar en más detalle los resultados del analisis transitorio, en especial los de 2 anillos.]

== 1 anillo

#subpar.grid(
  figure(image("assets/plots/trans_1_rise_two_y_axis_smooth.png"), caption: []), <fig:trans_1_rise_full>,
  figure(image("assets/plots/trans_1_rise_two_y_axis_zoom_smooth.png"), caption: []), <fig:trans_1_rise_zoom>,
  columns: (1fr, 1fr),
  gutter: 1em,
  caption: [Respuesta del sistema de 1 anillo ante un flanco ascendente del láser externo.],
  label: <fig:trans_1_rise>
)

#subpar.grid(
  figure(image("assets/plots/trans_1_fall_two_y_axis_smooth.png"), caption: []), <fig:trans_1_fall_full>,
  figure(image("assets/plots/trans_1_fall_two_y_axis_zoom_smooth.png"), caption: []), <fig:trans_1_fall_zoom>,
  columns: (1fr, 1fr),
  gutter: 1em,
  caption: [Respuesta del sistema de 1 anillo ante un flanco descendente del láser externo.],
  label: <fig:trans_1_fall>
)


El tiempo de subida y de bajada del sistema de 1 anillo es de $approx 1 mu"s"$

== 2 anillos

#subpar.grid(
  figure(image("assets/plots/trans_2_vs_t_linesweep_smooth.png"), caption: []), <fig:trans_2_triangle_vs_t>,
  figure(image("assets/plots/trans_2_vs_ext_linesweep_smooth.png"), caption: []), <fig:trans_2_triangle_vs_ext>,
  columns: (1fr),
  gutter: 1em,
  caption: [],
  label: <fig:trans_2_triangle>
)


#subpar.grid(
  figure(image("assets/plots/trans_2_rise_vs_t_linesweep_zoom_smooth.png"), caption: []), <fig:trans_2_triangle_vs_t_rise>,
  figure(image("assets/plots/trans_2_fall_vs_t_linesweep_zoom_smooth.png"), caption: []), <fig:trans_2_triangle_vs_t_fall>,
  columns: (1fr, 1fr),
  gutter: 1em,
  caption: [],
  label: <fig:trans_2_triangle_vs_t_rise_and_fall>
)


#subpar.grid(
  figure(image("assets/plots/trans_2_rise_smooth.png"), caption: []), <fig:trans_2_rise_step_vs_t>,
  figure(image("assets/plots/trans_2_rise_zoom_smooth.png"), caption: []), <fig:trans_2_rise_step_vs_t_zoom>,
  columns: (1fr, 1fr),
  gutter: 1em,
  caption: [],
  label: <fig:trans_2_rise>
)

#figure(
  image("assets/plots/trans_2_fall_zoom_smooth.png"),
  caption: []
)<fig:trans_2_fall>



= Oportunidades de mejora <sec:mejoras>

+ Para el caso de 1 anillo, la estimación de $T$ a través de $P_"tot"$ difiere de la $T$ medida debido a que la relación entre la $T$ y la $P_"tot"$ medidas no coincide con la curva $G_"dB" (P_"out")$ obtenida en una caracterización previa (@sec:Gdb_vs_Pout_SOA). Es recomendable revisar y/o rehacer las mediciones de $G_"dB" (P_"out")$ verificando que se mantengan las mismas condiciones que las utilizadas en el sistema final. Es notable que para el rango de $P_"tot"$ utilizadas en las mediciones de 1 anillo, la caracterización previa muestra un comportamiento lineal entre $P_"tot"$ y $T$, mientras que en las mediciones se evidencia una relación no lineal similar a la esperada en el "codo" de la curva $G_"dB"$ vs. $P_"tot"$.
+ Para el caso de 1 anillo, la potencia total de salida del SOA $P_"out" = P_"ring" + P_"ext"/T$ no es constante para las $P_"ext" slash.big P_"ring">0$, cuando es esperado que para ese rango de $P_"ext"$ se cumpla que $P_"out" = P_"tot" " " (c t e)$. Combinado con que la relación entre $P_"ring"$ y $P_"ext"$ es una recta como era esperado, esto indica un error de escala en la medición de $P_"ring"$ y/o $P_"ext"$.
+ Para el caso de 1 anillo, la estimación de $T$ a través de la pendiente de $P_"ring"$ vs. $P_"ext"$ difiere de la $T$ medida. Un factor contribuyente es el error de escala en la medición de $P_"ring"$ y/o $P_"ext"$ en el punto anterior.
+ Elegir $T_"ii"$ y $I_"SOA"$ para que el SOA trabaje en la zona "lejana al codo" de la curva $G_"dB"$ vs. $P_"out"$, ie.: que se cumpla la aproximación utilizada en @sec:Gdb_vs_Pout_SOA para llegar a la @eq:Pring_vs_Pext_y_T
+ Realizar mediciones de tiempo de subida y bajada de ambos anillos para diferentes $P_"tot"$, debido a que el sistema presenta un comportamiento no lineal donde el tiempo de subida/bajada varía en función de la altura del escalón.

#show: annex
= Anexo

== Potencia en un láser de anillo $P_"ring"$ en función de la transmitancia de lazo $T$ y la potencia externa $P_"ext"$ <sec:Pring_vs_ext_single_ring>



#figure(
  image("assets/Hill2002_setup_singlering.PNG"),
  caption: [Sistema de láser de anillo con entrada de láser externo.]
)<fig:anexo_sistema_1_anillo>

Para el sistema de la @fig:anexo_sistema_1_anillo el filtro dentro del anillo se configura en $lambda=lambda_"ring" != lambda_"ext"$, de forma tal que el láser de anillo trabaje a una longitud de onda $lambda_"ring"$ diferente a la del láser externo $lambda_"ext"$.

=== $P_"ring" (P_"ext", T)$

$
  gamma = gamma_0/(phi.alt/phi.alt_"sat" + 1),
$

$
  ln(Y) + Y = ln(X) + X + ln(G_0)
$
donde
$
  X &= P_"in"/P_"sat" \
  Y &= P_"out"/P_"sat" \
  ln(G_0) &= gamma_0 d \
  G &=Y/X
$

Asumiendo que $P_"in" >> P_"sat"$:
$
  Y &approx X + ln(G_0) \
  => Y/X &= 1 + ln(G_0)/X\
  => G &= 1 + (ln(G_0)P_"sat")/P_"in"
$


$P_"in"$ es la suma de potencias de dos fuentes distintas en diferentes $lambda$, el láser externo y el láser de anillo:

$
  => G = 1 + (ln(G_0)P_"sat")/(P_"ext" + T P_"ring")
$

donde 
 - $P_"ext"$ es la potencia en $lambda_"ext"$ en la entrada del SOA.
 - $P_"ring"$ es la potencia a la salida del SOA para $lambda_"ring"$.
 - $T$ es la transmitancia desde la salida del SOA hasta la entrada para $lambda_"ring"$. 


En estado estacionario, la ganancia de una vuelta completa por el anillo para $lambda_"ring"$ es $1$:

$
  1 &= G dot T  \
  // 1/T &= G  \
  1/T &= 1 + (ln(G_0)P_"sat")/(P_"ext" + T P_"ring") \
  P_"ext" + T P_"ring" &= T/(1-T) ln(G_0)P_"sat" \
$


#align(center)[
  #rect[
    $
      P_"ring" &= 1/(1-T) ln(G_0)P_"sat" - P_"ext"/T
    $
  ]
]




// === Estimación de $T$ a partir de $P_"tot"$

// $
//   P_"tot" eq.delta lr(P_"ring"|, size: #150%)_(P_"ext"=0) \
// $

// A partir de la @eq:Pring_vs_Pext_y_T:
// $
//   P_"tot" = 1/(1-T) ln(G_0)P_"sat" \
// $

// #numbered_eq_box("eq:T_est_desde_Ptot")[
//   $
//     T = 1- ...
//   $
// ]

=== Estimación de $T$ a partir de la pendiente de  $P_"ring" (P_"ext")$

A partir de @eq:Pring_vs_Pext_y_T:
$
  (partial P_"ring") / (partial P_"ext") = - 1/T
$
$(partial P_"ring") / (partial P_"ext")$ es una constante,#footnote[ $forall
 P_"ring" > 0 <=> P_"ext" < T P_"tot"$] por lo que 

#numbered_eq_box("eq:T_est_pendiente")[
  $
     T = -1/m
  $
]
donde
$
  m eq.delta (partial P_"ring") / (partial P_"ext")
$
es la pendiente de la recta $P_"ring" (P_"ext")$.


== Relación entre potencia de salida y ganancia del SOA <sec:Gdb_vs_Pout_SOA>

=== Medición y ajuste de $G$


Se midió $P_"in"$ y $P_"out"$ de un SOA para un barrido de $P_"in"$ en las condiciones de trabajo ($I_"SOA"$ y $T_"SOA"$) utilizadas para los dos anillos(@fig:G_measurement_Pout_vs_Pin). Se calculó $G_"dB" = 10dot log_(10) (P_"out"/P_"in")$ y se realizó un ajuste de $G_"dB" approx hat(G)_"dB"$ de acuerdo a la @eq:G_dB_fit. La @fig:G_measurement_GdB_vs_Pout muestra la relación entre la ganancia y $P_"out"$, tanto medida ($G_"dB"$) como aproximada por el ajuste ($hat(G)_"dB"$).

#numbered_eq(
$
  hat(G)_"dB" (P_"out") = a + b dot P_"out" + c dot (P_"out")^2 + d / (e+P_"out")
$
) <eq:G_dB_fit>


#figure(
  table(
    columns: 8,
    align: center + horizon,
    stroke: 0.4pt,
  [Anillo],[$I_"SOA" med ["mA"]$],[$T_"SOA" med [degree"C"]$],[$a$],[$b med ["mW"^(-1)]$],[$c med ["mW"^(-2)]$],[$d med ["mW"]$],[$e med ["mW"]$],
  [1],[270],[25],[$11.4050$],[$0.0884$],[$-0.1187$],[$0.8817$],[$-0.1024$],
  [2],[180],[25],[$7.2637$],[$-0.9424$],[$-0.1411$],[$0.0962$],[$-0.0385$],
  )
)

#subpar.grid(
  figure(image("assets/plots/gain_meas_Pout_vs_Pin_mW.png"), caption: [$P_"out"$ vs. $P_"in"$]), <fig:G_measurement_Pout_vs_Pin>,
  figure(image("assets/plots/gain_meas_G_dB_vs_Pout_mW.png"), caption: [$G_"dB"$ vs. $P_"out"$]), <fig:G_measurement_GdB_vs_Pout>,
  columns: (1fr),
  gutter: 1em,
  caption: [Mediciones realizadas en los SOAs],
  label: <fig:G_measurement>
)

=== Estimación de $T$ a partir de $P_"tot"$

Para las condiciones de trabajo en las que se realizaron las mediciones, es posible estimar $G$ a partir de $P_"out"$ con el ajuste de la @eq:G_dB_fit (@fig:G_measurement_GdB_vs_Pout).


$
  P_"out" &= P_"ring" + G P_"ext"\
$
Cuando $P_"ext" = 0$, $P_"out" = P_"ring"$:
$
  P_"out" &= lr(P_"ring"|, size: #150%)_(P_"ext"=0)  eq.delta P_"tot"
$

En estacionario $G dot T = 1$, por lo tanto:

#numbered_eq_box("eq:T_est_Ptot")[
  $
    hat(T)_"dB" (P_"tot") = -hat(G)_"dB" (P_"tot") = -(a + b dot P_"tot" + c dot (P_"tot")^2 + d / (e+P_"tot"))
  $
]


== Efecto del desbalance del acoplador/divisor 2 en la condición de transición en escalón <sec:desbalance_acop>

$ 
  T_"ij" &= T_"out"_"i" + T_"ac"_"ij" +T_"in"_"j"
$
donde
- $T_"out"_"i"$: Transmitancia entre la salida del SOA $"i"$ y la entrada del acoplador/divisor 2.
- $T_"ac"_"ij"$: Transmitancia entre la entrada del acoplador/divisor 2 conectada al anillo $"i"$ y la salida del acoplador/divisor 2 conectada al anillo $"j"$ 
- $T_"in"_"j"$: Transmitancia entre la salida del acoplador/divisor 2 y la entrada del SOA $"j"$.

Para obtener una transición con forma de escalón se debe cumplir que $T_"ii" = T_"ij"$ :
$
  &&T_"ii" &= T_"ij" \
  &arrow.r.double&  T_"out"_"i" + T_"ac"_"ii" +T_"in"_"i"  &= T_"out"_"i" + T_"ac"_"ij" +T_"in"_"j" \
  &arrow.r.double&  T_"ac"_"ii" +T_"in"_"i"  &= T_"ac"_"ij" +T_"in"_"j" \
  &arrow.r.double&  T_"in"_"i"  &= T_"in"_"j" + T_"ac"_"ij" - T_"ac"_"ii"
$

Para un sistema de 2 SOAs $1, 2$:

$
   arrow.r.double&cases(
    T_"in"_"1"  &= T_"in"_"2" + T_"ac"_"12" - T_"ac"_"11",
    T_"in"_"2"  &= T_"in"_"1" + T_"ac"_"21" - T_"ac"_"22"
  )
$

$
  arrow.r.double & 0 "dB"= (T_"ac"_"11" - T_"ac"_"12") + (T_"ac"_"22" - T_"ac"_"21")
$

Las mediciones de las transmitancias del acoplador utilizado son:

#figure()[
  #table(
    columns: 2,
    align: left + horizon,
    stroke: 0.4pt,
  [$T_"ac"_11$],
  [-3.43 dB],
  [$T_"ac"_12$],
  [-3.31 dB],
  [$T_"ac"_21$],
  [-3.06 dB],
  [$T_"ac"_22$],
  [-3.38 dB],
  )
]
$
  arrow.r.double (T_"ac"_"11" - T_"ac"_"12") + (T_"ac"_"22" - T_"ac"_"21") = 0.20 "dB"
$


== Scripts de automación

https://github.com/malustewart/tesis_hill_2002

#bibliography("refs.bib")