#!/usr/bin/env python3
"""Genera la portada de antxiko.github.io en los dos idiomas.

    python3 tools/make_index.py

Escribe index.html (ingles) y es/index.html (castellano). El diseno es el de la
serie de desensamblados: la hoja de estilo se importa tal cual de
tools/estilo_web.py (el mismo fichero que usan las webs de los juegos) y aqui
solo se anade lo propio de una portada de indice: la tarjeta de proyecto.

TODOS los datos de cada proyecto salen de su repositorio local: las cifras y las
frases, de su README; la URL del repositorio, de su remote de git; y la URL de su
web, del remote mas la existencia de docs/index.html. Un proyecto sin web se
queda sin enlace de web, y no se inventa ninguna.

La pagina son secciones de primer nivel (CATEGORIAS: hoy los desensamblados y
los parches). Una seccion puede ir en partes: la de los desensamblados lleva las
cifras, tres grupos de juegos (Konami, exclusivos de MSX, conversiones) y el
metodo, y cada juego dice su grupo en el campo 'grupo'. Para anadir otra clase
de proyecto: otra lista con los mismos campos que DESENSAMBLADOS y otra entrada
en CATEGORIAS. El menu, las secciones y sus partes se generan de esas listas.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo_web import ESTILO

USUARIO = "antxiko"

# Lo unico que se anade a la hoja de estilo de la serie: la tarjeta de proyecto.
# Usa el mismo mecanismo de rejilla que .cifras (separador de 1px en --linea
# sobre --panel) para que se vea como las tarjetas de las webs de los juegos.
EXTRA = """
header.top h1{margin:0;font-size:2.3rem;letter-spacing:.04em}
header.top h1 span{color:var(--rojo)}
.proyectos{display:grid;gap:1px;background:var(--linea);border:1px solid var(--linea);
  grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr))}
.proy{background:var(--panel);padding:1.4rem 1.3rem;display:flex;flex-direction:column}
.proy h3{margin:0 0 .35rem;font-size:1.15rem;color:var(--rojo)}
.proy h3 span{color:var(--suave);font-size:12px;letter-spacing:.08em}
.proy p.meta{margin:0 0 .9rem;font-size:11px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--suave)}
.proy p.claim{margin:0 0 1rem;max-width:none;font-size:15px;color:var(--tinta)}
.proy p.datos{margin:0;padding-top:.85rem;border-top:1px solid var(--linea);
  font-size:13px;color:var(--suave)}
.proy p.datos b{color:var(--oro);font-weight:400;font-variant-numeric:tabular-nums}
.proy p.enlaces{margin:auto 0 0;padding-top:1rem;font-size:12px;letter-spacing:.07em;
  text-transform:uppercase}
.proy p.enlaces a{margin-right:1.1rem}
.proy p.enlaces em{color:var(--suave);font-style:normal}
.parte{margin-top:3rem;scroll-margin-top:1rem}
.parte h3{margin:0 0 1rem;font-size:.95rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--oro)}
.parte h3 span{color:var(--suave);font-size:12px;letter-spacing:.08em;margin-left:.6rem}
"""


def mil(n, idioma):
    return f"{n:,}".replace(",", "." if idioma == "es" else ",")


def cif(n, idioma):
    """Un numero, con su separador de miles, para el pie de una tarjeta."""
    return f"<b>{mil(n, idioma)}</b>"


# --------------------------------------------------------------------------
# Los proyectos. Orden: por ano del juego y, dentro de 1984, por referencia de
# catalogo. Las cifras van copiadas de los README/docs de cada repositorio.
# --------------------------------------------------------------------------
DESENSAMBLADOS = [
    dict(
        clave="3dgolf",
        grupo="msx-exclusive",
        titulo="3D Golf Simulation",
        anio=1983,
        repo="https://github.com/antxiko/3DGolfSimulation-disassembly",
        web="https://antxiko.github.io/3DGolfSimulation-disassembly/",
        meta=dict(
            en="T&amp;E Soft &middot; MSX &middot; 16 KB cartridge",
            es="T&amp;E Soft &middot; MSX &middot; cartucho de 16 KB",
        ),
        claim=dict(
            en="A cartridge <b>without a single Z80 instruction</b>: inside is "
               "a 246-line MSX-BASIC program the interpreter runs straight out "
               "of the ROM, and the boot trick is that the cartridge also "
               "carries <b>the interpreter&rsquo;s variable table from a real "
               "session</b>. The nine holes fit in <b>4,000 bytes</b> of "
               "coordinates, and the game has no terrain map: it asks the "
               "screen what colour the ground under the ball is painted.",
            es="Un cartucho <b>sin una sola instrucción Z80</b>: dentro hay un "
               "programa MSX-BASIC de 246 líneas que el intérprete ejecuta "
               "directamente desde la ROM, y el truco del arranque es que el "
               "cartucho lleva pegada <b>la tabla de variables de una partida "
               "de verdad</b>. Los nueve hoyos caben en <b>4.000 bytes</b> de "
               "coordenadas, y el juego no tiene mapa de terreno: le pregunta a "
               "la pantalla de qué color está pintado el suelo bajo la bola.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> "
                          f"unidentified &middot; <b>retokenises</b> byte for "
                          f"byte &middot; {cif(9041, i)} of BASIC program, "
                          f"{cif(4000, i)} of course &middot; {cif(246, i)} "
                          f"lines &middot; <b>100 %</b> of them commented"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin "
                          f"identificar &middot; <b>retokeniza</b> byte a byte "
                          f"&middot; {cif(9041, i)} de programa BASIC, "
                          f"{cif(4000, i)} de campo &middot; {cif(246, i)} "
                          f"líneas &middot; <b>100 %</b> comentadas"),
        ),
        nota=dict(
            en="the nine holes on its site are drawn from the ROM by running "
               "the program&rsquo;s own drawing subroutines in Python",
            es="los nueve hoyos de su web están dibujados desde la ROM "
               "ejecutando en Python las propias subrutinas de dibujo del "
               "programa",
        ),
    ),
    dict(
        clave="timepilot",
        grupo="konami",
        titulo="Time Pilot",
        anio=1983,
        repo="https://github.com/antxiko/TimePilot-disassembly",
        web="https://antxiko.github.io/TimePilot-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-703",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-703",
        ),
        claim=dict(
            en="The plane does not move: it turns, one step at a time between "
               "sixteen directions, and only the drawing in use is in video "
               "memory. The shots and the end-of-era machine are not sprites "
               "but screen characters that read the cell before writing "
               "themselves into it. And the attract mode flies by reading the "
               "cartridge's own code.",
            es="El avión no se mueve: gira, un paso cada vez entre dieciséis "
               "direcciones, y en la memoria de vídeo solo está el dibujo que "
               "toca. Los disparos y el bicho del final de época no son "
               "sprites, son caracteres de la pantalla que leen la casilla "
               "antes de escribirse en ella. Y la demo vuela leyendo el propio "
               "código del cartucho.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8911, i)} of code, {cif(7473, i)} of data "
                          f"&middot; {cif(593, i)} labels &middot; measured in "
                          f"openMSX: the interrupt takes <b>50.1%</b> of the frame"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8911, i)} de código, {cif(7473, i)} de datos "
                          f"&middot; {cif(593, i)} etiquetas &middot; medido en "
                          f"openMSX: la interrupción se come el <b>50,1 %</b> del "
                          f"cuadro"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="frogger",
        grupo="konami",
        titulo="Frogger",
        anio=1983,
        repo="https://github.com/antxiko/Frogger-disassembly",
        web="https://antxiko.github.io/Frogger-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 8 KB cartridge &middot; RC-704",
            es="Konami &middot; MSX &middot; cartucho de 8 KB &middot; RC-704",
        ),
        claim=dict(
            en="Half the size of any other Konami cartridge here, and it "
               "carries the very same sound player as Time Pilot: 163 bytes "
               "with only three different. Logs and cars do not spend a single "
               "sprite &mdash; four pre-generated versions of every drawing, "
               "shifted two pixels at a time &mdash; and the whole attract "
               "mode fits in fifteen bytes.",
            es="La mitad de grande que cualquier otro Konami de aquí, y lleva "
               "dentro el mismo reproductor de sonido que Time Pilot: 163 "
               "bytes con solo tres distintos. Los troncos y los coches no "
               "gastan un solo sprite &mdash;cuatro versiones pregeneradas de "
               "cada dibujo, de dos en dos píxeles&mdash; y la demo entera "
               "cabe en quince bytes.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(4880, i)} of code, {cif(3312, i)} of data "
                          f"&middot; {cif(314, i)} labels"),
            es=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(4880, i)} de código, {cif(3312, i)} de datos "
                          f"&middot; {cif(314, i)} etiquetas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="supercobra",
        grupo="konami",
        titulo="Super Cobra",
        anio=1983,
        repo="https://github.com/antxiko/SuperCobra-disassembly",
        web="https://antxiko.github.io/SuperCobra-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 8 KB cartridge &middot; RC-705",
            es="Konami &middot; MSX &middot; cartucho de 8 KB &middot; RC-705",
        ),
        claim=dict(
            en="The main thread does nothing: it hooks the interrupt and "
               "settles into a <code>jr $</code> forever, so the whole game "
               "runs inside the video hook. It shares 400 bytes with Athletic "
               "Land and <b>not one run of bytes with Frogger</b>, from the "
               "same year and the same 8 KB. And the letters are not even in "
               "the cartridge: they are copied from the BASIC ROM.",
            es="El hilo principal no hace nada: engancha la interrupción y se "
               "queda en un <code>jr $</code> para siempre, así que el juego "
               "entero corre dentro del gancho de vídeo. Comparte 400 bytes "
               "con Athletic Land y <b>ni un byte seguido con Frogger</b>, del "
               "mismo año y de los mismos 8 KB. Y las letras ni siquiera están "
               "en el cartucho: se copian de la ROM del BASIC.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(5783, i)} of code, {cif(2409, i)} of data "
                          f"&middot; {cif(407, i)} labels &middot; commented "
                          f"to <b>24.2%</b>"),
            es=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5783, i)} de código, {cif(2409, i)} de datos "
                          f"&middot; {cif(407, i)} etiquetas &middot; comentado "
                          f"al <b>24,2 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="athletic",
        grupo="konami",
        titulo="Athletic Land",
        anio=1984,
        repo="https://github.com/antxiko/AthleticLand-disassembly",
        web="https://antxiko.github.io/AthleticLand-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-700",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-700",
        ),
        claim=dict(
            en="Konami's first MSX cartridge. The game is a table of thirty-two "
               "screens, not a map, and what kills you is not the height you fall "
               "to but the height you fell from. The vine is nine drawings, each "
               "ending with the three bytes that say where its tip is.",
            es="El primer cartucho de Konami para MSX. El juego es una tabla de "
               "treinta y dos pantallas, no un mapa, y lo que te mata no es la "
               "altura a la que caes, sino la altura desde la que caíste. La liana "
               "son nueve dibujos, cada uno con tres bytes al final que dicen "
               "dónde está su punta.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7448, i)} of code, {cif(8936, i)} of data "
                          f"&middot; {cif(296, i)} labels"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7448, i)} de código, {cif(8936, i)} de datos "
                          f"&middot; {cif(296, i)} etiquetas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="antarctic",
        grupo="konami",
        titulo="Antarctic Adventure",
        anio=1984,
        repo="https://github.com/antxiko/AntarcticAdventure-disassembly",
        web="https://antxiko.github.io/AntarcticAdventure-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-701",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-701",
        ),
        claim=dict(
            en="Three different builds of this cartridge are taken apart here, "
               "each in its own folder, and all three reassemble byte for byte. "
               "The attract mode is a recording: 64 bytes carrying the joystick's "
               "own bits, read one every 32 frames. And NEW ZEALAND is spelled out "
               "inside for a research base nobody visits.",
            es="Aquí se desmontan tres compilaciones distintas del cartucho, cada "
               "una en su carpeta, y las tres reensamblan byte a byte. La "
               "demostración va grabada: 64 bytes con los bits del propio joystick, "
               "leídos uno cada 32 fotogramas. Y NEW ZEALAND está escrito dentro "
               "para una base a la que no se llega nunca.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; <b>three builds</b>, all <b>byte for byte</b> "
                          f"&middot; main listing: {cif(5947, i)} of code, "
                          f"{cif(10437, i)} of data"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>tres compilaciones</b>, las tres <b>byte a "
                          f"byte</b> &middot; listado principal: {cif(5947, i)} de "
                          f"código, {cif(10437, i)} de datos"),
        ),
        nota=dict(
            en="which build is which is not settled",
            es="cuál es cuál no está cerrado",
        ),
    ),
    dict(
        clave="monkey",
        grupo="konami",
        titulo="Monkey Academy",
        anio=1984,
        repo="https://github.com/antxiko/MonkeyAcademy-disassembly",
        web="https://antxiko.github.io/MonkeyAcademy-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-702",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-702",
        ),
        claim=dict(
            en="Konami's arithmetic cartridge. The five levels are five scripts "
               "of three to five bytes, the digit that gets hidden depends on "
               "the one you can see, and the fruit gets thrown back and forth "
               "between the monkey and the crabs.",
            es="El cartucho de aritmética de Konami. Los cinco niveles son cinco "
               "guiones de tres a cinco bytes, la cifra que se tapa depende de "
               "la que se ve, y las frutas se las tiran unos a otros el mono y "
               "los cangrejos.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8962, i)} of code, {cif(7422, i)} of data "
                          f"&middot; {cif(498, i)} labels"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8962, i)} de código, {cif(7422, i)} de datos "
                          f"&middot; {cif(498, i)} etiquetas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="billiards",
        grupo="konami",
        titulo="Konami&rsquo;s Billiards",
        anio=1984,
        repo="https://github.com/antxiko/KonamisBilliards-disassembly",
        web="https://antxiko.github.io/KonamisBilliards-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-706",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-706",
        ),
        claim=dict(
            en="Collision physics in the eight kilobytes the game uses: trigonometry by slope, "
               "a twelve-byte square root that <b>rounds</b>, and 45&deg; "
               "bounces done by swapping the two velocity components, without "
               "one multiplication. There are only <b>seven balls</b> — the "
               "eighth entry is the point you aim at — and the attract mode "
               "plays by <b>writing the fire button</b> into the same "
               "variables where the player&rsquo;s keys land.",
            es="Una física de choques en los ocho kilobytes que ocupa el juego: trigonometría por "
               "pendiente, una raíz cuadrada de doce bytes que <b>redondea</b>, "
               "y rebotes a 45&deg; resueltos intercambiando las dos "
               "componentes de la velocidad, sin una sola multiplicación. Solo "
               "hay <b>siete bolas</b> —la octava entrada es el punto al que "
               "se apunta— y el attract juega <b>escribiendo el botón de "
               "tiro</b> en las mismas variables donde caen las teclas del "
               "jugador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(5343, i)} of code, {cif(11041, i)} of data "
                          f"&middot; {cif(332, i)} labels &middot; commented "
                          f"to <b>39.3%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5343, i)} de código, {cif(11041, i)} de datos "
                          f"&middot; {cif(332, i)} etiquetas &middot; comentado "
                          f"al <b>39,3 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="mahjong",
        grupo="konami",
        titulo="Konami&rsquo;s Mahjong Dojo",
        anio=1984,
        repo="https://github.com/antxiko/KonamisMahjongDojo-disassembly",
        web="https://antxiko.github.io/KonamisMahjongDojo-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-707",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-707",
        ),
        claim=dict(
            en="The whole game runs <b>inside the interrupt</b> &mdash; the deal, the "
               "scoring, the screens &mdash; while the main program is an "
               "<code>ei / jr $</code> that never gets the machine back. And the "
               "computer <b>does not play mahjong</b>: its thirteen tiles are "
               "written into the cartridge one away from completion, and the tile "
               "it throws is <b>drawn from the wall</b> and then filtered so it "
               "looks like a human discard. Even the empty slot in its face-down "
               "hand is theatre.",
            es="El juego entero corre <b>dentro de la interrupción</b> &mdash;el reparto, "
               "el recuento, las pantallas&mdash; mientras el programa principal es "
               "un <code>ei / jr $</code> que no recupera el control nunca. Y el "
               "ordenador <b>no juega al mahjong</b>: sus trece fichas están "
               "escritas en el cartucho a una de completarse, y la que suelta la "
               "<b>sortea del muro</b> y luego la filtra para que parezca un "
               "descarte humano. Hasta el hueco vacío de su mano boca abajo es "
               "teatro.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(15432, i)} of code, {cif(17336, i)} of data "
                          f"&middot; {cif(1091, i)} labels &middot; commented "
                          f"to <b>30.7%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(15432, i)} de código, {cif(17336, i)} de datos "
                          f"&middot; {cif(1091, i)} etiquetas &middot; comentado "
                          f"al <b>30,7 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hyperolympic1",
        grupo="konami",
        titulo="Hyper Olympic 1",
        anio=1984,
        repo="https://github.com/antxiko/HyperOlympic1-disassembly",
        web="https://antxiko.github.io/HyperOlympic1-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-710",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-710",
        ),
        claim=dict(
            en="Almost nothing here is drawn: the screens are scripts that get "
               "interpreted, and the large letters are manufactured by "
               "stretching the small ones. The 400 metres does not exist in the "
               "arcade &mdash; it is the 100 metres label with <b>one glyph "
               "changed</b>. And the stopwatch was worked out for 60 Hz, so in "
               "Europe a &laquo;12.00&raquo; is really 14.4 seconds.",
            es="Aquí casi nada está dibujado: las pantallas son guiones que se "
               "interpretan, y las letras grandes se fabrican estirando las "
               "pequeñas. Los 400 metros no existen en el arcade &mdash;son el "
               "rótulo de los 100 con <b>un glifo cambiado</b>&mdash;. Y el "
               "cronómetro está calculado para 60 Hz, así que en Europa un "
               "&laquo;12,00&raquo; son 14,4 segundos de verdad.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9335, i)} of code, {cif(7049, i)} of data "
                          f"&middot; {cif(569, i)} labels &middot; commented "
                          f"to <b>33.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9335, i)} de código, {cif(7049, i)} de datos "
                          f"&middot; {cif(569, i)} etiquetas &middot; comentado "
                          f"al <b>33,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hyperolympic2",
        grupo="konami",
        titulo="Hyper Olympic 2",
        anio=1984,
        repo="https://github.com/antxiko/HyperOlympic2-disassembly",
        web="https://antxiko.github.io/HyperOlympic2-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-711",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-711",
        ),
        claim=dict(
            en="Four new events on the previous cartridge&rsquo;s program: "
               "<b>83.4 % of its instructions are here</b>, and the motor that "
               "span the hammer over there is the one that lifts the high "
               "jumper. What belongs to this one fits in 1,519 bytes &mdash; "
               "and in the first event&rsquo;s label, which reads <b>110 "
               "HURDLERS</b>, with the typo written into the ROM.",
            es="Cuatro pruebas nuevas sobre el programa del cartucho anterior: "
               "<b>el 83,4 % de sus instrucciones están aquí</b>, y el motor "
               "que allí hacía girar el martillo es el que aquí levanta al "
               "saltador de altura. Lo propio de éste cabe en 1.519 bytes "
               "&mdash;y en el rótulo de la primera prueba, que dice <b>110 "
               "HURDLERS</b>, con la errata escrita en la ROM.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9872, i)} of code, {cif(6512, i)} of data "
                          f"&middot; {cif(647, i)} labels &middot; commented "
                          f"to <b>29.9%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9872, i)} de código, {cif(6512, i)} de datos "
                          f"&middot; {cif(647, i)} etiquetas &middot; comentado "
                          f"al <b>29,9 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="holeinone",
        grupo="msx-exclusive",
        titulo="Hole in One",
        anio=1984,
        repo="https://github.com/antxiko/HoleInOne-disassembly",
        web="https://antxiko.github.io/HoleInOne-disassembly/",
        meta=dict(
            en="HAL Laboratory &middot; MSX &middot; 16 KB cartridge",
            es="HAL Laboratory &middot; MSX &middot; cartucho de 16 KB",
        ),
        claim=dict(
            en="An eighteen-hole course, par 72 and 6,430 metres, in 16 KB: a "
               "hole fits in three hundred bytes because <b>its header is its "
               "palette</b> &mdash; the table starts three bytes early so the "
               "opcode&rsquo;s own nibble lands on it. The cartridge builds "
               "<b>three trigonometry tables in RAM</b> at boot, and the "
               "wordmark loads by <b>calling into the middle of an "
               "instruction</b>, where the operand runs as <code>xor a</code>.",
            es="Un campo de dieciocho hoyos, par 72 y 6.430 metros, en 16 KB: "
               "un hoyo cabe en trescientos bytes porque <b>su cabecera es su "
               "paleta</b> &mdash;la tabla empieza tres bytes antes para que el "
               "nibble del propio opcode caiga encima&mdash;. El cartucho monta "
               "<b>tres tablas de trigonometria en RAM</b> al arrancar, y el "
               "rotulo se carga <b>llamando a mitad de una instruccion</b>, "
               "donde el operando se ejecuta como <code>xor a</code>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(6065, i)} of code, {cif(10319, i)} of data "
                          f"&middot; {cif(358, i)} routines &middot; commented "
                          f"to <b>41.9%</b>, none below 10%"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6065, i)} de codigo, {cif(10319, i)} de datos "
                          f"&middot; {cif(358, i)} rutinas &middot; comentado al "
                          f"<b>41,9 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="casioworldopen",
        grupo="msx-exclusive",
        titulo="Casio World Open",
        anio=1985,
        repo="https://github.com/antxiko/CasioWorldOpen-disassembly",
        web="https://antxiko.github.io/CasioWorldOpen-disassembly/",
        meta=dict(
            en="Casio &middot; MSX &middot; 32 KB cartridge",
            es="Casio &middot; MSX &middot; cartucho de 32 KB",
        ),
        claim=dict(
            en="Eighteen holes stored as <b>ten layouts</b>: eight of them are "
               "used twice, once mirrored, and the flag is bit 7 of the same "
               "byte whose low nibble is the par. What look like sprites are "
               "not &mdash; the VDP only ever holds ten, five of them the ball "
               "at five sizes; everything else is tile indices, decompressed, "
               "spread apart and then <b>running-summed in 16 bits</b>.",
            es="Dieciocho hoyos guardados como <b>diez trazados</b>: ocho se "
               "usan dos veces, uno de ellos espejado, y la marca es el bit 7 "
               "del mismo byte cuyo nibble bajo es el par. Lo que parecen "
               "sprites no lo son &mdash;del VDP solo hay diez, y cinco son la "
               "bola a cinco tamanos&mdash;: todo lo demas son indices de tile, "
               "descomprimidos, separados y luego <b>sumados en cadena a 16 "
               "bits</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8185, i)} of code, {cif(24583, i)} of data "
                          f"&middot; {cif(435, i)} routines &middot; commented "
                          f"to <b>37.0%</b>, none below 10%"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8185, i)} de codigo, {cif(24583, i)} de datos "
                          f"&middot; {cif(435, i)} rutinas &middot; comentado al "
                          f"<b>37,0 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(
            en="its title screen is drawn without its text, and that is not a "
               "bug: the text comes from the machine's own font",
            es="su pantalla de titulo sale sin el texto, y no es un fallo: el "
               "texto lo pone la fuente de la propia maquina",
        ),
    ),
    dict(
        clave="hyperrally",
        grupo="konami",
        titulo="Hyper Rally",
        anio=1985,
        repo="https://github.com/antxiko/HyperRally-disassembly",
        web="https://antxiko.github.io/HyperRally-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-718",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-718",
        ),
        claim=dict(
            en="The road is pseudo-3D with no 3D: each strip is picked from a "
               "table of shapes indexed by the curve ahead. And hidden at the "
               "tail of the ROM, in katakana, is Konami&rsquo;s house mark "
               "&mdash; <b>RC-718</b> &mdash; the signature Manuel Pazos found.",
            es="La carretera es pseudo-3D sin 3D: cada franja se saca de una "
               "tabla de formas indexada por la curva que viene. Y escondida al "
               "final de la ROM, en katakana, está la marca de la casa de Konami "
               "&mdash; <b>RC-718</b> &mdash;, la firma que encontró Manuel Pazos.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(6464, i)} of code, {cif(9920, i)} of data "
                          f"&middot; {cif(431, i)} labels &middot; commented "
                          f"to <b>22.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6464, i)} de código, {cif(9920, i)} de datos "
                          f"&middot; {cif(431, i)} etiquetas &middot; comentado "
                          f"al <b>22,1 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="skyjaguar",
        grupo="konami",
        titulo="Sky Jaguar",
        anio=1984,
        repo="https://github.com/antxiko/SkyJaguar-disassembly",
        web="https://antxiko.github.io/SkyJaguar-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-721",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-721",
        ),
        claim=dict(
            en="There are no levels: one <b>1,920-row</b> stage that repeats. "
               "And the fine scroll is not computed but <b>stored</b> &mdash; "
               "every landscape strip is kept in eight versions, the same one "
               "started zero to seven rows lower. The giant enemy has no body "
               "sprites either: the background draws it.",
            es="No hay niveles: una sola fase de <b>1.920 filas</b> que se "
               "repite. Y el desplazamiento fino no se calcula, está "
               "<b>guardado</b> &mdash; cada tira del paisaje se guarda en ocho "
               "versiones, la misma empezada de cero a siete filas más abajo. Al "
               "enemigo gigante tampoco le dibujan sprites el cuerpo: se lo "
               "pinta el fondo.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7086, i)} of code, {cif(9298, i)} of data "
                          f"&middot; {cif(464, i)} labels &middot; commented "
                          f"to <b>32.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7086, i)} de código, {cif(9298, i)} de datos "
                          f"&middot; {cif(464, i)} etiquetas &middot; comentado "
                          f"al <b>32,1 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="golf",
        grupo="konami",
        titulo="Konami's Golf",
        anio=1985,
        repo="https://github.com/antxiko/KonamisGolf-disassembly",
        web="https://antxiko.github.io/KonamisGolf-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-723",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-723",
        ),
        claim=dict(
            en="Nine holes in 16 KB, and every one of them stored <b>once</b>: "
               "the same bytes are read as a VRAM script to paint the plan view "
               "and as data to build the grid that knows fairway from bunker. "
               "The wind is rolled from <b>the memory refresh register</b>, and "
               "the ball&rsquo;s height is never stored anywhere &mdash; it is "
               "the gap between its two sprites.",
            es="Nueve hoyos en 16 KB, y cada uno guardado <b>una sola vez</b>: "
               "los mismos bytes se leen como guion de VRAM para pintar el plano "
               "y como datos para armar la rejilla que sabe dónde está la calle "
               "y dónde el búnker. El viento se sortea con <b>el registro de "
               "refresco de la memoria</b>, y la altura de la bola no se guarda "
               "en ninguna parte &mdash; es la distancia entre sus dos sprites.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8665, i)} of code, {cif(7719, i)} of data "
                          f"&middot; {cif(558, i)} labels &middot; commented "
                          f"to <b>35.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8665, i)} de código, {cif(7719, i)} de datos "
                          f"&middot; {cif(558, i)} etiquetas &middot; comentado "
                          f"al <b>35,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="mopiranger",
        grupo="konami",
        titulo="Mopi Ranger",
        anio=1985,
        repo="https://github.com/antxiko/MopiRanger-disassembly",
        web="https://antxiko.github.io/MopiRanger-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-728",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-728",
        ),
        claim=dict(
            en="The house&rsquo;s secret bonus &mdash;<b>5730 points</b>, which "
               "read <i>go-na-mi</i> in Japanese&mdash;, an attract mode that "
               "is not AI but a <b>recorded game of 77 keypresses</b>, and a "
               "game that keeps <b>no collision map</b>: it reads the screen "
               "to find out where you can walk.",
            es="El premio secreto de la casa &mdash;<b>5730 puntos</b>, que en "
               "japonés se leen <i>go-na-mi</i>&mdash;, una demostración que "
               "no es inteligencia sino una <b>partida grabada de 77 "
               "pulsaciones</b>, y un juego que <b>no guarda mapa de "
               "colisiones</b>: lee la pantalla para saber por dónde se puede "
               "pasar.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7789, i)} of code, {cif(8595, i)} of data "
                          f"&middot; {cif(512, i)} labels &middot; commented "
                          f"to <b>52.9%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7789, i)} de código, {cif(8595, i)} de datos "
                          f"&middot; {cif(512, i)} etiquetas &middot; comentado "
                          f"al <b>52,9 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="roadfighter",
        grupo="konami",
        titulo="Road Fighter",
        anio=1985,
        repo="https://github.com/antxiko/RoadFighter-disassembly",
        web="https://antxiko.github.io/RoadFighter-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-730",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-730",
        ),
        claim=dict(
            en="A game that stores <b>nowhere</b> where the road is &mdash;it "
               "reads it off the screen&mdash;, a routine <b>hidden inside "
               "its own pointer table</b>, and two builds that differ by a "
               "<b>single byte</b>.",
            es="Un juego que <b>no guarda</b> por dónde va la carretera "
               "&mdash;la lee de la pantalla&mdash;, una rutina <b>escondida "
               "dentro de su propia tabla de punteros</b>, y dos "
               "compilaciones que se diferencian en <b>un solo byte</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7797, i)} of code, {cif(8587, i)} of data "
                          f"&middot; {cif(482, i)} labels &middot; commented "
                          f"to <b>55.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7797, i)} de código, {cif(8587, i)} de datos "
                          f"&middot; {cif(482, i)} etiquetas &middot; comentado "
                          f"al <b>55,1 %</b>"),
        ),
        nota=dict(
            en=None,
            es=None,
        ),
    ),
    dict(
        clave="pingpong",
        grupo="konami",
        titulo="Konami's Ping Pong",
        anio=1985,
        repo="https://github.com/antxiko/KonamisPingPong-disassembly",
        web="https://antxiko.github.io/KonamisPingPong-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-731",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-731",
        ),
        claim=dict(
            en="A table whose right half is <b>not stored anywhere</b> "
               "&mdash;it is drawn by mirroring the left one byte by "
               "byte&mdash;, forty frames each carrying <b>the pointer to its "
               "own patterns</b> right behind it, and the whole of table "
               "tennis scoring written <b>in BCD</b>.",
            es="Una mesa cuya mitad derecha <b>no está guardada</b> &mdash;se "
               "dibuja reflejando la izquierda byte a byte&mdash;, cuarenta "
               "fotogramas que llevan pegado detrás <b>el puntero a sus "
               "propios patrones</b>, y el reglamento del tenis de mesa "
               "entero escrito <b>en BCD</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7676, i)} of code, {cif(8708, i)} of data "
                          f"&middot; {cif(548, i)} labels &middot; commented "
                          f"to <b>64.3%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7676, i)} de código, {cif(8708, i)} de datos "
                          f"&middot; {cif(548, i)} etiquetas &middot; comentado "
                          f"al <b>64,3 %</b>"),
        ),
        nota=dict(
            en="The densest listing in the series.",
            es="El listado más denso de la serie.",
        ),
    ),
    dict(
        clave="soccer",
        grupo="konami",
        titulo="Konami&rsquo;s Soccer",
        anio=1985,
        repo="https://github.com/antxiko/KonamisSoccer-disassembly",
        web="https://antxiko.github.io/KonamisSoccer-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-732",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-732",
        ),
        claim=dict(
            en="A 1985 football game that <b>calls offside</b> &mdash;and only "
               "from level 3 up against the machine&mdash;, twelve players "
               "that are <b>not sprites but 3x3 tile patches</b> over an "
               "eighty-column pitch held in RAM, and an aim that is never "
               "computed: it is <b>looked up in two tables</b>.",
            es="Un fútbol de 1985 que <b>pita el fuera de juego</b> &mdash;y "
               "sólo del nivel 3 en adelante contra la máquina&mdash;, doce "
               "jugadores que <b>no son sprites sino parches de 3x3 "
               "casillas</b> sobre un campo de ochenta columnas guardado en la "
               "RAM, y una puntería que no se calcula: <b>se consulta en dos "
               "tablas</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(20116, i)} of code, {cif(12652, i)} of data "
                          f"&middot; {cif(1213, i)} labels &middot; commented "
                          f"to <b>36.5%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(20116, i)} de código, {cif(12652, i)} de datos "
                          f"&middot; {cif(1213, i)} etiquetas &middot; comentado "
                          f"al <b>36,5 %</b>"),
        ),
        nota=dict(
            en="The same cartridge also came out as <b>Konami&rsquo;s "
               "Football</b>: <b>one instruction out of 9,755</b> differs.",
            es="El mismo cartucho salió también como <b>Konami&rsquo;s "
               "Football</b>: cambia <b>una instrucción de 9.755</b>.",
        ),
    ),
    dict(
        clave="kingsvalley",
        grupo="konami",
        titulo="King's Valley",
        anio=1985,
        repo="https://github.com/antxiko/KingsValley-disassembly",
        web="https://antxiko.github.io/KingsValley-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-727",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-727",
        ),
        claim=dict(
            en="The colour table kept <b>underneath</b> the pattern table, "
               "the explorer&rsquo;s position in <b>twenty-four bits</b>, and "
               "<b>eighty-seven bytes of code</b> hidden behind a "
               "<code>push</code>. Sprite flicker is shared out on purpose, "
               "and the stone changes colour every four rooms.",
            es="La tabla de colores <b>debajo</b> de la de patrones, la "
               "posición del explorador en <b>veinticuatro bits</b>, y "
               "<b>ochenta y siete bytes de código</b> escondidos detrás de "
               "un <code>push</code>. El parpadeo de los sprites está "
               "repartido a propósito, y la piedra cambia de color cada "
               "cuatro salas.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9803, i)} of code, {cif(6581, i)} of data "
                          f"&middot; {cif(651, i)} labels &middot; commented "
                          f"to <b>45.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9803, i)} de código, {cif(6581, i)} de datos "
                          f"&middot; {cif(651, i)} etiquetas &middot; comentado "
                          f"al <b>45,5 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="baseball",
        grupo="konami",
        titulo="Konami's Baseball",
        anio=1984,
        repo="https://github.com/antxiko/KonamisBaseball-disassembly",
        web="https://antxiko.github.io/KonamisBaseball-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-724",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-724",
        ),
        claim=dict(
            en="The script&rsquo;s address written <b>behind the CALL "
               "itself</b>, the <b>twelve teams</b> of the 1984 Japanese "
               "league hidden in twelve letters, and a computer opponent that "
               "plays by <b>writing into the joystick slot</b>. The menu demo "
               "plays itself, and it is silent on purpose.",
            es="La dirección del guion escrita <b>detrás del propio CALL</b>, "
               "los <b>doce equipos</b> de la liga japonesa de 1984 "
               "escondidos en doce letras, y una máquina que juega "
               "<b>escribiendo en el hueco del mando</b>. La demostración del "
               "menú se juega sola, y es muda a propósito.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9618, i)} of code, {cif(6766, i)} of data "
                          f"&middot; {cif(629, i)} labels &middot; commented "
                          f"to <b>44.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9618, i)} de código, {cif(6766, i)} de datos "
                          f"&middot; {cif(629, i)} etiquetas &middot; comentado "
                          f"al <b>44,5 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="yiearkungfu",
        grupo="konami",
        titulo="Yie Ar Kung-Fu",
        anio=1985,
        repo="https://github.com/antxiko/YieArKungFu-disassembly",
        web="https://antxiko.github.io/YieArKungFu-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-725",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-725",
        ),
        claim=dict(
            en="The cartridge&rsquo;s <b>two builds</b> collated instruction "
               "by instruction: 95% of their bytes differ and <b>97% of their "
               "instructions match</b>. What actually changes is a mask that "
               "the hard one makes <b>depend on the level</b> &mdash; and the "
               "fact that only that one carries Konami&rsquo;s hidden mark.",
            es="Las <b>dos compilaciones</b> del cartucho cotejadas "
               "instrucción a instrucción: difieren en el 95 % de los bytes y "
               "coinciden en el <b>97 % de las instrucciones</b>. Lo que "
               "cambia de verdad es una máscara que la difícil hace "
               "<b>depender del nivel</b> &mdash;y que solo esa lleva la "
               "marca oculta de Konami.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7494, i)} of code, {cif(8890, i)} of data "
                          f"&middot; {cif(569, i)} labels &middot; commented "
                          f"to <b>44.0%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7494, i)} de código, {cif(8890, i)} de datos "
                          f"&middot; {cif(569, i)} etiquetas &middot; comentado "
                          f"al <b>44,0 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="tennis",
        grupo="konami",
        titulo="Konami's Tennis",
        anio=1984,
        repo="https://github.com/antxiko/KonamisTennis-disassembly",
        web="https://antxiko.github.io/KonamisTennis-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-720",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-720",
        ),
        claim=dict(
            en="The screen&rsquo;s three thirds painted with <b>a single "
               "loop that reads its own output</b>, the colour table kept "
               "<b>underneath</b> the pattern table, and every player built "
               "from <b>five stacked sprites</b>. The chair umpire has three "
               "faces so he can follow the ball with his eyes.",
            es="Los tres tercios de la pantalla pintados con <b>un solo "
               "bucle que se lee a sí mismo</b>, la tabla de colores "
               "<b>debajo</b> de la de patrones, y cada tenista montado con "
               "<b>cinco sprites apilados</b>. El juez de silla tiene tres "
               "caras para seguir la pelota con los ojos.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7882, i)} of code, {cif(8502, i)} of data "
                          f"&middot; {cif(492, i)} labels &middot; commented "
                          f"to <b>32.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7882, i)} de código, {cif(8502, i)} de datos "
                          f"&middot; {cif(492, i)} etiquetas &middot; comentado "
                          f"al <b>32,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hypersports1",
        grupo="konami",
        titulo="Hyper Sports 1",
        anio=1984,
        repo="https://github.com/antxiko/HyperSports1-disassembly",
        web="https://antxiko.github.io/HyperSports1-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-715",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-715",
        ),
        claim=dict(
            en="Its four events are written into the ROM as plain text &mdash; "
               "DIVING, TRAMPOLINE, LONG HORSE, HORIZONTAL BAR &mdash; and two "
               "players take turns by swapping the whole block of state. Unlike "
               "its Hyper Olympic siblings, it carries <b>no hidden Konami mark</b>.",
            es="Sus cuatro pruebas están escritas en la ROM como texto llano "
               "&mdash; DIVING, TRAMPOLINE, LONG HORSE, HORIZONTAL BAR &mdash; y "
               "dos jugadores se turnan intercambiando el bloque entero de estado. "
               "A diferencia de sus hermanos Hyper Olympic, <b>no lleva marca "
               "oculta de Konami</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(5953, i)} of code, {cif(10431, i)} of data "
                          f"&middot; {cif(387, i)} labels &middot; commented "
                          f"to <b>24.8%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5953, i)} de código, {cif(10431, i)} de datos "
                          f"&middot; {cif(387, i)} etiquetas &middot; comentado "
                          f"al <b>24,8 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hypersports2",
        grupo="konami",
        titulo="Hyper Sports 2",
        anio=1984,
        repo="https://github.com/antxiko/HyperSports2-disassembly",
        web="https://antxiko.github.io/HyperSports2-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-717",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-717",
        ),
        claim=dict(
            en="Skeet shooting, archery and weight lifting. The bow scores with "
               "<b>Pythagoras and no square root</b>, against ring radii already "
               "squared; the clays are not random but read bit by bit from two "
               "tables; and a lift is good only when <b>three judges&rsquo; "
               "lights</b> come on, one every 0x20 frames.",
            es="Tiro al plato, tiro con arco y halterofilia. El arco acierta con "
               "<b>Pitágoras y sin raíz cuadrada</b>, contra radios de anillo ya "
               "elevados al cuadrado; los platos no salen al azar, sino leídos "
               "bit a bit de dos tablas; y un levantamiento solo vale cuando se "
               "encienden <b>las tres luces del jurado</b>, una cada 0x20 cuadros.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(6956, i)} of code, {cif(9428, i)} of data "
                          f"&middot; {cif(314, i)} labels &middot; commented "
                          f"to <b>22.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6956, i)} de código, {cif(9428, i)} de datos "
                          f"&middot; {cif(314, i)} etiquetas &middot; comentado "
                          f"al <b>22,5 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="cabbagepatch",
        grupo="konami",
        titulo="Cabbage Patch Kids",
        anio=1984,
        repo="https://github.com/antxiko/CabbagePatchKids-disassembly",
        web="https://antxiko.github.io/CabbagePatchKids-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-716",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-716",
        ),
        claim=dict(
            en="Before you play, it asks you two things: <b>which kid you want "
               "and what it is called</b> &mdash; ten letters that come out of "
               "the factory saying ANNA LEE, written in next to the three lives. "
               "It is another Konami cartridge recompiled, and it still carries "
               "<b>439 bytes of that game's scenery that nothing here reads</b>.",
            es="Antes de jugar te hace dos preguntas: <b>qué muñeco quieres y "
               "cómo se llama</b> &mdash;diez letras que de fábrica dicen ANNA "
               "LEE, escritas junto a las tres vidas&mdash;. Es otro cartucho de "
               "Konami recompilado, y todavía arrastra <b>439 bytes de decorado "
               "suyo que aquí no lee nadie</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7981, i)} of code, {cif(8403, i)} of data "
                          f"&middot; {cif(314, i)} labels &middot; commented "
                          f"to <b>24.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7981, i)} de código, {cif(8403, i)} de datos "
                          f"&middot; {cif(314, i)} etiquetas &middot; comentado "
                          f"al <b>24,5 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="pitfall",
        grupo="ports",
        titulo="Pitfall!",
        anio=1984,
        repo="https://github.com/antxiko/Pitfall-MSX-disassembly",
        web="https://antxiko.github.io/Pitfall-MSX-disassembly/",
        meta=dict(
            en="Activision &middot; MSX &middot; 16 KB cartridge",
            es="Activision &middot; MSX &middot; cartucho de 16 KB",
        ),
        claim=dict(
            en="There is no map inside: the jungle's 255 screens come out of an "
               "eight-bit shift register, and the 32 treasures are exactly the 32 "
               "scenes of one kind. The vine is drawn frame by frame onto a bitmap "
               "in RAM, so the rope you see is arithmetic, not a graphic.",
            es="Dentro no hay ni un mapa guardado: las 255 pantallas de la selva "
               "salen de un registro de desplazamiento de ocho bits, y los 32 "
               "tesoros son exactamente las 32 escenas de un tipo. La liana se "
               "dibuja fotograma a fotograma en un bitmap en RAM: la cuerda que se "
               "ve es aritmética, no un gráfico.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9467, i)} of code, {cif(6917, i)} of data "
                          f"&middot; {cif(337, i)} labels"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9467, i)} de código, {cif(6917, i)} de datos "
                          f"&middot; {cif(337, i)} etiquetas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="pippols",
        grupo="konami",
        titulo="Pippols",
        anio=1985,
        repo="https://github.com/antxiko/Pippols-disassembly",
        web="https://antxiko.github.io/Pippols-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-729",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-729",
        ),
        claim=dict(
            en="It scrolls one pixel at a time in a video mode with no scroll "
               "register: the background sits in video memory eight times over, "
               "each copy a pixel lower, and the whole screen is rewritten every "
               "frame. That costs three quarters of the machine's time, measured "
               "in the emulator, and the road of every stage fits in 328 bytes.",
            es="Se desplaza de pixel en pixel en un modo de vídeo que no tiene "
               "registro de desplazamiento: el fondo está ocho veces en la memoria "
               "de vídeo, cada copia bajada un pixel más, y la pantalla entera se "
               "reescribe cada fotograma. Eso cuesta tres cuartas partes del tiempo "
               "de la máquina, medido en el emulador, y el camino de todas las "
               "fases cabe en 328 bytes.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(9099, i)} of code, {cif(7285, i)} of data "
                          f"&middot; {cif(676, i)} labels"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9099, i)} de código, {cif(7285, i)} de datos "
                          f"&middot; {cif(676, i)} etiquetas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="demonia",
        grupo="msx-exclusive",
        titulo="Demonia",
        anio=1986,
        repo="https://github.com/antxiko/Demonia-disassembly",
        web="https://antxiko.github.io/Demonia-disassembly/",
        meta=dict(
            en="Microids &middot; MSX &middot; 58,334-byte cassette",
            es="Microids &middot; MSX &middot; cinta de 58.334 bytes",
        ),
        claim=dict(
            en="It does not fit in the RAM an MSX booted into BASIC can see, so "
               "it hides twenty-six kilobytes underneath the BASIC ROM. And "
               "riding inside it, a 1984 machine code monitor by the same "
               "author: its back door still wired to CTRL+STOP, its command "
               "table buried under the game&rsquo;s own screen records, and in "
               "the single-step buffer the last instruction it ever ran before "
               "someone saved the tape.",
            es="No cabe en la RAM que ve un MSX arrancado desde BASIC, así que "
               "esconde veintiséis kilobytes debajo de la ROM del BASIC. Y "
               "dentro viaja, de polizón, un monitor de código máquina de 1984 "
               "del mismo autor: con su puerta trasera todavía enchufada al "
               "CTRL+STOP, sus órdenes tapadas por las fichas de pantalla del "
               "juego, y en el búfer del paso a paso la última instrucción que "
               "ejecutó antes de que alguien grabara la cinta.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(58334, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(20299, i)} of code, {cif(37597, i)} of data "
                          f"&middot; {cif(1586, i)} labels &middot; commented at "
                          f"<b>33.0%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(58334, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(20299, i)} de código, {cif(37597, i)} de datos "
                          f"&middot; {cif(1586, i)} etiquetas &middot; comentado "
                          f"al <b>33,0 %</b>, ninguna rutina por debajo del 10 %"),
        ),
        nota=dict(
            en="The 26 screens on its site are not screenshots: they are drawn "
               "from the tape&rsquo;s own bytes.",
            es="Las 26 pantallas de su web no son capturas: están dibujadas "
               "desde los propios bytes de la cinta.",
        ),
    ),
    dict(
        clave="nemesis",
        grupo="konami",
        titulo="Nemesis / Gradius",
        anio=1986,
        repo="https://github.com/antxiko/Nemesis-disassembly",
        web="https://antxiko.github.io/Nemesis-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB MegaROM &middot; RC-742",
            es="Konami &middot; MSX &middot; MegaROM de 128 KB &middot; RC-742",
        ),
        claim=dict(
            en="Twelve stages of Gradius in a 128 KB MegaROM, and the terrain is "
               "not in video memory: it is <b>22 rows of 32 cells in RAM</b>, "
               "shifted one column left by hand every scroll step with 22 "
               "<code>ldir</code>s. That is what lets the twelve maps on the site "
               "be <b>drawn from the ROM</b> and checked against the cartridge "
               "running. There is no random generator anywhere in the 128 KB: "
               "the stars, the falling rocks and the out-of-step blinking all "
               "come out of <b>the Z80&rsquo;s R register</b>.",
            es="Doce fases de Gradius en un MegaROM de 128 KB, y el terreno no "
               "está en la memoria de vídeo: son <b>22 filas de 32 casillas en la "
               "RAM</b>, que se corren una columna a la izquierda a mano en cada "
               "paso de scroll con 22 <code>ldir</code>. Eso es lo que permite que "
               "los doce mapas de la web estén <b>dibujados desde la ROM</b> y "
               "comprobados contra el cartucho corriendo. En los 128 KB no hay ni "
               "un generador de azar: las estrellas, la lluvia de piedras y el "
               "parpadeo a destiempo salen todos del <b>registro R del Z80</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(25471, i)} of code, {cif(105601, i)} of data "
                          f"&middot; {cif(916, i)} routines &middot; commented "
                          f"to <b>23.3%</b> &middot; <b>12</b> maps"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(25471, i)} de código, {cif(105601, i)} de datos "
                          f"&middot; {cif(916, i)} rutinas &middot; comentado "
                          f"al <b>23,3 %</b> &middot; <b>12</b> mapas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="f1spirit",
        grupo="konami",
        titulo="F-1 Spirit &mdash; The Way to Formula 1",
        anio=1987,
        terminado=False,
        repo="https://github.com/antxiko/F1Spirit-disassembly",
        web="https://antxiko.github.io/F1Spirit-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB MegaROM &middot; RC-752",
            es="Konami &middot; MSX &middot; MegaROM de 128 KB &middot; RC-752",
        ),
        claim=dict(
            en="The first MegaROM in this series, with the Konami SCC mapper and "
               "the SCC sound chip: sixteen 8 KB pages the game swaps in and out, "
               "so there is not one listing but sixteen. The depth of the road is "
               "not perspective: SCREEN 2 keeps three pattern banks, one per third "
               "of the screen, and the cartridge loads <b>different drawings under "
               "the same index</b> at the top and at the bottom. And its 21 "
               "circuits are lists of pieces that can be rewritten &mdash; there is "
               "an editor to do it, and it runs in the browser.",
            es="El primer MegaROM de la serie, con mapper Konami SCC y chip de "
               "sonido SCC: dieciséis páginas de 8 KB que el juego va metiendo y "
               "sacando, así que aquí no hay un listado sino dieciséis. La "
               "profundidad de la carretera no es perspectiva: en SCREEN 2 hay tres "
               "bancos de patrones, uno por tercio de pantalla, y el cartucho carga "
               "<b>dibujos distintos bajo el mismo índice</b> arriba y abajo. Y sus "
               "21 circuitos son listas de piezas que se pueden reescribir: hay un "
               "editor para hacerlo, y funciona en el navegador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>99.6%</b> explained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(31591, i)} of code, {cif(99481, i)} of data "
                          f"&middot; {cif(977, i)} routines &middot; "
                          f"<b>21</b> circuits"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>99,6 %</b> explicado "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(31591, i)} de código, {cif(99481, i)} de datos "
                          f"&middot; {cif(977, i)} rutinas &middot; "
                          f"<b>21</b> circuitos"),
        ),
        nota=dict(
            en="in progress: 504 bytes (0.4%) are still marked as pending to "
               "trace. The six code pages are commented, with no routine below "
               "the 10% line",
            es="en marcha: quedan 504 bytes (0,4 %) marcados como pendientes de "
               "trazar. Las seis páginas con código están comentadas, sin "
               "ninguna rutina por debajo del listón del 10 %",
        ),
    ),
    dict(
        clave="colt36",
        grupo="msx-exclusive",
        titulo="Colt 36",
        anio=1987,
        repo="https://github.com/antxiko/Colt36-disassembly",
        web="https://antxiko.github.io/Colt36-disassembly/",
        meta=dict(
            en="Topo Soft &middot; MSX &middot; cassette tape",
            es="Topo Soft &middot; MSX &middot; cinta de cassette",
        ),
        claim=dict(
            en="The game turned out to be written in BASIC: a tokenised MSX-BASIC "
               "program 63 lines long, with 45 bytes of Z80 at the end to start the "
               "interpreter, and a scrolling engine seventeen bytes long. Of the "
               "34,239 bytes on the tape there are 1,566 whose contents nobody has "
               "identified, published as a WANTED poster with every measurement "
               "next to it.",
            es="El juego resultó estar escrito en BASIC: un programa MSX-BASIC "
               "tokenizado de 63 líneas, con 45 bytes de Z80 al final para arrancar "
               "el intérprete, y un motor de scroll de diecisiete bytes. De los "
               "34.239 bytes de la cinta hay 1.566 cuyo contenido nadie ha "
               "identificado, publicados como un cartel de SE BUSCA con todas las "
               "medidas al lado.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(34239, i)} bytes &middot; <b>100%</b> accounted "
                          f"for &middot; reassembled and re-tokenised <b>byte for "
                          f"byte</b> &middot; only {cif(997, i)} bytes of machine "
                          f"code &middot; {cif(1566, i)} bytes unidentified"),
            es=lambda i: (f"{cif(34239, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; reensamblado y retokenizado <b>byte a byte</b> "
                          f"&middot; solo {cif(997, i)} bytes de código máquina "
                          f"&middot; {cif(1566, i)} bytes sin identificar"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="stardust",
        grupo="ports",
        titulo="Stardust",
        anio=1987,
        repo="https://github.com/antxiko/Stardust-MSX-disassembly",
        web="https://antxiko.github.io/Stardust-MSX-disassembly/",
        meta=dict(
            en="Topo Soft &middot; MSX &middot; cassette tape",
            es="Topo Soft &middot; MSX &middot; cinta de cassette",
        ),
        claim=dict(
            en="A ZX Spectrum conversion that brought the Spectrum's tape system "
               "across with it, not just the graphics: Spectrum blocks instead of "
               "the MSX's own, a loader that reimplements LD-BYTES with the same "
               "register interface, and RAM mapped into pages 1 and 2 to get the "
               "flat 48K the Spectrum has as standard. And it is multiload: two "
               "different programs on one cassette.",
            es="Una conversión del ZX Spectrum que se trajo el sistema de cinta del "
               "Spectrum, no solo los gráficos: bloques del Spectrum en vez de los "
               "del MSX, un cargador que reimplementa LD-BYTES con el mismo "
               "interfaz de registros, y RAM mapeada en las páginas 1 y 2 para "
               "tener los 48K planos que el Spectrum da de serie. Y es multicarga: "
               "dos programas distintos en un mismo cassette.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(93861, i)} bytes &middot; <b>100%</b> accounted "
                          f"for &middot; <b>five listings</b>, all <b>byte for "
                          f"byte</b> &middot; {cif(335, i)} routines commented"),
            es=lambda i: (f"{cif(93861, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; <b>cinco listados</b>, todos <b>byte a byte</b> "
                          f"&middot; {cif(335, i)} rutinas comentadas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="temptations",
        grupo="msx-exclusive",
        titulo="Temptations",
        anio=1988,
        repo="https://github.com/antxiko/temptations-disassembly",
        web="https://antxiko.github.io/temptations-disassembly/",
        meta=dict(
            en="Topo Soft &middot; MSX &middot; cassette tape",
            es="Topo Soft &middot; MSX &middot; cinta de cassette",
        ),
        claim=dict(
            en="The punishment for cheating never fires, and not because they meant "
               "it that way: they forgot to initialise the flag that triggers it, "
               "the only variable in the game that is read but never set. And the "
               "only published cheat for the game, from a 1988 book, has a typo "
               "&mdash; B4CC for 84CC &mdash; confirmed in an emulator.",
            es="El castigo por hacer trampas no salta nunca, y no porque lo "
               "quisieran así: se olvidaron de inicializar la bandera que lo "
               "dispara, la única variable del juego que se lee y nunca se escribe. "
               "Y el único truco publicado del juego, de un libro de 1988, tiene "
               "una errata &mdash;B4CC por 84CC&mdash; comprobada en el emulador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(40449, i)} bytes &middot; <b>100%</b> accounted "
                          f"for &middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(137, i)} routines, {cif(74, i)} data blocks "
                          f"&middot; {cif(29, i)} screens drawn from the binary"),
            es=lambda i: (f"{cif(40449, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(137, i)} rutinas, {cif(74, i)} bloques de datos "
                          f"&middot; {cif(29, i)} pantallas dibujadas desde el "
                          f"binario"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="alehop",
        grupo="msx-exclusive",
        titulo="Ale Hop!",
        anio=1988,
        repo="https://github.com/antxiko/AleHop-disassembly",
        web="https://antxiko.github.io/AleHop-disassembly/",
        meta=dict(
            en="Topo Soft &middot; MSX &middot; cassette tape",
            es="Topo Soft &middot; MSX &middot; cinta de cassette",
        ),
        claim=dict(
            en="The game loads on top of the ROM: all 42,645 bytes go into page 0, "
               "where the MSX BIOS lives, and the 35 KB of graphics and maps stay "
               "hidden underneath it, uncovered for an instant each time a level "
               "loads. That one decision is why this disassembly is several "
               "listings and not one. 135 bytes never execute.",
            es="El juego carga encima de la ROM: los 42.645 bytes van a la página "
               "0, donde vive la BIOS del MSX, y los 35 KB de gráficos y mapas se "
               "quedan escondidos debajo, al descubierto solo un instante cada vez "
               "que carga un nivel. Esa decisión es la razón de que este "
               "desensamblado sean varios listados y no uno. 135 bytes no se "
               "ejecutan nunca.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(42645, i)} bytes in the game block &middot; "
                          f"<b>0</b> unexplained &middot; the modules reassemble "
                          f"<b>byte for byte</b> and the rebuilt tape has the "
                          f"<b>same sha256</b> &middot; {cif(4588, i)} of code, "
                          f"{cif(38057, i)} of data"),
            es=lambda i: (f"{cif(42645, i)} bytes en el bloque del juego &middot; "
                          f"<b>0</b> sin explicar &middot; los módulos reensamblan "
                          f"<b>byte a byte</b> y la cinta regenerada tiene el "
                          f"<b>mismo sha256</b> &middot; {cif(4588, i)} de código, "
                          f"{cif(38057, i)} de datos"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="war",
        grupo="ports",
        titulo="War in Middle Earth",
        anio=1989,
        repo="https://github.com/antxiko/WarinMiddleEarth-MSX-disassembly",
        web="https://antxiko.github.io/WarinMiddleEarth-MSX-disassembly/",
        meta=dict(
            en="Melbourne House / Dro Soft &middot; MSX &middot; 62,261-byte cassette",
            es="Melbourne House / Dro Soft &middot; MSX &middot; cinta de 62.261 bytes",
        ),
        claim=dict(
            en="A ZX Spectrum conversion that brought the whole tape system across "
               "&mdash; Spectrum blocks, a hand-written LD-BYTES &mdash; along with "
               "the colour attribute glued behind every map tile, which is why they "
               "are nine bytes long and not eight. It even brought the beeper sound "
               "engine, and then nothing ever calls it: the four places that ask for "
               "a sound effect all land on a bare <code>ret</code>, and of the MSX&rsquo;s "
               "PSG only the two joystick registers are ever written. The game is "
               "silent.",
            es="Una conversión del ZX Spectrum que se trajo el sistema de cinta "
               "entero &mdash;bloques del Spectrum, un LD-BYTES escrito a mano&mdash; "
               "y el atributo de color pegado detrás de cada tile del mapa, que por "
               "eso ocupan nueve bytes y no ocho. Se trajo hasta el motor de sonido "
               "del altavoz, y luego no lo llama nadie: los cuatro sitios que piden "
               "un efecto acaban en un <code>ret</code> pelado, y del PSG del MSX "
               "solo se escriben los dos registros del joystick. El juego es mudo.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(62261, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; <b>five listings</b>, all <b>byte for byte</b> "
                          f"&middot; {cif(11814, i)} of code, {cif(50191, i)} of data "
                          f"&middot; {cif(819, i)} labels &middot; commented at "
                          f"<b>29.7%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(62261, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>cinco listados</b>, todos <b>byte a byte</b> "
                          f"&middot; {cif(11814, i)} de código, {cif(50191, i)} de datos "
                          f"&middot; {cif(819, i)} etiquetas &middot; comentado al "
                          f"<b>29,7 %</b>, ninguna rutina por debajo del 10 %"),
        ),
        nota=dict(
            en="the loading screen on its site is not a screenshot: it is drawn from "
               "the tape, credits and all",
            es="la pantalla de carga de su web no es una captura: está dibujada desde "
               "la cinta, con sus créditos y todo",
        ),
    ),
    dict(
        clave="descubrimiento",
        grupo="msx-exclusive",
        titulo="El Descubrimiento de América",
        anio=1987,
        repo="https://github.com/antxiko/Descubrimiento-disassembly",
        web="https://antxiko.github.io/Descubrimiento-disassembly/",
        meta=dict(
            en="Gema / OMK Software &middot; MSX &middot; 66,371-byte cassette",
            es="Gema / OMK Software &middot; MSX &middot; cinta de 66.371 bytes",
        ),
        claim=dict(
            en="The tape carries not one program but <b>two, and both live at "
               "the same addresses</b> &mdash; which is why this is five "
               "listings and not one. The BIOS never reads them: a "
               "<b>88-instruction loader</b> that outlives both halves pulls "
               "them off the tape by hand, and the two bytes at <b>0xD300 are "
               "not code but a pointer</b> back to it. The second half plays "
               "out inside a <b>128&times;52 tile cutaway of the caravel</b>, "
               "with the cargo you bought drawn stowed in the hold.",
            es="La cinta no trae un programa sino <b>dos, y los dos viven en "
               "las mismas direcciones</b> &mdash;por eso son cinco listados y "
               "no uno&mdash;. La BIOS no los lee: los saca de la cinta a mano "
               "un <b>cargador de 88 instrucciones</b> que sobrevive a las dos "
               "mitades, y los dos bytes de <b>0xD300 no son código sino un "
               "puntero</b> de vuelta a él. La segunda parte transcurre dentro "
               "de un <b>plano de la carabela de 128&times;52 baldosas</b>, "
               "con la carga que compraste dibujada estibada en la bodega.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(66016, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; <b>five listings</b>, the whole tape "
                          f"<b>byte for byte</b> &middot; {cif(15504, i)} of "
                          f"code, {cif(50512, i)} of data &middot; "
                          f"{cif(733, i)} labels &middot; commented at "
                          f"<b>26.7%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(66016, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>cinco listados</b>, la cinta entera "
                          f"<b>byte a byte</b> &middot; {cif(15504, i)} de "
                          f"código, {cif(50512, i)} de datos &middot; "
                          f"{cif(733, i)} etiquetas &middot; comentado al "
                          f"<b>26,7 %</b>, ninguna rutina por debajo del 10 %"),
        ),
        nota=dict(
            en="7,564 bytes on this tape are read by nobody: the tape records "
               "fixed-size blocks, so whatever was in memory got recorded "
               "behind the program.",
            es="7.564 bytes de esta cinta no los lee nadie: los bloques son de "
               "tamaño fijo, así que detrás del programa se grabó lo que "
               "hubiera en memoria.",
        ),
    ),
]

# Los desensamblados van en tres grupos, cada uno una parte de su seccion. Aqui
# esta el orden y el rotulo de cada grupo; a que grupo va cada juego lo dice el
# propio juego en 'grupo'. Un grupo que no este aqui, o que se quede sin juegos,
# para la generacion (ver comprueba()).
GRUPOS = [
    dict(id="konami", titulo=dict(en="Konami", es="Konami")),
    dict(id="msx-exclusive", titulo=dict(en="MSX Exclusive", es="Exclusivos de MSX")),
    dict(id="ports", titulo=dict(en="Ports", es="Conversiones")),
]


def del_grupo(gid):
    return [p for p in DESENSAMBLADOS if p.get("grupo") == gid]


def es_cinta(p):
    return "cinta" in p["meta"]["es"]


# LOS PARCHES. Otra clase de proyecto: aqui no se documenta un cartucho, se
# MODIFICA. Van en su propia seccion y NO cuentan en las cifras de la serie de
# desensamblados, que son de juegos desmontados.
PARCHES = [
    dict(
        clave="mahjong-en",
        titulo="Konami&rsquo;s Mahjong Dojo &mdash; English patch",
        anio=1984,
        repo="https://github.com/antxiko/KonamisMahjongDojo-ENPatch",
        web="https://antxiko.github.io/KonamisMahjongDojo-ENPatch/",
        meta=dict(
            en="Konami &middot; MSX &middot; RC-707 &middot; IPS patch, unofficial",
            es="Konami &middot; MSX &middot; RC-707 &middot; parche IPS, extraoficial",
        ),
        claim=dict(
            en="The cartridge is in Japanese, and so is the screen that tells you "
               "why you won. This puts every screen you have to read into English "
               "<b>without changing one instruction of the game</b> &mdash; and "
               "gives it the tutorial it never had: <b>twenty attract screens</b> "
               "with all thirty-four tiles drawn, hooked on with a single "
               "<code>jp</code>. The room came from a gap the cartridge leaves "
               "inside its own tiles, and the centre of the screen writes "
               "<b>two letters per character cell</b> to fit.",
            es="El cartucho está en japonés, y la pantalla que dice por qué has "
               "ganado también. Esto pasa al inglés todas las pantallas que hay "
               "que leer <b>sin cambiar ni una instrucción del juego</b> &mdash;y "
               "de paso le pone el tutorial que nunca tuvo: <b>veinte pantallas</b> "
               "en el modo attract con las treinta y cuatro fichas dibujadas, "
               "enganchadas con un solo <code>jp</code>&mdash;. El sitio salió del "
               "hueco que el cartucho deja dentro de sus propias fichas, y el "
               "centro de la pantalla escribe <b>dos letras por celda</b> para que "
               "quepa.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(11777, i)} bytes changed in <b>44</b> blocks "
                          f"&middot; <b>0</b> outside them &middot; "
                          f"{cif(12279, i)}-byte IPS &middot; <b>20</b> tutorial "
                          f"screens &middot; no ROM distributed"),
            es=lambda i: (f"{cif(11777, i)} bytes cambiados en <b>44</b> bloques "
                          f"&middot; <b>0</b> fuera de ellos &middot; IPS de "
                          f"{cif(12279, i)} bytes &middot; <b>20</b> pantallas de "
                          f"tutorial &middot; no se distribuye ninguna ROM"),
        ),
        nota=dict(
            en="work in progress: playable, but not finished",
            es="trabajo en curso: se juega, pero no está terminado",
        ),
    ),
    dict(
        clave="warinmiddleearth-patch",
        titulo="War in Middle Earth &mdash; Araubi&rsquo;s patch",
        anio=1989,
        repo="https://github.com/antxiko/WarinMiddleEarth-MSX-Patch",
        web="https://antxiko.github.io/WarinMiddleEarth-MSX-Patch/",
        meta=dict(
            en="Melbourne House / Dro Soft &middot; MSX &middot; tape &middot; "
               "IPS patch, unofficial",
            es="Melbourne House / Dro Soft &middot; MSX &middot; cinta &middot; "
               "parche IPS, extraoficial",
        ),
        claim=dict(
            en="Araubi asked for three things on the forum and four came out. The "
               "enemy was invisible because the loop that plants units on the map "
               "<b>stops one slot before the enemy side begins</b>; a unit&rsquo;s "
               "qualities were adjectives with no numbers; and the Ring&rsquo;s "
               "deadline &mdash;a countdown of months the game never shows&mdash; "
               "now sits beside the ring in the bearer&rsquo;s sheet. The enemy "
               "also got <b>the Eye of Sauron</b>, because a free bit in the map "
               "byte was all it took to tell the two sides apart. The new code "
               "lives inside the <b>ZX beeper engine this port brought across and "
               "never calls</b>.",
            es="Araubi pidió tres cosas en el foro y salieron cuatro. Las unidades "
               "enemigas no se veían porque el bucle que las siembra en el mapa "
               "<b>para una ranura antes de que empiece el bando enemigo</b>; las "
               "cualidades de una unidad eran adjetivos sin número; y el plazo del "
               "Anillo &mdash;una cuenta atrás de meses que el juego no enseña&mdash; "
               "sale ya al lado del anillo, en la ficha del portador. Las enemigas "
               "llevan además <b>el Ojo de Sauron</b>, porque bastaba un bit libre "
               "del byte de mapa para distinguir los dos bandos. El código nuevo "
               "vive dentro del <b>motor de altavoz del ZX que esta conversión "
               "trajo y no llama nadie</b>.",
        ),
        datos=dict(
            en=lambda i: ("<b>197</b> bytes changed in <b>7</b> places &middot; "
                          "<b>0</b> outside the table &middot; <b>0</b> shifted "
                          f"&middot; {cif(249, i)}-byte IPS &middot; no tape "
                          "distributed"),
            es=lambda i: ("<b>197</b> bytes cambiados en <b>7</b> sitios &middot; "
                          "<b>0</b> fuera de la tabla &middot; <b>0</b> desplazados "
                          f"&middot; IPS de {cif(249, i)} bytes &middot; no se "
                          "distribuye ninguna cinta"),
        ),
        nota=dict(
            en="playable, but nobody has finished a game with it yet",
            es="se juega, pero nadie ha terminado una partida con él",
        ),
    ),
]

# Las cuentas de la cabecera salen de la lista, no de escribirlas a mano: al
# anadir un proyecto se ponen al dia solas. Un proyecto lleva 'terminado=False'
# cuando no esta al 100 %, y 'web' a None cuando todavia no tiene sitio
# publicado. Ojo: 'nota' NO sirve para esto, porque la llevan tambien los
# terminados que tienen alguna pregunta abierta.
N_JUEGOS = len(DESENSAMBLADOS)
N_CINTAS = sum(1 for p in DESENSAMBLADOS if es_cinta(p))
N_CARTUCHOS = N_JUEGOS - N_CINTAS
N_TERMINADOS = sum(1 for p in DESENSAMBLADOS if p.get("terminado", True))
N_CON_WEB = sum(1 for p in DESENSAMBLADOS if p.get("web"))
ANIOS = "%d-%d" % (min(p["anio"] for p in DESENSAMBLADOS),
                   max(p["anio"] for p in DESENSAMBLADOS))

# Rotulo de cuenta de un grupo: '12 cartridges', '4 tapes' o, si hay de las dos
# clases, '3 games'. Sale de la lista, como las demas cuentas.
CUENTA = dict(
    en=dict(cinta=("tape", "tapes"), cartucho=("cartridge", "cartridges"),
            juego=("game", "games")),
    es=dict(cinta=("cinta", "cintas"), cartucho=("cartucho", "cartuchos"),
            juego=("juego", "juegos")),
)


def cuenta(proyectos, idioma):
    n = len(proyectos)
    cintas = sum(1 for p in proyectos if es_cinta(p))
    clase = "cinta" if cintas == n else "cartucho" if cintas == 0 else "juego"
    return f"{n} {CUENTA[idioma][clase][n != 1]}"


def html_cifras(idioma, t):
    return ('<div class="cifras">'
            + "".join(f'<div class="cifra"><b>{v}</b><span>{e}</span></div>'
                      for v, e in t["cifras"])
            + '</div>')


def html_metodo(idioma, t):
    return '<div class="n">' + "".join(f"<p>{x}</p>" for x in t["met"]) + '</div>'


# Las secciones de primer nivel. Una seccion lleva o bien solo 'proyectos' (una
# rejilla) o bien ademas 'partes': subsecciones con ancla y rotulo propio, cada
# una con sus 'proyectos' o con un 'html' (idioma, textos) -> html. La seccion
# gana entonces un menu propio para saltar entre partes.
CATEGORIAS = [
    dict(
        id="disassemblies",
        titulo=dict(en="The disassemblies", es="Los desensamblados"),
        menu=dict(en="Disassemblies", es="Desensamblados"),
        intro=dict(
            en=f"{N_JUEGOS} games for the MSX, {N_CINTAS} off cassette tapes "
               f"and {N_CARTUCHOS} off cartridges, taken apart byte by byte and "
               f"commented. {N_TERMINADOS} of them are finished: every byte "
               f"accounted for, and the source giving the original back byte for "
               f"byte. The ones still in progress say so.",
            es=f"{N_JUEGOS} juegos de MSX, {N_CINTAS} de cinta de cassette y "
               f"{N_CARTUCHOS} de cartucho, desmontados byte a byte y comentados. "
               f"{N_TERMINADOS} están terminados: cada byte explicado y el código "
               f"fuente devolviendo el original byte a byte. Los que siguen en "
               f"marcha lo dicen.",
        ),
        proyectos=DESENSAMBLADOS,
        partes=[
            dict(id="numbers",
                 titulo=dict(en="The series in numbers", es="La serie en cifras"),
                 html=html_cifras),
            *[dict(id=g["id"], titulo=g["titulo"], proyectos=del_grupo(g["id"]))
              for g in GRUPOS],
            dict(id="method",
                 titulo=dict(en="How they are made", es="Cómo están hechos"),
                 html=html_metodo),
        ],
    ),
    dict(
        id="patches",
        titulo=dict(en="The patches", es="Los parches"),
        menu=dict(en="Patches", es="Parches"),
        intro=dict(
            en="What comes after understanding a cartridge: changing it. Same "
               "rule as the disassemblies &mdash; the build has to prove that "
               "outside the blocks it declares, the ROM is identical to the "
               "original. What is distributed is the difference file, never a "
               "cartridge image.",
            es="Lo que viene después de entender un cartucho: cambiarlo. Con la "
               "misma regla que los desensamblados &mdash;la construcción tiene "
               "que demostrar que, fuera de los bloques que declara, la ROM es "
               "idéntica a la original&mdash;. Lo que se distribuye es el fichero "
               "de diferencias, nunca una imagen de cartucho.",
        ),
        proyectos=PARCHES,
    ),
    # Para anadir otra categoria: una lista de proyectos con estos mismos campos
    # y otra entrada aqui, con 'partes' si las necesita. El menu y las secciones
    # salen de esta lista.
]

TXT = dict(
    en=dict(
        titulo="antxiko &mdash; commented disassemblies of 8-bit games",
        claim="Old 8-bit binaries taken apart byte by byte and commented, with the "
              "tools to rebuild them: nothing gets claimed that the binary does not "
              "show, and the source has to give the original back, byte for byte. "
              f"Right now that means {N_JUEGOS} MSX games.",
        ficha=[f"<b>{N_JUEGOS}</b> games", f"<b>{ANIOS}</b>",
               "MSX",
               f"<b>{N_CINTAS}</b> tapes &middot; <b>{N_CARTUCHOS}</b> cartridges"],
        menu_gh="GitHub",
        otro=("es/", "En castellano"),
        cifras=[(str(N_JUEGOS), "games taken apart"),
                (str(N_TERMINADOS), "finished at 100%"),
                (str(N_CON_WEB), "with a website"),
                (str(N_CINTAS), "cassette tapes"),
                (str(N_CARTUCHOS), "cartridges"),
                ("3", "builds of Antarctic Adventure")],
        met=["Every project follows the same rule: nothing gets claimed that the "
             "binary does not show. <code>make</code> extracts the game from the "
             "tape or the cartridge, traces the code from its real entry points, "
             "generates the commented listings, then reassembles them and demands "
             "the original back, byte for byte.",
             "That test settles whether a listing can be trusted, but not whether "
             "it is right: if graphics are read as instructions, the bytes still "
             "come out identical and only the listing lies. So each project carries "
             "a second, different check &mdash; a budget where every byte has to be "
             "either code the tracer genuinely reaches, or a data range with a name "
             "and an explanation &mdash; plus tests that check what the "
             "documentation says against the binary.",
             "The comments live apart from the listings, anchored to the address "
             "they describe, so they survive a re-analysis of the binary. And much "
             "of what is claimed was not deduced by reading but measured with the "
             "openMSX emulator: watchpoints on memory to see which code touches "
             "each variable, and sampling the program counter during play to know "
             "what actually executes.",
             "No tape or cartridge image is distributed in any of these "
             "repositories. To rebuild a project you need your own copy of the "
             "game; each repository states the sha256 it expects."],
        e_repo="Repository", e_web="Website",
        pie="Documentation and preservation work on 8-bit software. Each game's "
            "code, graphics and sound belong to its authors and rights holders; "
            "what is published here is the analysis, the comments and the tools. "
            "No tape or cartridge image is distributed.",
    ),
    es=dict(
        titulo="antxiko &mdash; desensamblados comentados de juegos de 8 bits",
        claim="Binarios viejos de 8 bits desmontados byte a byte y comentados, con "
              "las herramientas para volver a montarlos: no se afirma nada que el "
              "binario no enseñe, y el código fuente tiene que devolver el "
              f"original, byte a byte. Ahora mismo son {N_JUEGOS} juegos de MSX.",
        ficha=[f"<b>{N_JUEGOS}</b> juegos", f"<b>{ANIOS}</b>",
               "MSX",
               f"<b>{N_CINTAS}</b> cintas &middot; <b>{N_CARTUCHOS}</b> cartuchos"],
        menu_gh="GitHub",
        otro=("../", "In English"),
        cifras=[(str(N_JUEGOS), "juegos desmontados"),
                (str(N_TERMINADOS), "terminados al 100 %"),
                (str(N_CON_WEB), "con web publicada"),
                (str(N_CINTAS), "cintas de cassette"),
                (str(N_CARTUCHOS), "cartuchos"),
                ("3", "compilaciones de Antarctic Adventure")],
        met=["Todos los proyectos siguen la misma regla: no se afirma nada que el "
             "binario no enseñe. <code>make</code> extrae el juego de la cinta o "
             "del cartucho, traza el código desde sus puntos de entrada de verdad, "
             "genera los listados comentados y luego los reensambla y exige que "
             "vuelva a salir el original, byte a byte.",
             "Esa prueba decide si un listado es de fiar, pero no si es correcto: "
             "si unos gráficos se leen como instrucciones, los bytes salen "
             "idénticos igual y lo único que miente es el listado. Por eso cada "
             "proyecto lleva una segunda comprobación, distinta &mdash;un "
             "presupuesto en el que cada byte tiene que ser o código al que el "
             "trazador llega de verdad, o un rango de datos con nombre y "
             "explicación&mdash;, más unos tests que cotejan contra el binario lo "
             "que dice la documentación.",
             "Los comentarios viven aparte de los listados, anclados a la dirección "
             "que describen, así que sobreviven a un reanálisis del binario. Y "
             "buena parte de lo que se afirma no se dedujo leyendo, sino midiendo "
             "con el emulador openMSX: watchpoints en memoria para ver qué código "
             "toca cada variable, y muestreo del contador de programa mientras se "
             "juega para saber qué se ejecuta de verdad.",
             "En ninguno de estos repositorios se distribuye la cinta ni la imagen "
             "del cartucho. Para reconstruir un proyecto hace falta una copia "
             "propia del juego; cada repositorio dice el sha256 que espera."],
        e_repo="Repositorio", e_web="Web",
        pie="Trabajo de documentación y preservación sobre software de 8 bits. El "
            "código, los gráficos y el sonido de cada juego siguen siendo de sus "
            "autores y titulares de derechos; lo que se publica aquí es el "
            "análisis, los comentarios y las herramientas. No se distribuye "
            "ninguna cinta ni imagen de cartucho.",
    ),
)


def tarjeta(p, idioma, t):
    enlaces = []
    if p["repo"]:
        enlaces.append(f'<a href="{p["repo"]}">{t["e_repo"]}</a>')
    if p["web"]:
        enlaces.append(f'<a href="{p["web"]}">{t["e_web"]}</a>')
    nota = p["nota"][idioma]
    if nota:
        enlaces.append(f"<em>{nota}</em>")
    return ('<article class="proy">'
            f'<h3>{p["titulo"]} <span>{p["anio"]}</span></h3>'
            f'<p class="meta">{p["meta"][idioma]}</p>'
            f'<p class="claim">{p["claim"][idioma]}</p>'
            f'<p class="datos">{p["datos"][idioma](idioma)}</p>'
            f'<p class="enlaces">{"".join(enlaces)}</p>'
            '</article>')


def rejilla(proyectos, idioma, t):
    return ('<div class="proyectos">'
            + "".join(tarjeta(p, idioma, t) for p in proyectos) + '</div>')


def seccion(c, idioma, t):
    """Una seccion de primer nivel: rotulo, intro y, o bien la rejilla de sus
    proyectos, o bien sus partes con un menu propio para saltar entre ellas."""
    partes = c.get("partes")
    if not partes:
        cuerpo = f'  {rejilla(c["proyectos"], idioma, t)}\n'
    else:
        cuerpo = ('  <nav class="docs">'
                  + "".join(f'<a href="#{p["id"]}">{p["titulo"][idioma]}</a>'
                            for p in partes)
                  + '</nav>\n')
        for p in partes:
            if "proyectos" in p:
                rotulo = (f'{p["titulo"][idioma]} '
                          f'<span>{cuenta(p["proyectos"], idioma)}</span>')
                dentro = rejilla(p["proyectos"], idioma, t)
            else:
                rotulo = p["titulo"][idioma]
                dentro = p["html"](idioma, t)
            cuerpo += (f'  <div class="parte" id="{p["id"]}">\n'
                       f'    <h3>{rotulo}</h3>\n'
                       f'    {dentro}\n'
                       f'  </div>\n')
    return (f'\n<section id="{c["id"]}">\n'
            f'  <h2>{c["titulo"][idioma]}</h2>\n'
            f'  <p class="n" style="margin-bottom:2rem;color:var(--suave)">'
            f'{c["intro"][idioma]}</p>\n'
            f'{cuerpo}'
            f'</section>\n')


def comprueba():
    """Que al repartir una seccion en partes no se pierda ni se repita nada."""
    ids = [g["id"] for g in GRUPOS]
    for p in DESENSAMBLADOS:
        if p.get("grupo") not in ids:
            raise SystemExit(f"{p['clave']}: grupo {p.get('grupo')!r} no esta en GRUPOS")
    for c in CATEGORIAS:
        for parte in c.get("partes", []):
            if "proyectos" in parte and not parte["proyectos"]:
                raise SystemExit(f"{c['id']}/{parte['id']}: parte sin proyectos")
        if c.get("partes"):
            repartidos = sorted(p["clave"] for parte in c["partes"]
                                for p in parte.get("proyectos", []))
            if repartidos != sorted(p["clave"] for p in c["proyectos"]):
                raise SystemExit(f"{c['id']}: las partes no reparten exactamente "
                                 f"sus proyectos")


def pagina(idioma):
    t = TXT[idioma]
    menu = [("#" + c["id"], c["menu"][idioma]) for c in CATEGORIAS]
    menu.append(("https://github.com/" + USUARIO, t["menu_gh"]))
    nav = "".join(f'<a href="{h}">{x}</a>' for h, x in menu)
    nav += (f'<a href="{t["otro"][0]}" style="margin-left:auto;color:var(--oro)">'
            f'{t["otro"][1]}</a>')

    ficha = "".join(f"<span>{x}</span>" for x in t["ficha"])
    secciones = "".join(seccion(c, idioma, t) for c in CATEGORIAS)

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t['titulo']}</title>
<style>{ESTILO}{EXTRA}</style>

<div class="w">
<header class="top">
  <h1>antxiko<span>/</span></h1>
  <p class="claim">{t['claim']}</p>
  <div class="ficha">{ficha}</div>
</header>
<nav>{nav}</nav>
{secciones}
<footer>{t['pie']}</footer>
</div>
"""


def main():
    comprueba()
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for idioma, ruta in (("en", "index.html"), ("es", "es/index.html")):
        destino = os.path.join(raiz, ruta)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        html = pagina(idioma)
        with open(destino, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("  %s: %d KB (%s)" % (ruta, len(html) // 1024, idioma))
    return 0


if __name__ == "__main__":
    sys.exit(main())
