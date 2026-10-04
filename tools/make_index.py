#!/usr/bin/env python3
"""Genera la portada de antxiko.github.io en los dos idiomas.

    python3 tools/make_index.py

Escribe index.html (ingles) y es/index.html (castellano), y la pagina de cada
seccion en los dos idiomas. El diseno es el de la
serie de desensamblados: la hoja de estilo se importa tal cual de
tools/estilo_web.py (el mismo fichero que usan las webs de los juegos) y aqui
solo se anade lo propio de una portada de indice: la tarjeta de proyecto.

TODOS los datos de cada proyecto salen de su repositorio local: las cifras y las
frases, de su README; la URL del repositorio, de su remote de git; y la URL de su
web, del remote mas la existencia de docs/index.html. Un proyecto sin web se
queda sin enlace de web, y no se inventa ninguna.

El sitio son secciones de primer nivel (CATEGORIAS: hoy los desensamblados y
los parches), cada una en su pagina: <id>/index.html y es/<id>/index.html. La
portada lleva la cabecera, el menu (un boton por seccion) y de cada seccion su
rotulo, su intro y la puerta a su pagina. Las anclas viejas de cuando todo iba
en una pagina (/#patches, /#konami, /#tools...) las redirige un script de la
portada a su pagina. Una seccion sin proyectos no sale ni en el menu.
Una seccion puede ir en partes: la de los desensamblados lleva las cifras, tres
grupos de juegos (Konami, exclusivos de MSX, conversiones), el metodo y la serie
por dentro (HERRAMIENTAS), y cada juego dice su grupo en el campo 'grupo'. Para
anadir otra clase de proyecto: otra lista con los mismos campos que
DESENSAMBLADOS y otra entrada en CATEGORIAS. El menu, las secciones y sus
partes se generan de esas listas.

Y escribe los dos feeds Atom, feed.xml (ingles) y es/feed.xml (castellano), de
la lista NOVEDADES: una entrada por publicacion, escrita a mano en el mismo
commit que pone el proyecto en la portada. El feed es XML, asi que ningun texto
de la portada llega a el sin pasar por texto_plano(): las entidades HTML
(&middot;, &mdash;...) no existen en XML y romperian el fichero entero.
"""

import html
import json
import os
import re
import sys
from datetime import datetime
from xml.sax import saxutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo_web import ESTILO

USUARIO = "antxiko"
SITIO = "https://antxiko.github.io"   # sin barra final: se le pegan las rutas
DOMINIO = SITIO.split("//", 1)[1]      # para los id tag: del feed
LIMITE = 20                            # entradas que salen al feed; el resto se queda en la lista

# Lo unico que se anade a la hoja de estilo de la serie: la tarjeta de proyecto
# y los botones de seccion del menu de arriba.
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
nav a.sec,a.entrar{border:1px solid var(--linea);padding:.4rem .95rem;
  color:var(--tinta);text-transform:uppercase;letter-spacing:.07em;font-size:13px;
  text-decoration:none}
nav a.sec:hover,nav a.sec:focus,a.entrar:hover,a.entrar:focus{border-color:var(--rojo)}
nav a.sec[aria-current]{background:var(--rojo);border-color:var(--rojo);color:var(--fondo)}
nav{align-items:center}
.resumen{margin:3rem 0}
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
        clave="bomberman",
        grupo="msx-exclusive",
        titulo="Bomber Man",
        anio=1983,
        repo="https://github.com/antxiko/Bomberman-disassembly",
        web="https://antxiko.github.io/Bomberman-disassembly/",
        meta=dict(
            en="Hudson Soft &middot; MSX &middot; 8 KB cartridge",
            es="Hudson Soft &middot; MSX &middot; cartucho de 8 KB",
        ),
        claim=dict(
            en="The smallest cartridge in this series, and the whole game fits "
               "inside it <b>without a single sprite</b>: the bomber, the "
               "monsters, the bombs and the flames are all name-table tiles. "
               "There is no map data structure either &mdash; the game reads "
               "the tile number, and three comparisons carry the lot. Its "
               "cartridge header <b>is code</b>: INIT points at 0x4004, where "
               "STATEMENT, DEVICE and TEXT should be.",
            es="El cartucho más pequeño de esta serie, y el juego entero cabe "
               "dentro <b>sin un solo sprite</b>: el bombero, los bichos, las "
               "bombas y las llamas son casillas de la tabla de nombres. "
               "Tampoco hay una estructura de datos del mapa &mdash;el juego "
               "lee el número de casilla, y tres comparaciones sostienen todo "
               "lo demás&mdash;. Su cabecera de cartucho <b>es código</b>: "
               "INIT apunta a 0x4004, donde deberían estar STATEMENT, DEVICE "
               "y TEXT.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(3557, i)} of code, {cif(4635, i)} of data "
                          f"&middot; {cif(200, i)} routines, none under 10% "
                          f"&middot; commented to <b>50.2%</b>"),
            es=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(3557, i)} de código, {cif(4635, i)} de datos "
                          f"&middot; {cif(200, i)} rutinas, ninguna por debajo "
                          f"del 10 % &middot; comentado al <b>50,2 %</b>"),
        ),
        nota=dict(
            en="every fourth stage the game <b>drops the bombs for you</b> "
               "&mdash; and hides a different prize under the bricks, chosen "
               "by the very same mask",
            es="cada cuatro fases el juego <b>pone las bombas solo</b> &mdash;y "
               "esconde otro premio debajo de los ladrillos, elegido con la "
               "misma máscara&mdash;",
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
                          f"&middot; {cif(593, i)} routines &middot; commented to "
                          f"<b>23.4%</b> &middot; measured in "
                          f"openMSX: the interrupt takes <b>50.1%</b> of the frame"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8911, i)} de código, {cif(7473, i)} de datos "
                          f"&middot; {cif(593, i)} rutinas &middot; comentado al "
                          f"<b>23,4 %</b> &middot; medido en "
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
                          f"&middot; {cif(314, i)} routines &middot; commented to <b>25.6%</b>"),
            es=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(4880, i)} de código, {cif(3312, i)} de datos "
                          f"&middot; {cif(314, i)} rutinas &middot; comentado al <b>25,6 %</b>"),
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
                          f"&middot; {cif(407, i)} routines &middot; commented "
                          f"to <b>24.2%</b>"),
            es=lambda i: (f"{cif(8192, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5783, i)} de código, {cif(2409, i)} de datos "
                          f"&middot; {cif(407, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(513, i)} routines &middot; commented to <b>29.7%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7448, i)} de código, {cif(8936, i)} de datos "
                          f"&middot; {cif(513, i)} rutinas &middot; comentado al <b>29,7 %</b>"),
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
                          f"{cif(10437, i)} of data &middot; commented to <b>24.0%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>tres compilaciones</b>, las tres <b>byte a "
                          f"byte</b> &middot; listado principal: {cif(5947, i)} de "
                          f"código, {cif(10437, i)} de datos &middot; comentado al "
                          f"<b>24,0 %</b>"),
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
                          f"&middot; {cif(498, i)} routines &middot; commented to <b>25.9%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8962, i)} de código, {cif(7422, i)} de datos "
                          f"&middot; {cif(498, i)} rutinas &middot; comentado al <b>25,9 %</b>"),
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
                          f"&middot; {cif(333, i)} routines &middot; commented "
                          f"to <b>39.3%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5343, i)} de código, {cif(11041, i)} de datos "
                          f"&middot; {cif(333, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(1001, i)} routines &middot; commented "
                          f"to <b>30.7%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(15432, i)} de código, {cif(17336, i)} de datos "
                          f"&middot; {cif(1001, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(569, i)} routines &middot; commented "
                          f"to <b>33.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9335, i)} de código, {cif(7049, i)} de datos "
                          f"&middot; {cif(569, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(647, i)} routines &middot; commented "
                          f"to <b>29.9%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9872, i)} de código, {cif(6512, i)} de datos "
                          f"&middot; {cif(647, i)} rutinas &middot; comentado "
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
                          f"to <b>42.0%</b>, none below 10%"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6065, i)} de codigo, {cif(10319, i)} de datos "
                          f"&middot; {cif(358, i)} rutinas &middot; comentado al "
                          f"<b>42,0 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="dunkshot",
        grupo="msx-exclusive",
        titulo="Dunk Shot",
        anio=1986,
        repo="https://github.com/antxiko/DunkShot-disassembly",
        web="https://antxiko.github.io/DunkShot-disassembly/",
        meta=dict(
            en="HAL Laboratory &middot; MSX &middot; 32 KB cartridge",
            es="HAL Laboratory &middot; MSX &middot; cartucho de 32 KB",
        ),
        claim=dict(
            en="Three-on-three basketball on a <b>56-column court seen through "
               "a 32-column window</b>, with no hardware scrolling. Every player "
               "is <b>four sprites</b> (hair, skin, shirt, skin) and the flicker "
               "is deliberate: seven groups sorted by depth, shown forwards and "
               "reversed on alternate frames. The computer teams are <b>generated by "
               "level</b>, teams are saved to tape as a BSAVE, and the whole "
               "court, the 160 poses and six screens are drawn from the ROM and "
               "checked against openMSX down to zero bytes.",
            es="Baloncesto de tres contra tres en una <b>pista de 56 columnas "
               "vista por una ventana de 32</b>, sin scroll por hardware. Cada "
               "jugador son <b>cuatro sprites</b> (pelo, piel, camiseta, piel) y "
               "el parpadeo est&aacute; programado: siete grupos ordenados por "
               "profundidad, del derecho y del rev&eacute;s en cuadros alternos. Los equipos de la "
               "m&aacute;quina se <b>fabrican por nivel</b>, los equipos se "
               "graban en cinta como un BSAVE, y la pista entera, las 160 poses "
               "y seis pantallas est&aacute;n dibujadas desde la ROM y "
               "cotejadas contra openMSX a cero bytes.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(20642, i)} of code, {cif(12126, i)} of data "
                          f"&middot; {cif(1289, i)} routines &middot; commented "
                          f"to <b>43.2%</b>, none below 10%"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(20642, i)} de c&oacute;digo, {cif(12126, i)} de datos "
                          f"&middot; {cif(1289, i)} rutinas &middot; comentado al "
                          f"<b>43,2 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="holeinonepro",
        grupo="msx-exclusive",
        titulo="Hole in One Professional",
        anio=1986,
        repo="https://github.com/antxiko/HoleInOnePro-disassembly",
        web="https://antxiko.github.io/HoleInOnePro-disassembly/",
        meta=dict(
            en="HAL Laboratory &middot; MSX &middot; 32 KB cartridge",
            es="HAL Laboratory &middot; MSX &middot; cartucho de 32 KB",
        ),
        claim=dict(
            en="Two eighteen-hole courses, <b>thirty-five real tour "
               "professionals</b> and a full course editor, in 32 KB. The "
               "opponent does not compute its shot: it <b>rehearses it with "
               "the real physics</b> and retries until it likes the result. "
               "The terrain is decided <b>by the pixel</b>, read straight out "
               "of the VRAM. And what the editor saves is the <b>1984 "
               "cartridge&rsquo;s own file</b>, byte for byte.",
            es="Dos campos de dieciocho hoyos, <b>treinta y cinco "
               "profesionales reales</b> y un editor de campos completo, en "
               "32 KB. El rival no calcula el golpe: lo <b>ensaya con la "
               "fisica de verdad</b> y lo repite hasta que le sale. El terreno "
               "se decide <b>por el pixel</b>, leido de la propia VRAM. Y lo "
               "que graba el editor es el <b>fichero del cartucho de 1984</b>, "
               "byte a byte.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(14186, i)} of code, {cif(18582, i)} of data "
                          f"&middot; {cif(903, i)} routines &middot; commented "
                          f"to <b>44.4%</b>, none below 10%"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(14186, i)} de codigo, {cif(18582, i)} de datos "
                          f"&middot; {cif(903, i)} rutinas &middot; comentado al "
                          f"<b>44,4 %</b>, ninguna por debajo del 10 %"),
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
        clave="circus",
        grupo="konami",
        titulo="Circus Charlie",
        anio=1984,
        repo="https://github.com/antxiko/CircusCharlie-disassembly",
        web="https://antxiko.github.io/CircusCharlie-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-712",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-712",
        ),
        claim=dict(
            en="<b>The whole game lives inside the interrupt</b>: INIT hooks "
               "H.KEYI and sits forever on a <code>jr $</code>. Five circus "
               "acts chosen by <b>a single byte</b>, and the ring drawn "
               "<b>from the cartridge's tables</b>, frame by frame, without "
               "one byte differing from the emulator.",
            es="<b>El juego entero vive en la interrupción</b>: INIT engancha "
               "H.KEYI y se queda para siempre en un <code>jr $</code>. Cinco "
               "números de circo repartidos por <b>un solo byte</b>, y la pista "
               "dibujada <b>desde las tablas del cartucho</b>, cuadro a "
               "cuadro, sin un byte distinto del emulador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(7894, i)} of code, {cif(8490, i)} of data "
                          f"&middot; {cif(576, i)} routines &middot; commented "
                          f"to <b>47.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7894, i)} de código, {cif(8490, i)} de datos "
                          f"&middot; {cif(576, i)} rutinas &middot; comentado "
                          f"al <b>47,1 %</b>"),
        ),
        nota=dict(
            en="The <b>five acts</b> drawn from the cartridge's tables, with "
               "Charlie and the obstacles: <b>0 bytes</b> different from "
               "openMSX.",
            es="Los <b>cinco números</b> dibujados desde las tablas del "
               "cartucho, con Charlie y los obstáculos: <b>0 bytes</b> "
               "distintos de openMSX.",
        ),
    ),
    dict(
        clave="magicaltree",
        grupo="konami",
        titulo="Magical Tree",
        anio=1984,
        repo="https://github.com/antxiko/MagicalTree-disassembly",
        web="https://antxiko.github.io/MagicalTree-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-713",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-713",
        ),
        claim=dict(
            en="<b>The level lives in VRAM</b>: each stage's script goes up to "
               "<code>0x3B80</code>, behind the sprite attributes, and the "
               "screen doubles as the map. <b>Nine stages</b> drawn from the "
               "cartridge's tables without one cell differing from the "
               "emulator.",
            es="<b>El nivel vive en la VRAM</b>: el guion de cada fase sube a "
               "<code>0x3B80</code>, detrás de los atributos de los sprites, y "
               "la pantalla hace de mapa. <b>Nueve fases</b> dibujadas desde "
               "las tablas del cartucho sin una celda distinta del emulador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8537, i)} of code, {cif(7847, i)} of data "
                          f"&middot; {cif(628, i)} routines &middot; commented "
                          f"to <b>47.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8537, i)} de código, {cif(7847, i)} de datos "
                          f"&middot; {cif(628, i)} rutinas &middot; comentado "
                          f"al <b>47,4 %</b>"),
        ),
        nota=dict(
            en="The tree's <b>nine stages</b>, whole, drawn from each stage's "
               "script: <b>0 cells</b> different from openMSX in 156 dumps.",
            es="Las <b>nueve fases</b> del árbol, enteras, dibujadas desde el "
               "guion de cada fase: <b>0 celdas</b> distintas de openMSX en 156 "
               "volcados.",
        ),
    ),
    dict(
        clave="comicbakery",
        grupo="konami",
        titulo="Comic Bakery",
        anio=1984,
        repo="https://github.com/antxiko/ComicBakery-disassembly",
        web="https://antxiko.github.io/ComicBakery-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-714",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-714",
        ),
        claim=dict(
            en="<b>A 92-column bakery</b> whose machines change from one "
               "stage to the next, an <b>eight-minute working day</b>, and "
               "the raccoons the listing called carts, <b>drawn from the "
               "ROM</b> without one byte differing from the emulator.",
            es="<b>Una panadería de 92 columnas</b> que cambia de máquinas de "
               "una fase a otra, una <b>jornada de ocho minutos</b>, y los "
               "mapaches que el listado llamaba carros, <b>dibujados desde la "
               "ROM</b> sin un byte distinto del emulador.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(8097, i)} of code, {cif(8287, i)} of data "
                          f"&middot; {cif(535, i)} routines &middot; commented "
                          f"to <b>46.9%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8097, i)} de código, {cif(8287, i)} de datos "
                          f"&middot; {cif(535, i)} rutinas &middot; comentado "
                          f"al <b>46,9 %</b>"),
        ),
        nota=dict(
            en="The <b>baker</b>'s fourteen poses, the <b>three "
               "raccoons</b> and the <b>bakery of each stage</b>, drawn from "
               "the ROM: <b>0 bytes</b> different from openMSX in 16 dumps.",
            es="El <b>panadero</b> en sus catorce poses, los <b>tres "
               "mapaches</b> y la <b>panadería de cada fase</b>, dibujados "
               "desde la ROM: <b>0 bytes</b> distintos de openMSX en 16 "
               "volcados.",
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
                          f"{cif(6446, i)} of code, {cif(9938, i)} of data "
                          f"&middot; {cif(428, i)} routines &middot; commented "
                          f"to <b>22.8%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6446, i)} de código, {cif(9938, i)} de datos "
                          f"&middot; {cif(428, i)} rutinas &middot; comentado "
                          f"al <b>22,8 %</b>"),
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
                          f"&middot; {cif(461, i)} routines &middot; commented "
                          f"to <b>32.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7086, i)} de código, {cif(9298, i)} de datos "
                          f"&middot; {cif(461, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(558, i)} routines &middot; commented "
                          f"to <b>35.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(8665, i)} de código, {cif(7719, i)} de datos "
                          f"&middot; {cif(558, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(512, i)} routines &middot; commented "
                          f"to <b>53.0%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7789, i)} de código, {cif(8595, i)} de datos "
                          f"&middot; {cif(512, i)} rutinas &middot; comentado "
                          f"al <b>53,0 %</b>"),
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
                          f"&middot; {cif(482, i)} routines &middot; commented "
                          f"to <b>55.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7797, i)} de código, {cif(8587, i)} de datos "
                          f"&middot; {cif(482, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(548, i)} routines &middot; commented "
                          f"to <b>64.3%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7676, i)} de código, {cif(8708, i)} de datos "
                          f"&middot; {cif(548, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(1213, i)} routines &middot; commented "
                          f"to <b>36.5%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(20116, i)} de código, {cif(12652, i)} de datos "
                          f"&middot; {cif(1213, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(651, i)} routines &middot; commented "
                          f"to <b>45.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9803, i)} de código, {cif(6581, i)} de datos "
                          f"&middot; {cif(651, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(629, i)} routines &middot; commented "
                          f"to <b>44.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9618, i)} de código, {cif(6766, i)} de datos "
                          f"&middot; {cif(629, i)} rutinas &middot; comentado "
                          f"al <b>44,5 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="knightmare",
        grupo="konami",
        titulo="Knightmare",
        anio=1986,
        repo="https://github.com/antxiko/Knightmare-disassembly",
        web="https://antxiko.github.io/Knightmare-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-739",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-739",
        ),
        claim=dict(
            en="<b>Konami left two typos in its cosine tables.</b> A cosine "
               "quadrant can only go down; these two go up once each, and the "
               "value that goes up is <b>precisely the only one</b> that "
               "departs from the function. Inside there is also a cheat that "
               "asks for <b>left and right at once</b> &mdash; impossible on a "
               "joystick &mdash; and hands over twenty-six lives.",
            es="<b>Konami dejó dos erratas en sus tablas de coseno.</b> Un "
               "cuadrante de coseno solo puede bajar; estos dos suben una vez "
               "cada uno, y el valor que sube es <b>justo el único</b> que se "
               "aparta de la función. Dentro hay además un truco que pide "
               "<b>izquierda y derecha a la vez</b> &mdash;imposible en un "
               "joystick&mdash; y regala veintiséis vidas.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(15233, i)} of code, {cif(17535, i)} of data "
                          f"&middot; {cif(985, i)} routines &middot; commented "
                          f"to <b>22.4%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(15233, i)} de código, {cif(17535, i)} de datos "
                          f"&middot; {cif(985, i)} rutinas &middot; comentado "
                          f"al <b>22,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="penguinadventure",
        grupo="konami",
        titulo="Penguin Adventure",
        anio=1986,
        repo="https://github.com/antxiko/PenguinAdventure-disassembly",
        web="https://antxiko.github.io/PenguinAdventure-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB cartridge &middot; RC-743",
            es="Konami &middot; MSX &middot; cartucho de 128 KB &middot; RC-743",
        ),
        claim=dict(
            en="<b>Two hidden keyboard codes: NORIKO and KAZUMI.</b> They turn "
               "on a CONTINUE that does not exist without them, and the proof "
               "is in the watcher itself: the <b>nine</b> keys it polls are "
               "exactly the letters needed to spell those two names and no "
               "others. And the gambling machine is a real slot machine &mdash; "
               "the cherry takes five of sixteen slots and is the only symbol "
               "that pays on its own. And the good ending or the bad one "
               "&mdash;the princess alive or dead&mdash; does not depend on how "
               "you play: it depends on <b>how many times you pause</b>, a "
               "finding of Manuel Pazos&rsquo;s that is pinned down here in the "
               "binary.",
            es="<b>Dos claves de teclado escondidas: NORIKO y KAZUMI.</b> "
               "Encienden un CONTINUE que sin ellas no existe, y la prueba "
               "está en el propio vigilante: las <b>nueve</b> teclas que mira "
               "son exactamente las letras que hacen falta para escribir esos "
               "dos nombres y ninguna más. Y la máquina de apostar es una "
               "tragaperras de verdad &mdash; la cereza ocupa cinco de las "
               "dieciséis casillas y es el único símbolo que paga suelto. Y el "
               "final bueno o el malo &mdash;la princesa viva o muerta&mdash; "
               "no depende de cómo juegues: depende de <b>cuántas veces "
               "pauses</b>, hallazgo de Manuel Pazos que aquí se localiza en "
               "el binario.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(32317, i)} of code, {cif(98755, i)} of data "
                          f"&middot; {cif(1526, i)} routines &middot; commented "
                          f"to <b>44.7%</b>"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(32317, i)} de código, {cif(98755, i)} de datos "
                          f"&middot; {cif(1526, i)} rutinas &middot; comentado "
                          f"al <b>44,7 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="vampirekiller",
        grupo="konami",
        titulo="Vampire Killer",
        anio=1986,
        repo="https://github.com/antxiko/VampireKiller-disassembly",
        web="https://antxiko.github.io/VampireKiller-disassembly/",
        meta=dict(
            en="Konami &middot; MSX2 &middot; 128 KB cartridge &middot; RC-744",
            es="Konami &middot; MSX2 &middot; cartucho de 128 KB &middot; RC-744",
        ),
        claim=dict(
            en="<b>The first MSX2 in the series: Dracula&rsquo;s whole castle, "
               "drawn from the ROM.</b> The 156 rooms with what each one hides, "
               "Simon, the enemies and the six bosses, checked against openMSX "
               "down to zero bytes. There are <b>33 hidden vendors who do not "
               "always sell</b>: what happens depends "
               "on how many times you hit them. And Dracula is half sprite "
               "and half drawing: the body is copied by the VDP.",
            es="<b>El primer MSX2 de la serie: el castillo de Drácula entero, "
               "dibujado desde la ROM.</b> Las 156 habitaciones con lo que "
               "esconde cada una, Simon, los enemigos y los seis jefes, "
               "cotejados contra openMSX a cero bytes. Hay <b>33 vendedores "
               "escondidos que no siempre venden</b>: lo que "
               "pasa depende de cuántas veces se les pega. Y Drácula es "
               "medio sprite y medio dibujo: el cuerpo lo copia el VDP.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(29786, i)} of code, {cif(101286, i)} of data "
                          f"&middot; {cif(1909, i)} routines &middot; commented "
                          f"to <b>49.4%</b>"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(29786, i)} de código, {cif(101286, i)} de datos "
                          f"&middot; {cif(1909, i)} rutinas &middot; comentado "
                          f"al <b>49,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="goemon",
        grupo="konami",
        titulo="Ganbare Goemon! Karakuri D&#333;ch&#363;",
        anio=1987,
        repo="https://github.com/antxiko/GanbareGoemon-disassembly",
        web="https://antxiko.github.io/GanbareGoemon-disassembly/",
        meta=dict(
            en="Konami &middot; MSX2 &middot; 128 KB cartridge &middot; RC-748",
            es="Konami &middot; MSX2 &middot; cartucho de 128 KB &middot; RC-748",
        ),
        claim=dict(
            en="<b>Seven stages of seven areas, 124 screens, drawn from the "
               "ROM street by street.</b> The 21 interiors with their prices, "
               "Goemon, Ebisumaru and 30 enemy types, and the <b>42 secret "
               "passages</b> walked in first person, all checked against openMSX "
               "down to zero. Plus four password keywords, two words to type in "
               "the pause, a stage menu with Q*bert or the Game Master next to "
               "it, and Konami's hidden mark written in the game's own hiragana.",
            es="<b>Siete fases de siete zonas, 124 pantallas, dibujadas desde "
               "la ROM calle a calle.</b> Los 21 interiores con sus precios, "
               "Goemon, Ebisumaru y 30 tipos de enemigo, y los <b>42 pasadizos "
               "secretos</b> que se recorren en primera persona, todo cotejado "
               "contra openMSX a cero. Y cuatro claves en la contrase&ntilde;a, "
               "dos palabras para teclear en la pausa, un men&uacute; de fases "
               "con Q*bert o el Game Master al lado, y la marca oculta de Konami "
               "escrita en el hiragana del propio juego.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(28724, i)} of code, {cif(102348, i)} of data "
                          f"&middot; {cif(1678, i)} routines &middot; commented "
                          f"to <b>42.5%</b>, none below 10%"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(28724, i)} de c&oacute;digo, {cif(102348, i)} de datos "
                          f"&middot; {cif(1678, i)} rutinas &middot; comentado al "
                          f"<b>42,5 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="galious",
        grupo="konami",
        titulo="The Maze of Galious",
        anio=1987,
        repo="https://github.com/antxiko/MazeOfGalious-disassembly",
        web="https://antxiko.github.io/MazeOfGalious-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB cartridge &middot; RC-749",
            es="Konami &middot; MSX &middot; cartucho de 128 KB &middot; RC-749",
        ),
        claim=dict(
            en="<b>The castle and ten worlds, all 321 rooms, drawn from the ROM "
               "and laid out by their neighbours.</b> Popolon and Aphrodite, the "
               "sprite sets, the ten bosses (character mosaics, not sprites), "
               "the 47 items and the shops, all checked against openMSX down to "
               "zero. Plus the black rooms that turn out to be hints and shops, "
               "ZEUS in the pause to continue, the character sitting on a cup "
               "with F2, and what Q*bert next to it gives you.",
            es="<b>El castillo y diez mundos, las 321 salas, dibujadas desde la "
               "ROM y colocadas por sus vecinas.</b> Popolon y Afrodita, los "
               "juegos de sprites, los diez jefes (mosaicos de caracteres, no "
               "sprites), los 47 objetos y las tiendas, todo cotejado contra "
               "openMSX a cero. Y las salas negras que resultan ser pistas y "
               "tiendas, ZEUS en la pausa para continuar, el personaje sentado "
               "en una taza con F2 y lo que da Q*bert al lado.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(53613, i)} of code, {cif(77459, i)} of data "
                          f"&middot; {cif(3423, i)} routines &middot; commented "
                          f"to <b>40.1%</b>, none below 10%"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(53613, i)} de c&oacute;digo, {cif(77459, i)} de datos "
                          f"&middot; {cif(3423, i)} rutinas &middot; comentado al "
                          f"<b>40,1 %</b>, ninguna por debajo del 10 %"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="kingkong2",
        grupo="konami",
        titulo="King Kong 2: Yomigaeru Densetsu",
        anio=1986,
        repo="https://github.com/antxiko/KingKong2-disassembly",
        web="https://antxiko.github.io/KingKong2-disassembly/",
        meta=dict(
            en="Konami &middot; MSX2 &middot; 128 KB cartridge &middot; RC-745",
            es="Konami &middot; MSX2 &middot; cartucho de 128 KB &middot; RC-745",
        ),
        claim=dict(
            en="<b>A 140-screen island, drawn from the ROM, with what every "
               "screen hides</b>: 15 passages, 37 pieces of scenery that can be "
               "removed, the items and who talks. Mitchel, the 55 named enemies "
               "and <b>five bosses that are not sprites</b>, painted by the VDP "
               "and checked against openMSX down to zero bytes. Three endings "
               "that depend on the days and on how many times you continue, and "
               "an axe that only works against one enemy.",
            es="<b>Una isla de 140 pantallas, dibujada desde la ROM, con lo que "
               "esconde cada una</b>: 15 pasadizos, 37 cosas de decorado que se "
               "quitan, los objetos y quién habla. Mitchel, los 55 enemigos con "
               "nombre y <b>cinco jefes que no son sprites</b>, pintados por el "
               "VDP y cotejados contra openMSX a cero bytes. Tres finales que "
               "dependen de los días y de las veces que continúas, y un hacha "
               "que solo sirve contra un enemigo.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(37983, i)} of code, {cif(93089, i)} of data "
                          f"&middot; {cif(2414, i)} routines &middot; commented "
                          f"to <b>40.1%</b>"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(37983, i)} de código, {cif(93089, i)} de datos "
                          f"&middot; {cif(2414, i)} rutinas &middot; comentado "
                          f"al <b>40,1 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="qbert",
        grupo="konami",
        titulo="Q*bert",
        anio=1986,
        repo="https://github.com/antxiko/Qbert-disassembly",
        web="https://antxiko.github.io/Qbert-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-746",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-746",
        ),
        claim=dict(
            en="<b>The cubes roll like dice</b>: each one is one of the 24 "
               "rotations of a cube, and a stage is cleared with <b>five "
               "finished in a row</b>, not by painting the pyramid. The 50 "
               "stages, the bonus stage and the duel drawn from the ROM and "
               "checked against openMSX down to zero bytes. A two-player duel "
               "settled by rock, paper, scissors, a hidden life and a moai.",
            es="<b>Los cubos ruedan como dados</b>: cada uno es uno de los 24 "
               "giros de un cubo, y la fase se acaba con <b>cinco acabados en "
               "línea</b>, no pintando la pirámide. Las 50 fases, la "
               "bonificación y el duelo dibujados desde la ROM y cotejados "
               "contra openMSX a cero bytes. Un duelo de dos que se desempata a "
               "piedra, papel o tijera, una vida escondida y un moái.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(11743, i)} of code, {cif(21025, i)} of data "
                          f"&middot; {cif(788, i)} routines &middot; commented "
                          f"to <b>78.1%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(11743, i)} de código, {cif(21025, i)} de datos "
                          f"&middot; {cif(788, i)} rutinas &middot; comentado "
                          f"al <b>78,1 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hinotori",
        grupo="konami",
        titulo="Hinotori",
        anio=1987,
        repo="https://github.com/antxiko/Hinotori-disassembly",
        web="https://antxiko.github.io/Hinotori-disassembly/",
        meta=dict(
            en="Konami &middot; MSX2 &middot; 128 KB cartridge &middot; RC-747",
            es="Konami &middot; MSX2 &middot; cartucho de 128 KB &middot; RC-747",
        ),
        claim=dict(
            en="<b>With King Kong 2 next to it, it boots King Kong 2</b> and "
               "saves its game to tape with F4. Seventeen cheat passwords, one "
               "named after a designer in the credits and one in lower case "
               "that can never be typed. The six stages, their rooms and the "
               "18 gates that join them drawn from the ROM and checked "
               "against openMSX.",
            es="<b>Con King Kong 2 al lado, arranca King Kong 2</b> y le graba "
               "la partida en cinta con F4. Diecisiete contraseñas de truco, "
               "una con el apodo de un diseñador de los créditos y otra en "
               "minúsculas que no se puede escribir nunca. Las seis fases, sus "
               "salas y las 18 puertas que las unen dibujadas desde la ROM y "
               "cotejadas contra openMSX.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(32229, i)} of code, {cif(98843, i)} of data "
                          f"&middot; {cif(1944, i)} routines &middot; commented "
                          f"to <b>40.4%</b>"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(32229, i)} de código, {cif(98843, i)} de datos "
                          f"&middot; {cif(1944, i)} rutinas &middot; comentado "
                          f"al <b>40,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="twinbee",
        grupo="konami",
        titulo="Twin Bee",
        anio=1986,
        repo="https://github.com/antxiko/TwinBee-disassembly",
        web="https://antxiko.github.io/TwinBee-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-740",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-740",
        ),
        claim=dict(
            en="<b>Only half a ship is in the ROM.</b> Each sprite pattern "
               "stores its <b>left half</b>; the right half is worked out by "
               "flipping every byte bit for bit, which is why everything that "
               "flies in this game is symmetric. And the demo is a "
               "<b>recorded game</b>: twenty-eight joystick readings fed in "
               "through the player's own door, with the Z80's R register set "
               "to zero so the randomness comes out the same every time.",
            es="<b>En la ROM solo está media nave.</b> De cada patrón de "
               "sprite se guarda la <b>mitad izquierda</b>; la derecha la "
               "calcula el cartucho invirtiendo cada byte bit a bit, y por eso "
               "todo lo que vuela en este juego es simétrico. Y la "
               "demostración es una <b>partida grabada</b>: veintiocho "
               "lecturas de mando metidas por la puerta del jugador, con el "
               "registro R del Z80 puesto a cero para que el azar salga "
               "siempre igual.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(14406, i)} of code, {cif(18362, i)} of data "
                          f"&middot; {cif(1000, i)} routines &middot; commented "
                          f"to <b>41.4%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(14406, i)} de código, {cif(18362, i)} de datos "
                          f"&middot; {cif(1000, i)} rutinas &middot; comentado "
                          f"al <b>41,4 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="boxing",
        grupo="konami",
        titulo="Konami's Boxing",
        anio=1985,
        repo="https://github.com/antxiko/Boxing-disassembly",
        web="https://antxiko.github.io/Boxing-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-736",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-736",
        ),
        claim=dict(
            en="<b>Six opponents out of three figure archives, and still six "
               "faces.</b> There are six names in the table at 0x5661 and the "
               "figures come out of a table of <b>three</b> words, but every "
               "opponent figure hides one piece more that only the second "
               "round paints: SANCHESS's long hair, CHINA KHAN's pigtail, "
               "MOAI Jr.'s face &mdash;and only the moai changes colour. And "
               "the scorecard is kept upside down &mdash; it adds up "
               "<b>faults</b> and finishes with <code>10 - faults</code>, "
               "which is the ten-point must system of real boxing.",
            es="<b>Seis rivales de tres archivos de figuras, y aun así seis "
               "caras.</b> Los nombres son seis en la tabla de 0x5661 y las "
               "figuras salen de una tabla de <b>tres</b> palabras, pero cada "
               "figura de rival esconde una pieza de más que solo pinta la "
               "segunda vuelta: el pelo largo de SANCHESS, la coleta de CHINA "
               "KHAN, la cara de MOAI Jr. &mdash;y solo el moai cambia de "
               "color. Y la puntuación se lleva al revés &mdash;va sumando "
               "<b>faltas</b> y al final hace <code>10 - faltas</code>, que es "
               "el sistema de los diez puntos del boxeo de verdad.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(6932, i)} of code, {cif(25836, i)} of data "
                          f"&middot; {cif(475, i)} routines &middot; commented "
                          f"to <b>52.6%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6932, i)} de código, {cif(25836, i)} de datos "
                          f"&middot; {cif(475, i)} rutinas &middot; comentado "
                          f"al <b>52,6 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="yiearkungfu2",
        grupo="konami",
        titulo="Yie Ar Kung-Fu II",
        anio=1985,
        repo="https://github.com/antxiko/YieArKungFu2-disassembly",
        web="https://antxiko.github.io/YieArKungFu2-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-737",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-737",
        ),
        claim=dict(
            en="<b>It looks for its own first part in the next slot.</b> "
               "Before installing the interrupt hook it scans the four slots "
               "and takes two 16-byte sums, and it tells the <b>two builds</b> "
               "of Yie Ar Kung-Fu (RC-725) apart. Inside, half a screen: the "
               "scenery is drawn only on the left and the right half is the "
               "same patterns with <b>all eight bits reversed</b>.",
            es="<b>Busca a su primera parte en la ranura de al lado.</b> Antes "
               "de instalar el gancho de interrupción rastrea las cuatro "
               "ranuras y toma dos sumas de 16 bytes, y distingue las <b>dos "
               "compilaciones</b> del Yie Ar Kung-Fu (RC-725). Dentro, media "
               "pantalla: el decorado se dibuja solo por la izquierda y la "
               "derecha son los mismos patrones con <b>los ocho bits del "
               "revés</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(13725, i)} of code, {cif(19043, i)} of data "
                          f"&middot; {cif(1027, i)} routines &middot; commented "
                          f"to <b>40.9%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(13725, i)} de código, {cif(19043, i)} de datos "
                          f"&middot; {cif(1027, i)} rutinas &middot; comentado "
                          f"al <b>40,9 %</b>"),
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
                          f"&middot; {cif(568, i)} routines &middot; commented "
                          f"to <b>44.0%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7494, i)} de código, {cif(8890, i)} de datos "
                          f"&middot; {cif(568, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(492, i)} routines &middot; commented "
                          f"to <b>32.4%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7882, i)} de código, {cif(8502, i)} de datos "
                          f"&middot; {cif(492, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(386, i)} routines &middot; commented "
                          f"to <b>25.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(5953, i)} de código, {cif(10431, i)} de datos "
                          f"&middot; {cif(386, i)} rutinas &middot; comentado "
                          f"al <b>25,1 %</b>"),
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
                          f"&middot; {cif(500, i)} routines &middot; commented "
                          f"to <b>22.7%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(6956, i)} de código, {cif(9428, i)} de datos "
                          f"&middot; {cif(500, i)} rutinas &middot; comentado "
                          f"al <b>22,7 %</b>"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="hypersports3",
        grupo="konami",
        titulo="Hyper Sports 3",
        anio=1985,
        repo="https://github.com/antxiko/HyperSports3-disassembly",
        web="https://antxiko.github.io/HyperSports3-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-733",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-733",
        ),
        claim=dict(
            en="Four events and four different ways of moving the screen: a "
               "circuit that is <b>not in VRAM</b> but in two RAM windows, a "
               "runway stored twice to move half a tile at a time, half a "
               "sheet of ice <b>mirrored by hand</b>, and a cyclist who is "
               "<b>not a sprite but four tiles</b> with eight one-pixel "
               "copies. Plus a demo nobody plays: <b>it is a recording</b>.",
            es="Cuatro pruebas y cuatro maneras distintas de mover la "
               "pantalla: un circuito que <b>no está en la VRAM</b> sino en "
               "dos ventanas de la RAM, una pista guardada dos veces para "
               "moverse medio tile cada vez, medio campo de hielo <b>espejado "
               "a mano</b> y un ciclista que <b>no es un sprite sino cuatro "
               "casillas</b> con ocho copias corridas un píxel. Y una "
               "demostración que no la juega nadie: <b>está grabada</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(14410, i)} of code, {cif(18358, i)} of data "
                          f"&middot; {cif(931, i)} routines &middot; commented "
                          f"to <b>34.5%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(14410, i)} de código, {cif(18358, i)} de datos "
                          f"&middot; {cif(931, i)} rutinas &middot; comentado "
                          f"al <b>34,5 %</b>"),
        ),
        nota=dict(
            en="The world records live in <b>RAM</b>, because the game "
               "overwrites them.",
            es="Los récords del mundo viven en la <b>RAM</b>, porque el juego "
               "los sobrescribe.",
        ),
    ),
    dict(
        clave="gamemaster",
        grupo="konami",
        titulo="Konami&rsquo;s Game Master",
        anio=1986,
        repo="https://github.com/antxiko/GameMaster-disassembly",
        web="https://antxiko.github.io/GameMaster-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 16 KB cartridge &middot; RC-735",
            es="Konami &middot; MSX &middot; cartucho de 16 KB &middot; RC-735",
        ),
        claim=dict(
            en="Not a game: the <b>cheat cartridge</b>. It plugs in beside "
               "another one, works out which game it is by <b>adding up 256 "
               "bytes</b> of its ROM, and patches that game&rsquo;s start-up "
               "<b>in RAM</b> to take over its interrupt. Its &ldquo;cheat "
               "active&rdquo; light is <b>the CAPS LED</b>.",
            es="No es un juego: es el <b>cartucho de trucos</b>. Se enchufa "
               "junto a otro, averigua qué juego es <b>sumando 256 bytes</b> "
               "de su ROM, y le parchea el arranque <b>en la RAM</b> para "
               "quedarse con su interrupción. Su aviso de truco activo es "
               "<b>el LED de CAPS</b>.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(10522, i)} of code, {cif(5862, i)} of data "
                          f"&middot; {cif(663, i)} routines &middot; commented "
                          f"to <b>22,1 %</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(10522, i)} de código, {cif(5862, i)} de datos "
                          f"&middot; {cif(663, i)} rutinas &middot; comentado "
                          f"al <b>22,1 %</b>"),
        ),
        nota=dict(
            en="The only commercial MSX cartridge whose entire job is to read "
               "and modify another cartridge. It recognises <b>28 games</b>.",
            es="El único cartucho comercial de MSX cuyo trabajo entero "
               "consiste en leer y modificar otro cartucho. Reconoce "
               "<b>28 juegos</b>.",
        ),
    ),
    dict(
        clave="goonies",
        grupo="konami",
        titulo="The Goonies",
        anio=1986,
        repo="https://github.com/antxiko/Goonies-disassembly",
        web="https://antxiko.github.io/Goonies-disassembly/",
        meta=dict(
            en="Konami &middot; MSX &middot; 32 KB cartridge &middot; RC-734",
            es="Konami &middot; MSX &middot; cartucho de 32 KB &middot; RC-734",
        ),
        claim=dict(
            en="<b>A hundred rooms and not one repeats</b>, in 32 KB, and none "
               "of them is drawn: each room is eighty bytes pointing at 8x4 "
               "tile blocks, and those blocks <b>share tails</b> and can be "
               "asked for mirrored. And the name of each round <b>is its own "
               "password</b>: the very bytes that paint the caption are the "
               "ones you type to get there.",
            es="<b>Cien salas y ninguna se repite</b>, en 32 KB, y ni una está "
               "dibujada: cada sala son ochenta bytes que apuntan a bloques de "
               "8x4 casillas, y esos bloques <b>comparten cola</b> y se piden "
               "espejados. Y el nombre de cada ronda <b>es a la vez su "
               "contraseña</b>: los mismos bytes que pintan el rótulo son los "
               "que se teclean para llegar allí.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(17422, i)} of code, {cif(15346, i)} of data "
                          f"&middot; {cif(1176, i)} routines &middot; commented "
                          f"to <b>36.9%</b>"),
            es=lambda i: (f"{cif(32768, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(17422, i)} de código, {cif(15346, i)} de datos "
                          f"&middot; {cif(1176, i)} rutinas &middot; comentado "
                          f"al <b>36,9 %</b>"),
        ),
        nota=dict(
            en="All <b>one hundred rooms</b> drawn from the ROM, and "
               "<b>64,000 tiles in 2,983 bytes</b>.",
            es="Las <b>cien salas</b> dibujadas desde la ROM, y <b>64.000 "
               "casillas en 2.983 bytes</b>.",
        ),
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
                          f"&middot; {cif(562, i)} routines &middot; commented "
                          f"to <b>24.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(7981, i)} de código, {cif(8403, i)} de datos "
                          f"&middot; {cif(562, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(337, i)} routines &middot; commented to <b>24.5%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9467, i)} de código, {cif(6917, i)} de datos "
                          f"&middot; {cif(337, i)} rutinas &middot; comentado al <b>24,5 %</b>"),
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
                          f"&middot; {cif(675, i)} routines &middot; commented to <b>23.1%</b>"),
            es=lambda i: (f"{cif(16384, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(9099, i)} de código, {cif(7285, i)} de datos "
                          f"&middot; {cif(675, i)} rutinas &middot; comentado al <b>23,1 %</b>"),
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
                          f"&middot; {cif(1308, i)} routines &middot; commented at "
                          f"<b>33.0%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(58334, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(20299, i)} de código, {cif(37597, i)} de datos "
                          f"&middot; {cif(1308, i)} rutinas &middot; comentado "
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
                          f"&middot; {cif(1540, i)} routines &middot; commented "
                          f"to <b>23.4%</b> &middot; <b>12</b> maps"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(25471, i)} de código, {cif(105601, i)} de datos "
                          f"&middot; {cif(1540, i)} rutinas &middot; comentado "
                          f"al <b>23,4 %</b> &middot; <b>12</b> mapas"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="f1spirit",
        grupo="konami",
        titulo="F-1 Spirit &mdash; The Way to Formula 1",
        anio=1987,
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
            en=lambda i: (f"{cif(131072, i)} bytes &middot; <b>100%</b> explained "
                          f"&middot; reassembles <b>byte for byte</b> &middot; "
                          f"{cif(31591, i)} of code, {cif(99481, i)} of data "
                          f"&middot; {cif(1953, i)} routines &middot; commented to "
                          f"<b>24.2%</b> &middot; "
                          f"<b>21</b> circuits"),
            es=lambda i: (f"{cif(131072, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(31591, i)} de código, {cif(99481, i)} de datos "
                          f"&middot; {cif(1953, i)} rutinas &middot; comentado al "
                          f"<b>24,2 %</b> &middot; "
                          f"<b>21</b> circuitos"),
        ),
        nota=dict(en=None, es=None),
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
                          f"code, commented to <b>37.7%</b> &middot; {cif(1566, i)} bytes "
                          f"unidentified"),
            es=lambda i: (f"{cif(34239, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; reensamblado y retokenizado <b>byte a byte</b> "
                          f"&middot; solo {cif(997, i)} bytes de código máquina, comentado "
                          f"al <b>37,7 %</b> "
                          f"&middot; {cif(1566, i)} bytes sin identificar"),
        ),
        nota=dict(en=None, es=None),
    ),
    dict(
        clave="trailblazer",
        grupo="ports",
        titulo="Trailblazer",
        anio=1986,
        repo="https://github.com/antxiko/Trailblazer-disassembly",
        web="https://antxiko.github.io/Trailblazer-disassembly/",
        meta=dict(
            en="Gremlin Graphics &middot; MSX &middot; cassette tape",
            es="Gremlin Graphics &middot; MSX &middot; cinta de cassette",
        ),
        claim=dict(
            en="A track in perspective that is <b>drawn nowhere at all</b>: the "
               "routine that paints it <b>rewrites itself</b> on every row with "
               "the pixels it needs, and what is stored are fourteen lists of "
               "indices into a table of rows. Five bands repainted at five "
               "different rates make the depth &mdash; no division, no table, "
               "not one multiply.",
            es="Una pista en perspectiva que <b>no está dibujada en ninguna "
               "parte</b>: la rutina que la pinta <b>se reescribe a sí misma</b> "
               "cada fila con los píxeles que le tocan, y lo que hay guardado "
               "son catorce listas de índices a una tabla de filas. Cinco "
               "bandas repintadas a cinco ritmos distintos hacen la profundidad "
               "&mdash;sin división, sin tabla y sin una sola multiplicación&mdash;.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(38299, i)} bytes &middot; <b>0</b> unexplained "
                          f"&middot; the tape reassembles <b>byte for byte</b> "
                          f"&middot; {cif(6556, i)} of code, {cif(31743, i)} of "
                          f"data &middot; {cif(355, i)} routines &middot; "
                          f"commented to <b>30.8%</b>"),
            es=lambda i: (f"{cif(38299, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; la cinta reensambla <b>byte a byte</b> "
                          f"&middot; {cif(6556, i)} de código, {cif(31743, i)} de "
                          f"datos &middot; {cif(355, i)} rutinas &middot; "
                          f"comentado al <b>30,8 %</b>"),
        ),
        nota=dict(
            en="The loader does not read the tape: it <b>builds a bridge on the "
               "stack</b> and rewrites it three times.",
            es="El cargador no lee la cinta: <b>monta un puente en la pila</b> y "
               "se lo reescribe tres veces.",
        ),
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
                          f"byte</b> &middot; {cif(1148, i)} routines &middot; commented to "
                          f"<b>31.2%</b>"),
            es=lambda i: (f"{cif(93861, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; <b>cinco listados</b>, todos <b>byte a byte</b> "
                          f"&middot; {cif(1148, i)} rutinas &middot; comentado al "
                          f"<b>31,2 %</b>"),
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
                          f"{cif(553, i)} routines, {cif(73, i)} data blocks "
                          f"&middot; commented to <b>35.8%</b> "
                          f"&middot; {cif(29, i)} screens drawn from the binary"),
            es=lambda i: (f"{cif(40449, i)} bytes &middot; <b>100 %</b> explicado "
                          f"&middot; reensambla <b>byte a byte</b> &middot; "
                          f"{cif(553, i)} rutinas, {cif(73, i)} bloques de datos "
                          f"&middot; comentado al <b>35,8 %</b> "
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
                          f"{cif(38057, i)} of data &middot; commented to <b>32.7%</b>"),
            es=lambda i: (f"{cif(42645, i)} bytes en el bloque del juego &middot; "
                          f"<b>0</b> sin explicar &middot; los módulos reensamblan "
                          f"<b>byte a byte</b> y la cinta regenerada tiene el "
                          f"<b>mismo sha256</b> &middot; {cif(4588, i)} de código, "
                          f"{cif(38057, i)} de datos &middot; comentado al <b>32,7 %</b>"),
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
                          f"&middot; {cif(766, i)} routines &middot; commented at "
                          f"<b>29.7%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(62261, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>cinco listados</b>, todos <b>byte a byte</b> "
                          f"&middot; {cif(11814, i)} de código, {cif(50191, i)} de datos "
                          f"&middot; {cif(766, i)} rutinas &middot; comentado al "
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
                          f"{cif(733, i)} routines &middot; commented at "
                          f"<b>26.7%</b>, no routine below 10%"),
            es=lambda i: (f"{cif(66016, i)} bytes &middot; <b>0</b> sin explicar "
                          f"&middot; <b>cinco listados</b>, la cinta entera "
                          f"<b>byte a byte</b> &middot; {cif(15504, i)} de "
                          f"código, {cif(50512, i)} de datos &middot; "
                          f"{cif(733, i)} rutinas &middot; comentado al "
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


def rc_de(p):
    """El numero de catalogo del cartucho, o None si no lleva.

    Sale del campo 'meta', que es donde ya esta escrito -"RC-743"- para que no
    haya que apuntarlo dos veces y se puedan desincronizar.
    """
    m = re.search(r"RC-(\d+)", p["meta"]["es"])
    return int(m.group(1)) if m else None


def del_grupo(gid):
    """Los juegos de un grupo, y los de Konami POR NUMERO DE CATALOGO.

    Konami numero sus cartuchos de MSX del RC-700 en adelante y ese numero es
    casi el orden en que salieron, asi que ordenar por el cuenta la historia
    del catalogo en vez del orden en que se fueron desmontando aqui.

    La regla es de datos y no una lista a mano: se ordena el grupo en el que
    TODOS los juegos llevan RC, que hoy es Konami y solo Konami -los otros dos
    grupos no son de Konami y no tienen catalogo-. Si algun dia entra un juego
    de Konami sin RC, el grupo vuelve al orden en que esta escrito en vez de
    colar ese juego al principio o al final por un valor inventado.
    """
    ps = [p for p in DESENSAMBLADOS if p.get("grupo") == gid]
    rcs = [rc_de(p) for p in ps]
    if ps and all(rc is not None for rc in rcs):
        return [p for _rc, _i, p in sorted(zip(rcs, range(len(ps)), ps))]
    return ps


def es_cinta(p):
    return "cinta" in p["meta"]["es"]


# LOS PARCHES. Otra clase de proyecto: aqui no se documenta un cartucho, se
# MODIFICA. Van en su propia seccion y NO cuentan en las cifras de la serie de
# desensamblados, que son de juegos desmontados.
PARCHES = [
    dict(
        clave="galious-yamanooto",
        titulo="The Maze of Galious &mdash; saves on the Yamanooto",
        anio=1987,
        repo="https://github.com/antxiko/Galious-Yamanooto-Patch",
        web="https://antxiko.github.io/Galious-Yamanooto-Patch/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB cartridge &middot; Yamanooto patch, unofficial",
            es="Konami &middot; MSX &middot; cartucho de 128 KB &middot; parche para el Yamanooto, extraoficial",
        ),
        claim=dict(
            en=("The game keeps your progress in a <b>45-letter password</b> that"
               " you have to write down. With the patch, in the password room "
               "you pick <b>one of three slots</b> and the game is saved to the "
               "cartridge&rsquo;s flash. On the title screen, L no longer takes "
               "you to the typing screen: you get the slot menu. What gets saved"
               " is those same 45 letters, and <b>the game checks them with its "
               "own checksum</b>, as if they had been typed."),
            es=("El juego guarda la partida en una <b>contraseña de 45 letras</b>"
               " que hay que apuntar a mano. Con el parche, en la sala de la "
               "contraseña se elige <b>un slot de los tres</b> y la partida se "
               "graba en la flash del cartucho. En el título, la L ya no lleva a"
               " teclear: sale el menú de slots. Lo que se graba son esas mismas"
               " 45 letras y <b>el juego las comprueba con su propia suma</b>, "
               "como si se tecleasen."),
        ),
        datos=dict(
            en=lambda i: ("<b>87</b> bytes changed in <b>36</b> stretches &middot; <b>8 "
               "KB</b> driver &middot; 3 slots in <b>one 64 KB sector</b> "
               "&middot; no ROM distributed"),
            es=lambda i: ("<b>87</b> bytes cambiados en <b>36</b> tramos &middot; driver de "
               "<b>8 KB</b> &middot; 3 slots en <b>un sector de 64 KB</b> "
               "&middot; no se distribuye ninguna ROM"),
        ),
        nota=dict(
            en="tested in openMSX and on a real MSX with a Yamanooto, by pabibiris",
            es="probado en openMSX y en un MSX real con un Yamanooto, por pabibiris",
        ),
    ),
    dict(
        clave="metalgear-yamanooto",
        titulo="Metal Gear &mdash; saves on the Yamanooto",
        anio=1987,
        repo="https://github.com/antxiko/MetalGear-Yamanooto-Patch",
        web="https://antxiko.github.io/MetalGear-Yamanooto-Patch/",
        meta=dict(
            en="Konami &middot; MSX &middot; 128 KB cartridge &middot; Yamanooto patch, unofficial",
            es="Konami &middot; MSX &middot; cartucho de 128 KB &middot; parche para el Yamanooto, extraoficial",
        ),
        claim=dict(
            en=("Metal Gear saves to <b>tape</b>. The patch redirects the "
               "game&rsquo;s <b>20 calls</b> to the tape BIOS to a <b>virtual "
               "tape</b> in the cartridge&rsquo;s flash: the file name, "
               "SKIP/FOUND, VERIFY and the retries are still the game&rsquo;s "
               "own. It holds <b>3 saves</b>."),
            es=("Metal Gear graba en <b>cinta</b>. El parche desvía las <b>20 "
               "llamadas</b> del juego a la BIOS de la cinta hacia una <b>cinta "
               "virtual</b> en la flash del cartucho: el nombre del fichero, el "
               "SKIP/FOUND, el VERIFY y los reintentos siguen siendo los del "
               "juego. Caben <b>3 partidas</b>."),
        ),
        datos=dict(
            en=lambda i: ("<b>109</b> bytes changed in <b>34</b> stretches &middot; <b>8 "
               "KB</b> driver &middot; one <b>64 KB</b> sector &middot; no ROM "
               "distributed"),
            es=lambda i: ("<b>109</b> bytes cambiados en <b>34</b> tramos &middot; driver de"
               " <b>8 KB</b> &middot; un sector de <b>64 KB</b> &middot; no se "
               "distribuye ninguna ROM"),
        ),
        nota=dict(
            en="tested in openMSX on 2026-07-05: save at an elevator, switch off and load",
            es="probado en openMSX el 2026-07-05: grabar en un ascensor, apagar y cargar",
        ),
    ),
    dict(
        clave="metalgear2-yamanooto",
        titulo="Metal Gear 2: Solid Snake &mdash; saves on the Yamanooto",
        anio=1990,
        repo="https://github.com/antxiko/MetalGear2-Yamanooto-Patch",
        web="https://antxiko.github.io/MetalGear2-Yamanooto-Patch/",
        meta=dict(
            en="Konami &middot; MSX2 &middot; 512 KB SCC cartridge &middot; Yamanooto patch, unofficial",
            es="Konami &middot; MSX2 &middot; cartucho de 512 KB con SCC &middot; parche para el Yamanooto, extraoficial",
        ),
        claim=dict(
            en=("Metal Gear 2 saves to the <b>Game Master 2</b> or to disk. The "
               "patch makes it believe the Game Master 2 is plugged in and "
               "<b>answers its calls itself</b>, writing the game&rsquo;s "
               "<b>three files</b> (SNAK1, SNAK2 and SNAK3) to the "
               "cartridge&rsquo;s flash. No Game Master 2, no disk drive."),
            es=("Metal Gear 2 graba en el <b>Game Master 2</b> o en disco. El "
               "parche le hace creer que tiene el Game Master 2 al lado y "
               "<b>contesta él</b> a sus llamadas, escribiendo en la flash del "
               "cartucho los <b>tres ficheros</b> del juego (SNAK1, SNAK2 y "
               "SNAK3). Ni Game Master 2 ni disquetera."),
        ),
        datos=dict(
            en=lambda i: ("<b>39</b> bytes changed in <b>3</b> stretches &middot; <b>8 "
               "KB</b> driver &middot; one <b>64 KB</b> sector &middot; no ROM "
               "distributed"),
            es=lambda i: ("<b>39</b> bytes cambiados en <b>3</b> tramos &middot; driver de "
               "<b>8 KB</b> &middot; un sector de <b>64 KB</b> &middot; no se "
               "distribuye ninguna ROM"),
        ),
        nota=dict(
            en="tested in openMSX",
            es="probado en openMSX",
        ),
    ),
    dict(
        clave="dunkshot-msx2",
        titulo="Dunk Shot &mdash; MSX2 patch",
        anio=1986,
        repo="https://github.com/antxiko/DunkShot-MSX2-Patch",
        web="https://antxiko.github.io/DunkShot-MSX2-Patch/",
        meta=dict(
            en="HAL Laboratory &middot; MSX2 &middot; 32 KB cartridge &middot; "
               "IPS patch, unofficial",
            es="HAL Laboratory &middot; MSX2 &middot; cartucho de 32 KB &middot; "
               "parche IPS, extraoficial",
        ),
        claim=dict(
            en="Every player is four sprites and the MSX draws four per line, "
               "so the game <b>sorts them by depth and shows the list and its "
               "reverse on alternate frames</b>: that is the flicker. An MSX2 "
               "draws eight. This takes the game to <b>SCREEN 4</b>, puts the "
               "sprite colour table and the attributes in the only free 1 KB "
               "block of VRAM and always shows the sorted list. The new code lives in "
               "the filler and in <b>three orphan routines</b> of the cartridge, "
               "not one pattern moves, and <b>on a first-generation MSX it plays as the "
               "original</b>.",
            es="Cada jugador son cuatro sprites y el MSX pinta cuatro por "
               "línea, así que el juego <b>los ordena por profundidad y enseña "
               "la lista y su inversa en cuadros alternos</b>: ese es el "
               "parpadeo. Un MSX2 pinta ocho. Esto lleva el juego a <b>SCREEN "
               "4</b>, pone la tabla de colores de sprite y los atributos en el "
               "único bloque de 1 KB libre de la VRAM y enseña siempre la lista ordenada. El "
               "código nuevo vive en el relleno y en <b>tres rutinas "
               "huérfanas</b> del cartucho, no se mueve ni un patrón, y <b>en un "
               "MSX de primera generación se juega como el original</b>.",
        ),
        datos=dict(
            en=lambda i: ("<b>164</b> bytes changed in <b>24</b> stretches "
                          "&middot; <b>292</b>-byte IPS &middot; sprites not "
                          "drawn per frame <b>66.7 &rarr; 1.7</b> &middot; no "
                          "ROM distributed"),
            es=lambda i: ("<b>164</b> bytes cambiados en <b>24</b> tramos "
                          "&middot; IPS de <b>292</b> bytes &middot; sprites "
                          "sin pintar por cuadro <b>66,7 &rarr; 1,7</b> "
                          "&middot; no se distribuye ninguna ROM"),
        ),
        nota=dict(
            en="tested in openMSX (MSX and Philips NMS 8250); not yet on real hardware",
            es="probado en openMSX (MSX y Philips NMS 8250); todavía no en una máquina real",
        ),
    ),
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
            en=lambda i: (f"{cif(12103, i)} bytes changed in <b>46</b> blocks "
                          f"&middot; <b>0</b> outside them &middot; "
                          f"{cif(12511, i)}-byte IPS &middot; <b>20</b> tutorial "
                          f"screens &middot; no ROM distributed"),
            es=lambda i: (f"{cif(12103, i)} bytes cambiados en <b>46</b> bloques "
                          f"&middot; <b>0</b> fuera de ellos &middot; IPS de "
                          f"{cif(12511, i)} bytes &middot; <b>20</b> pantallas de "
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
            en="Araubi asked for three things on the forum and six came out. The "
               "enemy was invisible because the loop that plants units on the map "
               "<b>stops one slot before the enemy side begins</b>; a unit&rsquo;s "
               "qualities were adjectives with no numbers; and the Ring&rsquo;s "
               "deadline &mdash;a countdown of months the game never shows&mdash; "
               "now sits beside the ring in the bearer&rsquo;s sheet. The enemy "
               "also got <b>the Eye of Sauron</b>, because a free bit in the map "
               "byte was all it took to tell the two sides apart. The new code "
               "lives inside the <b>ZX beeper engine this port brought across and "
               "never calls</b>. And the <b>whole map is repainted</b>: 122 of the "
               "128 tiles, drawn in a PNG and turned into patch entries by the "
               "tool itself.",
            es="Araubi pidió tres cosas en el foro y salieron seis. Las unidades "
               "enemigas no se veían porque el bucle que las siembra en el mapa "
               "<b>para una ranura antes de que empiece el bando enemigo</b>; las "
               "cualidades de una unidad eran adjetivos sin número; y el plazo del "
               "Anillo &mdash;una cuenta atrás de meses que el juego no enseña&mdash; "
               "sale ya al lado del anillo, en la ficha del portador. Las enemigas "
               "llevan además <b>el Ojo de Sauron</b>, porque bastaba un bit libre "
               "del byte de mapa para distinguir los dos bandos. El código nuevo "
               "vive dentro del <b>motor de altavoz del ZX que esta conversión "
               "trajo y no llama nadie</b>. Y el <b>mapa viene repintado entero</b>: "
               "122 de los 128 tiles, dibujados en un PNG y convertidos en entradas "
               "del parche por la propia herramienta.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(1396, i)} bytes changed in <b>130</b> "
                          "places &middot; <b>0</b> outside the table &middot; "
                          f"<b>0</b> shifted &middot; {cif(1718, i)}-byte IPS "
                          "&middot; no tape distributed"),
            es=lambda i: (f"{cif(1396, i)} bytes cambiados en <b>130</b> "
                          "sitios &middot; <b>0</b> fuera de la tabla &middot; "
                          f"<b>0</b> desplazados &middot; IPS de {cif(1718, i)} "
                          "bytes &middot; no se distribuye ninguna cinta"),
        ),
        nota=dict(
            en="playable; Araubi finished a game with the September build, nobody "
               "has with the map repainted",
            es="se juega; Araubi terminó una partida con la versión de septiembre, "
               "con el mapa repintado todavía nadie",
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
HERRAMIENTAS = [
    dict(
        clave="serie-db",
        titulo="La base de datos de la serie",
        anio=2026,
        repo="https://github.com/antxiko/MSX-disassembly-database",
        web="https://antxiko.github.io/MSX-disassembly-database/",
        meta=dict(
            en="49 projects &middot; measured, not copied &middot; 28 tests",
            es="49 proyectos &middot; medido, no copiado &middot; 28 pruebas",
        ),
        claim=dict(
            en="What comes out of looking at all of them at once. Every figure "
               "here is <b>measured again</b> against the listings the "
               "repositories publish today, never copied from a README &mdash; "
               "and that alone found <b>four cards quoting a density their own "
               "listing no longer gives</b>. It also shows that the joystick "
               "read is <b>thirty-six identical bytes in eighteen cartridges "
               "going by twelve different names</b>, and that seventeen "
               "cartridges carry Konami&rsquo;s hidden mark, all seventeen "
               "matching the catalogue number their card publishes.",
            es="Lo que sale de mirarlos todos a la vez. Cada cifra está "
               "<b>medida otra vez</b> sobre los listados que los repositorios "
               "publican hoy, nunca copiada de un README &mdash;y sólo con eso "
               "aparecieron <b>cuatro fichas que publican una densidad que su "
               "propio listado ya no da</b>&mdash;. También enseña que la "
               "lectura de mandos son <b>treinta y seis bytes idénticos en "
               "dieciocho cartuchos con doce nombres distintos</b>, y que "
               "diecisiete cartuchos llevan la marca oculta de Konami, los "
               "diecisiete con el número de catálogo que publica su ficha.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(249851, i)} instructions &middot; "
                          f"{cif(81234, i)} comments &middot; <b>32.5 %</b> "
                          f"across the series &middot; <b>0</b> routines below "
                          f"10 % &middot; {cif(1465115, i)} bytes of binary"),
            es=lambda i: (f"{cif(249851, i)} instrucciones &middot; "
                          f"{cif(81234, i)} comentarios &middot; <b>32,5 %</b> "
                          f"en toda la serie &middot; <b>0</b> rutinas por "
                          f"debajo del 10 % &middot; {cif(1465115, i)} bytes "
                          f"de binario"),
        ),
        nota=dict(en="", es=""),
    ),
]

# --------------------------------------------------------------------------
# LAS NOVEDADES: de aqui salen los dos feeds Atom (feed.xml y es/feed.xml). Una
# entrada por publicacion, la mas nueva ARRIBA, escrita a mano en el mismo
# commit que pone el proyecto en la portada. Reglas:
#   - 'id' no se toca NUNCA despues de publicarlo: es la identidad de la
#     entrada para el lector; si cambia, todos los lectores la ensenan otra vez
#     como nueva. Y no se reutiliza para otra noticia.
#   - 'fecha' en RFC 3339 con huso explicito (2026-09-09T18:00:00+02:00). Nada
#     de horas locales sin huso ni de strftime con nombres de mes. Las de abajo
#     estan MEDIDAS, no inventadas: el primer commit que anadio docs/index.html
#     en el repositorio de cada proyecto; y en los dos parches, que heredan el
#     historial del desensamblado del que se clonaron, el commit de esta portada
#     que los puso en ella.
#   - 'clave' es el proyecto del que habla; su web es el enlace de la entrada
#     (o 'enlace', si se da).
#   - 'otras' (opcional): mas proyectos de los que habla la misma entrada,
#     cuando se publican juntos (los tres parches del Yamanooto).
#   - 'clase': "nuevo" (el proyecto se publica) o "actualiza" (algo nuevo en
#     uno ya publicado).
#   - 'titulo' y 'resumen' son opcionales, bilingues y en TEXTO PLANO. Sin
#     ellos, el titulo sale del nombre del proyecto y de su clase, y el resumen
#     de la linea de cifras de su tarjeta, que asi no se copia dos veces.
# El build para si un id se repite, una fecha no es RFC 3339, el orden no es de
# nueva a vieja, una clave no existe o un proyecto se queda sin novedad.
# --------------------------------------------------------------------------
NOVEDADES = [
    dict(id="galious-yamanooto-en-un-msx-real", clave="galious-yamanooto",
         clase="actualiza", fecha="2026-10-03T21:23:23+02:00",
         titulo=dict(en="The Maze of Galious on the Yamanooto, tested on a real MSX",
                     es="The Maze of Galious en el Yamanooto, probado en un MSX real"),
         resumen=dict(
             en="pabibiris tested the save patch on a real MSX with a real "
                "Yamanooto and approves it.",
             es="pabibiris ha probado el parche de las partidas en un MSX real "
                "con un Yamanooto real y lo da por bueno."),
    ),
    dict(id="yamanooto-sin-menu", clave="galious-yamanooto",
         otras=["metalgear-yamanooto", "metalgear2-yamanooto"],
         clase="actualiza", fecha="2026-10-03T21:08:11+02:00",
         enlace="https://antxiko.github.io/#patches",
         titulo=dict(en="The Yamanooto patches boot on their own, with no menu",
                     es="Los parches del Yamanooto arrancan solos, sin menú"),
         resumen=dict(
             en="The image each one builds no longer carries nPackR's menu: the "
                "game goes at the start of the flash and boots straight away. "
                "Galious and Metal Gear now switch banks through the Konami SCC "
                "registers, the mode a Yamanooto starts in.",
             es="La imagen que monta cada uno ya no lleva el menú de nPackR: el "
                "juego va al principio de la flash y arranca directamente. "
                "Galious y Metal Gear cambian de banco con los registros Konami "
                "SCC, el modo con el que arranca el Yamanooto."),
    ),
    dict(id="partidas-en-el-yamanooto", clave="galious-yamanooto",
         otras=["metalgear-yamanooto", "metalgear2-yamanooto"],
         clase="nuevo", fecha="2026-10-03T20:33:16+02:00",
         enlace="https://antxiko.github.io/#patches",
         titulo=dict(en="Saves on the Yamanooto: Galious, Metal Gear and Metal Gear 2",
                     es="Partidas en el Yamanooto: Galious, Metal Gear y Metal Gear 2"),
         resumen=dict(
             en="Three patches that save the game to the cartridge&rsquo;s flash "
                "instead of to a password, a tape or the Game Master 2. Each one "
                "builds, from your own ROM, the image ready to flash.",
             es="Tres parches que guardan la partida en la flash del cartucho en "
                "vez de en contraseña, cinta o Game Master 2. Cada uno monta, con "
                "tu ROM, la imagen lista para grabar."),
    ),
    dict(id="galious", clave="galious",
         clase="nuevo", fecha="2026-10-03T18:39:57+02:00",
         titulo=dict(en="The Maze of Galious: the castle, ten worlds and 321 rooms, taken apart",
                     es="The Maze of Galious: el castillo, diez mundos y 321 salas, desmontado"),
         resumen=dict(
             en="Konami's 1987 MSX cartridge (Knightmare II), 100% explained and "
                "commented to 40.1%. All 321 rooms laid out by their neighbours, "
                "the ten bosses, Popolon and Aphrodite, the items and the shops, "
                "drawn from the ROM and checked against openMSX down to zero; "
                "plus ZEUS in the pause, the cup on F2 and the black rooms that "
                "are hints and shops.",
             es="El cartucho MSX de Konami de 1987 (Knightmare II), explicado al "
                "100 % y comentado al 40,1 %. Las 321 salas colocadas por sus "
                "vecinas, los diez jefes, Popolon y Afrodita, los objetos y las "
                "tiendas, dibujados desde la ROM y cotejados contra openMSX a "
                "cero; y ZEUS en la pausa, la taza de F2 y las salas negras que "
                "son pistas y tiendas."),
    ),
    dict(id="goemon-124-pantallas", clave="goemon",
         clase="actualiza", fecha="2026-10-02T15:32:53+02:00",
         titulo=dict(en="Ganbare Goemon!: 124 different screens, not 1,608",
                     es="Ganbare Goemon!: 124 pantallas distintas, no 1.608"),
         resumen=dict(
             en="Errata: 1,608 is the number of cells across the 49 areas; each "
                "area's grid (0x600C) reuses its screens, and there are 124 "
                "different ones.",
             es="Errata: 1.608 son las casillas de las 49 zonas; la rejilla de "
                "cada zona (0x600C) reutiliza sus pantallas, y distintas hay "
                "124."),
    ),
    dict(id="goemon", clave="goemon",
         clase="nuevo", fecha="2026-10-02T15:14:33+02:00",
         titulo=dict(en="Ganbare Goemon!: 49 areas, 21 interiors and 42 secret passages, taken apart",
                     es="Ganbare Goemon!: 49 zonas, 21 interiores y 42 pasadizos secretos, desmontado"),
         resumen=dict(
             en="Konami's 1987 MSX2 cartridge, 100% explained and commented to "
                "42.5%. The seven stages street by street, the interiors with "
                "their prices, the enemies and the 42 first-person secret "
                "passages drawn from the ROM and checked against openMSX down "
                "to zero; plus the password keywords, the pause words and the "
                "stage menu that shows up with Q*bert or the Game Master.",
             es="El cartucho MSX2 de Konami de 1987, explicado al 100 % y "
                "comentado al 42,5 %. Las siete fases calle a calle, los "
                "interiores con sus precios, los enemigos y los 42 pasadizos "
                "secretos en primera persona, dibujados desde la ROM y "
                "cotejados contra openMSX a cero; y las claves de la "
                "contrase&ntilde;a, las palabras de la pausa y el men&uacute; de "
                "fases que sale con Q*bert o el Game Master."),
    ),
    dict(id="dunkshot-msx2", clave="dunkshot-msx2", clase="nuevo",
         fecha="2026-10-02T08:40:00+02:00",
         titulo=dict(en="Dunk Shot gets its own MSX2 patch repository",
                     es="El parche MSX2 de Dunk Shot, con repositorio propio"),
         resumen=dict(
             en="The patch that takes the flicker away on an MSX2 now has its "
                "own repository and website, in the patches section: the IPS, "
                "the tool that builds it, the probe that measures it and how "
                "the game shares its sprites out. 66.7 sprites not drawn per "
                "frame on an MSX, 1.7 on the NMS 8250. Tested in openMSX; "
                "nobody has run it on real hardware yet.",
             es="El parche que quita el parpadeo en un MSX2 tiene ya repositorio "
                "y web propios, en la sección de parches: el IPS, la herramienta "
                "que lo genera, la sonda que lo mide y cómo reparte el juego sus "
                "sprites. 66,7 sprites sin pintar por cuadro en un MSX, 1,7 en "
                "el NMS 8250. Probado en openMSX; nadie lo ha pasado aún por una "
                "máquina real.")),
    dict(id="dunkshot-el-parche-msx2", clave="dunkshot",
         clase="actualiza", fecha="2026-10-02T08:30:00+02:00",
         enlace="https://antxiko.github.io/DunkShot-disassembly/THE-MSX2-PATCH.html",
         titulo=dict(en="Dunk Shot: a 164-byte patch takes the flicker away on an MSX2",
                     es="Dunk Shot: un parche de 164 bytes quita el parpadeo en un MSX2"),
         resumen=dict(
             en="The V9938 draws eight sprites per line instead of four, so "
                "the game no longer needs to share the players out: SCREEN 4, "
                "the sprite colour table at 0x3C00 and the attributes at "
                "0x3E00, in the filler and three orphan routines of the "
                "cartridge. Measured in openMSX over thirty seconds of a "
                "match: from 66.7 sprites not drawn per frame to 1.7. The "
                "same file still plays on an MSX1 as the original.",
             es="El V9938 pinta ocho sprites por línea en vez de cuatro, así "
                "que el juego ya no tiene que repartir a los jugadores: "
                "SCREEN 4, la tabla de colores de sprite en 0x3C00 y los "
                "atributos en 0x3E00, en el relleno y tres rutinas huérfanas "
                "del cartucho. Medido en openMSX sobre treinta segundos de "
                "partido: de 66,7 sprites sin pintar por cuadro a 1,7. El "
                "mismo fichero sigue jugándose en un MSX1 como el original.")),
    dict(id="dunkshot", clave="dunkshot",
         clase="nuevo", fecha="2026-10-01T19:46:17+02:00",
         titulo=dict(en="Dunk Shot: a 56-column court behind a 32-column window, taken apart",
                     es="Dunk Shot: una pista de 56 columnas tras una ventana de 32, desmontado"),
         resumen=dict(
             en="HAL Laboratory's three-on-three basketball for MSX, 100% "
                "explained and commented to 43.2%. The whole court in its three "
                "colours, the 160 poses of four sprites and six screens drawn "
                "from the ROM and checked against openMSX. The flicker is a "
                "deliberate alternation of the sprite order, the computer teams are "
                "generated by level and a team is saved to tape as a BSAVE.",
             es="El baloncesto de tres contra tres de HAL Laboratory para MSX, "
                "explicado al 100 % y comentado al 43,2 %. La pista entera en "
                "sus tres colores, las 160 poses de cuatro sprites y seis "
                "pantallas dibujadas desde la ROM y cotejadas contra openMSX. "
                "El parpadeo es una alternancia del orden de los sprites hecha a "
                "propósito, los equipos de la máquina se fabrican por nivel y "
                "un equipo se graba en cinta como un BSAVE.")),
    dict(id="hinotori-los-jefes-medidos-y-el-fenix", clave="hinotori",
         clase="actualiza", fecha="2026-09-30T23:30:00+02:00",
         titulo=dict(en="Hinotori: the room bosses checked in openMSX, and the phoenix's message",
                     es="Hinotori: los jefes de las salas, cotejados en openMSX, y el mensaje del fénix"),
         resumen=dict(
             en="Going into each of the six rooms in openMSX, the VRAM holds "
                "exactly the boss drawn from the ROM, and none of the unused "
                "figures; the stage-4 room has no boss. In the last room the "
                "phoenix appears: to fight the demon you need five heart "
                "jewels.",
             es="Entrando en cada una de las seis salas en openMSX, la VRAM "
                "lleva justo el jefe dibujado desde la ROM y ninguna de las "
                "figuras sin cargar; la sala de la fase 4 no tiene jefe. En la "
                "última sala sale el fénix: para luchar contra el demonio "
                "hacen falta cinco joyas del corazón.")),
    dict(id="hinotori-otra-version-de-cinco-jefes", clave="hinotori",
         clase="actualiza", fecha="2026-09-30T23:00:00+02:00",
         titulo=dict(en="Hinotori: the unused figures are another version of five bosses",
                     es="Hinotori: las figuras sin cargar son otra versión de cinco jefes"),
         resumen=dict(
             en="Correction: the figures published as used by nobody are, "
                "five of them, bosses of the game drawn another way: the "
                "beast, the one-eyed monster, the face, the demon and a "
                "warrior with several arms, found in 768 more bytes. Not one "
                "sprite in common with the ones the rooms load; now each one "
                "is shown next to its boss.",
             es="Corrección: de las figuras publicadas como de nadie, cinco "
                "son jefes del juego dibujados de otra manera: la bestia, el "
                "monstruo de un ojo, la cara, el demonio y un guerrero de "
                "varios brazos, sacado de otros 768 bytes. Ni un sprite en "
                "común con los que cargan las salas; ahora cada una sale al "
                "lado de su jefe.")),
    dict(id="hinotori-seis-figuras-y-los-mapas", clave="hinotori",
         clase="actualiza", fecha="2026-09-30T21:00:00+02:00",
         titulo=dict(en="Hinotori: six figures nobody uses, and the maps put right",
                     es="Hinotori: seis figuras que no usa nadie, y los mapas corregidos"),
         resumen=dict(
             en="Eighteen compressed strips that no list in the cartridge "
                "names, opened: a hunched beast, a one-eyed monster, a face, "
                "a 32x48 demon and a small warrior, none of them in the game. "
                "And the stage maps had the four rows of each block upside "
                "down: fixed, and the check against openMSX now looks at the "
                "order of the rows.",
             es="Dieciocho tiras comprimidas que no nombra ninguna lista del "
                "cartucho, abiertas: una bestia jorobada, un monstruo de un "
                "ojo, una cara, un demonio de 32x48 y un guerrero pequeño, "
                "ninguno en el juego. Y los mapas de las fases llevaban las "
                "cuatro filas de cada bloque del revés: corregido, y el cotejo "
                "con openMSX ahora mira el orden de las filas.")),
    dict(id="hinotori", clave="hinotori",
         clase="nuevo", fecha="2026-09-30T17:24:33+02:00",
         titulo=dict(en="Hinotori: the Firebird and its seventeen passwords, taken apart",
                     es="Hinotori: el pájaro de fuego y sus diecisiete contraseñas, desmontado"),
         resumen=dict(
             en="The third MSX2 in the series, 100% explained and commented to "
                "40.4%. The six stages, their rooms and the gates that join "
                "them, Gao and the enemies drawn from the ROM and checked in "
                "openMSX. With King Kong 2 next to it, it boots King Kong 2 "
                "and saves its game; fifteen of the seventeen cheats tried in "
                "play.",
             es="El tercer MSX2 de la serie, explicado al 100 % y comentado al "
                "40,4 %. Las seis fases, sus salas y las puertas que las unen, "
                "Gao y los bichos dibujados desde la ROM y cotejados en "
                "openMSX. Con King Kong 2 al lado, arranca King Kong 2 y le "
                "graba la partida; quince de los diecisiete trucos probados "
                "jugando.")),
    dict(id="qbert-el-visor-de-patrones", clave="qbert",
         clase="actualiza", fecha="2026-09-30T13:30:00+02:00",
         titulo=dict(en="Q*bert: the pattern viewer nobody calls, run",
                     es="Q*bert: el visor de patrones que no llama nadie, ejecutado"),
         resumen=dict(
             en="The twelve pieces of code the game never runs, run one by one "
                "in openMSX. The best one is a development tool left in the "
                "ROM: it fills the screen with the numbers 0 to 255 and shows "
                "every loaded tile. Built from the ROM and checked, zero bytes "
                "different.",
             es="Los doce trozos de c\u00f3digo que el juego no ejecuta nunca, "
                "ejecutados uno a uno en openMSX. El mejor es una herramienta de "
                "desarrollo que se qued\u00f3 en la ROM: llena la pantalla con los "
                "n\u00fameros 0 a 255 y ense\u00f1a todos los tiles cargados. "
                "Montado desde la ROM y cotejado, a cero bytes.")),
    dict(id="qbert", clave="qbert",
         clase="nuevo", fecha="2026-09-30T12:00:00+02:00",
         titulo=dict(en="Q*bert: cubes that roll like dice, taken apart",
                     es="Q*bert: cubos que ruedan como dados, desmontado"),
         resumen=dict(
             en="Konami's MSX Q*bert, 100% explained and commented to 78.1%. "
                "The 50 stages, the bonus stage and the duel drawn from the ROM "
                "and checked in openMSX. Five in a row clears a stage, the duel "
                "ends in rock, paper, scissors, and there is a hidden life, "
                "seen in play.",
             es="El Q*bert de Konami para MSX, explicado al 100 % y comentado al "
                "78,1 %. Las 50 fases, la bonificación y el duelo dibujados "
                "desde la ROM y cotejados en openMSX. Cinco en línea acaban la "
                "fase, el duelo se decide a piedra, papel o tijera y hay una "
                "vida escondida, vista jugando.")),
    dict(id="kingkong2", clave="kingkong2",
         clase="nuevo", fecha="2026-09-29T14:29:35+02:00",
         titulo=dict(en="King Kong 2: the island and what it hides, taken apart",
                     es="King Kong 2: la isla y lo que esconde, desmontada"),
         resumen=dict(
             en="The second MSX2 in the series. The 140 screens with their "
                "passages and removable scenery, Mitchel, the 55 enemies and "
                "five bosses painted by the VDP, drawn from the ROM and checked "
                "in openMSX. Three endings, and a level trick seen in play.",
             es="El segundo MSX2 de la serie. Las 140 pantallas con sus "
                "pasadizos y el decorado que se quita, Mitchel, los 55 enemigos "
                "y cinco jefes que pinta el VDP, dibujados desde la ROM y "
                "cotejados en openMSX. Tres finales, y un truco de nivel visto "
                "jugando.")),
    dict(id="vampirekiller-la-tienda-y-el-final", clave="vampirekiller",
         clase="actualiza", fecha="2026-09-28T22:04:33+02:00",
         titulo=dict(en="Vampire Killer: the shop, the old man, the items and the ending",
                     es="Vampire Killer: la tienda, el viejo, los objetos y el final"),
         resumen=dict(
             en="The shop window drawn from the ROM and checked against six "
                "openMSX dumps, zero dots different. The vendor is a hooded old "
                "man whose colour tells what comes. The 29 items with what each "
                "one does, and the ending with its story and its credits, read "
                "from the ROM.",
             es="La ventana de la tienda dibujada desde la ROM y cotejada contra "
                "seis volcados de openMSX, cero puntos distintos. El vendedor es "
                "un viejo encapuchado cuyo color dice lo que toca. Los 29 "
                "objetos con lo que hace cada uno, y el final con su historia y "
                "sus créditos, leídos de la ROM.")),
    dict(id="vampirekiller-los-vendedores", clave="vampirekiller",
         clase="actualiza", fecha="2026-09-28T19:12:12+02:00",
         titulo=dict(en="Vampire Killer: the vendors count hits, and the books set the prices",
                     es="Vampire Killer: los vendedores cuentan golpes, y los libros ponen los precios"),
         resumen=dict(
             en="What a vendor does depends on how many times you hit him, not "
                "on your visits; dying resets the count. The white book makes "
                "the shop cheaper and the red one dearer: full life costs 15, "
                "40 or 80 hearts. Seen in openMSX, one vendor of each class.",
             es="Lo que hace un vendedor depende de cuántas veces se le pega, "
                "no de las visitas; al morir, la cuenta vuelve a cero. El libro "
                "blanco abarata la tienda y el rojo la encarece: la vida llena "
                "cuesta 15, 40 u 80 corazones. Visto en openMSX, un vendedor "
                "de cada clase.")),
    dict(id="vampirekiller", clave="vampirekiller",
         clase="nuevo", fecha="2026-09-28T18:12:53+02:00",
         titulo=dict(en="Vampire Killer: Dracula's castle, taken apart",
                     es="Vampire Killer: el castillo de Drácula, desmontado"),
         resumen=dict(
             en="The first MSX2 in the series. The 156 rooms with what they "
                "hide, Simon, the enemies and the six bosses, drawn from the "
                "ROM and checked in openMSX. There are 33 hidden vendors who "
                "do not always sell.",
             es="El primer MSX2 de la serie. Las 156 habitaciones con lo que "
                "esconden, Simon, los enemigos y los seis jefes, dibujados "
                "desde la ROM y cotejados en openMSX. Hay 33 vendedores "
                "escondidos que no siempre venden.")),
    dict(id="penguinadventure-las-botas", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-28T15:35:08+02:00",
         titulo=dict(en="Penguin Adventure: the red boots do show up",
                     es="Penguin Adventure: las botas rojas sí salen"),
         resumen=dict(
             en="The secrets' prizes were off by one: stage 6 gives the blue "
                "boots and stage 13 the red ones. Checked in openMSX.",
             es="Los premios de los secretos estaban corridos en uno: la fase 6 "
                "da las botas azules y la 13 las rojas. Cotejado en openMSX.")),
    dict(id="penguinadventure-las-tiendas", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-28T11:59:37+02:00",
         titulo=dict(en="Penguin Adventure: the hidden shops and the sixteen items",
                     es="Penguin Adventure: las tiendas escondidas y los dieciséis artículos"),
         resumen=dict(
             en="The three shopkeepers drawn from the tables, each with his "
                "greeting and his farewell: the usual one, the one who charges "
                "double and Santa Claus, who gives one thing away. The sixteen "
                "items with what each one does, read from whoever checks its "
                "flag. Checked against 14 openMSX dumps, zero differences.",
             es="Los tres tenderos dibujados desde las tablas, cada uno con su "
                "saludo y su despedida: el de siempre, el que cobra el doble y "
                "Santa Claus, que regala una cosa. Los dieciséis artículos con "
                "lo que hace cada uno, leído de quien mira su bandera. "
                "Cotejado contra 14 volcados de openMSX, cero diferencias.")),
    dict(id="penguinadventure-el-mapa", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-28T11:06:18+02:00",
         titulo=dict(en="Penguin Adventure: the map before every stage",
                     es="Penguin Adventure: el mapa de antes de cada fase"),
         resumen=dict(
             en="The map before every stage, drawn from its tables and checked "
                "against the emulator, warps included.",
             es="El mapa de antes de cada fase, dibujado desde sus tablas y "
                "cotejado contra el emulador, con los atajos.")),
    dict(id="penguinadventure-la-pelea", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-26T23:16:10+02:00",
         titulo=dict(en="Penguin Adventure: the fight with the dinosaur",
                     es="Penguin Adventure: la pelea con el dinosaurio"),
         resumen=dict(
             en="The fight at the end of every third stage, drawn from the "
                "tables: the four blocks of ice that fall, the dinosaur moving "
                "between five columns and always looking at the penguin, what "
                "it throws, and after twenty hits the ice cracking and the "
                "dinosaur sinking. Also what moves in the scenes: the penguin "
                "walking in, the jump in the good ending, the apple and the "
                "crying. Checked against thousands of openMSX dumps with zero "
                "differences.",
             es="La pelea del final de cada tres fases, dibujada desde las "
                "tablas: los cuatro bloques de hielo que caen, el dinosaurio "
                "que va entre cinco columnas y siempre mira al pingüino, lo que "
                "lanza, y a los veinte aciertos el hielo que se agrieta y el "
                "dinosaurio que se hunde. Y lo que se mueve en las escenas: el "
                "pingüino que entra, el salto del final bueno, la manzana y el "
                "llanto. Cotejado con miles de volcados de openMSX, cero "
                "diferencias.")),
    dict(id="penguinadventure-pingu-en-el-final-malo", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-26T22:14:25+02:00",
         titulo=dict(en="Penguin Adventure: the penguin in the bad ending",
                     es="Penguin Adventure: Pingu en el final malo"),
         resumen=dict(
             en="The drawing of the scenes was missing what is on screen when "
                "the message appears: in the bad ending, the penguin seen from "
                "behind, crying in front of the king, and in the tree, the "
                "apple that has fallen. Now each scene carries exactly the "
                "sprites of a real frame, checked against openMSX with zero "
                "differences, and in the good ending the penguin stands whole "
                "on the carpet.",
             es="Al dibujo de las escenas le faltaba lo que hay en pantalla "
                "cuando sale el mensaje: en el final malo, el pingüino de "
                "espaldas llorando delante del rey, y en el árbol, la manzana "
                "que ha caído. Ahora cada escena lleva justo los sprites de un "
                "cuadro de verdad, cotejados con openMSX con cero diferencias, "
                "y en el final bueno el pingüino sale entero sobre la "
                "alfombra.")),
    dict(id="penguinadventure-arbol-y-finales", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-26T12:09:59+02:00",
         titulo=dict(en="Penguin Adventure: the tree and the two endings",
                     es="Penguin Adventure: el árbol y los dos finales"),
         resumen=dict(
             en="The three scenes after stages 12 and 24, drawn from the "
                "tables: the tree halfway through and the good and the bad "
                "endings, with their messages. The screens are painted from "
                "the middle outwards, and in the bad ending a piece of fifty "
                "bytes takes the princess's place. Checked against openMSX: "
                "zero differences.",
             es="Las tres escenas de después de las fases 12 y 24, dibujadas "
                "desde las tablas: el árbol de la mitad del camino y el final "
                "bueno y el malo, con sus mensajes. Las pantallas se pintan del "
                "centro hacia fuera, y en el final malo una pieza de cincuenta "
                "bytes ocupa el sitio de la princesa. Cotejadas con openMSX: "
                "cero diferencias.")),
    dict(id="penguinadventure-atajos-y-tiendas", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-26T12:00:43+02:00",
         titulo=dict(en="Penguin Adventure: the six warps and the 41 hidden shops",
                     es="Penguin Adventure: los seis atajos y las 41 tiendas escondidas"),
         resumen=dict(
             en="Backdrop 9 is the WARP: a flagged crevasse and pressing down "
                "take you from stage 1 to 6, 6 to 9, 9 to 12, 13 to 15, 15 to "
                "18 and 18 to 21, all six measured in openMSX. Other crevasses "
                "hide 41 shops: 18 usual, 20 that charge double and 3 with "
                "Santa Claus, who gives one item away. And a correction: space "
                "is reached by touching what flies across, not through a "
                "crevasse.",
             es="El decorado 9 es el WARP: una grieta marcada y pulsar abajo "
                "llevan de la fase 1 a la 6, de la 6 a la 9, de la 9 a la 12, de "
                "la 13 a la 15, de la 15 a la 18 y de la 18 a la 21, medidos los "
                "seis en openMSX. Otras grietas esconden 41 tiendas: 18 "
                "normales, 20 que cobran el doble y 3 de Santa Claus, que regala "
                "una cosa. Y una corrección: al espacio se sube tocando lo que "
                "cruza volando, no por una grieta.")),
    dict(id="penguinadventure-desde-las-tablas", clave="penguinadventure",
         clase="actualiza", fecha="2026-09-26T11:35:24+02:00",
         titulo=dict(en="Penguin Adventure: everything on screen, drawn from the tables",
                     es="Penguin Adventure: lo que sale en pantalla, dibujado desde las tablas"),
         resumen=dict(
             en="The penguin in its poses and terrains, the ten creatures, the "
                "dinosaur that closes every third stage, space with its "
                "meteorites and winged fish, the backdrops built whole and the "
                "twenty-four stages of each LEVEL walked step by step from "
                "their four scripts. All checked against openMSX: seven tests, "
                "zero differences. The stage diagram and the black-and-white "
                "sprite sheets are gone.",
             es="El pingüino en sus poses y terrenos, los diez bichos, el "
                "dinosaurio que cierra cada tres fases, el espacio con sus "
                "meteoritos y sus peces con alas, los decorados montados "
                "enteros y las veinticuatro fases de cada LEVEL andadas paso a "
                "paso desde sus cuatro guiones. Todo cotejado con openMSX: "
                "siete pruebas, cero diferencias. Fuera el esquema de fases y "
                "las hojas de sprites en blanco y negro.")),
    dict(id="magicaltree-nueve-fases", clave="magicaltree",
         clase="actualiza", fecha="2026-09-26T10:12:08+02:00",
         titulo=dict(en="Magical Tree: the nine stages side by side",
                     es="Magical Tree: las nueve fases, una al lado de otra"),
         resumen=dict(
             en="The nine whole trees, standing on the ground and drawn from "
                "each stage's script, now open the home page gallery and the "
                "stages section of The game; each one is still there full "
                "size.",
             es="Los nueve árboles enteros, apoyados en el suelo y dibujados "
                "desde el guion de cada fase, abren ahora la galería de la "
                "portada y la sección de las fases de El juego; cada uno sigue "
                "ahí a tamaño completo.")),
    dict(id="magicaltree-castillo", clave="magicaltree",
         clase="actualiza", fecha="2026-09-25T22:50:31+02:00",
         titulo=dict(en="Magical Tree: the castle, drawn right",
                     es="Magical Tree: el castillo, bien dibujado"),
         resumen=dict(
             en="The castle and the tree painted between stages were drawn "
                "with their columns left to right, and the cartridge paints "
                "them from the middle outwards: the castle came out "
                "scrambled. Now each column goes where 0x7629 puts it, the "
                "tree takes the colours of the stage that starts, and the "
                "castle carries its windows with the two characters and the "
                "CONGRATULATIONS sign. Checked against openMSX in nine dumps: "
                "0 bytes different.",
             es="El castillo y el árbol que se pinta entre fases estaban "
                "dibujados con las columnas de izquierda a derecha, y el "
                "cartucho los pinta del centro hacia fuera: el castillo salía "
                "revuelto. Ahora cada columna va donde la pone 0x7629, el "
                "árbol lleva los colores de la fase que empieza y el castillo "
                "sus ventanas con los dos personajes y el rótulo "
                "CONGRATULATIONS. Cotejado contra openMSX en nueve volcados: "
                "0 bytes distintos.")),
    dict(id="comicbakery", clave="comicbakery", clase="nuevo",
         fecha="2026-09-25T21:31:15+02:00"),
    dict(id="magicaltree", clave="magicaltree", clase="nuevo",
         fecha="2026-09-25T21:08:29+02:00"),
    dict(id="circus-pista-desde-las-tablas", clave="circus",
         clase="actualiza", fecha="2026-09-25T19:53:22+02:00",
         titulo=dict(en="Circus Charlie: the ring, drawn from the tables",
                     es="Circus Charlie: la pista, dibujada desde las tablas"),
         resumen=dict(
             en="The five pictures of the acts, with Charlie, his animal and "
                "the obstacles, no longer come from running the cartridge: "
                "tools/pista.py rewrites the game frame from the cartridge's "
                "own tables, moving objects, poses and start-ups, and against "
                "43 openMSX dumps it gives zero bytes of RAM and VRAM "
                "different.",
             es="Las cinco imágenes de las atracciones, con Charlie, su animal "
                "y los obstáculos, ya no salen de ejecutar el cartucho: "
                "tools/pista.py reescribe el cuadro de partida desde las "
                "tablas del propio cartucho, móviles, poses y arranques, y "
                "contra 43 volcados de openMSX da cero bytes de RAM y VRAM "
                "distintos.")),
    dict(id="circus", clave="circus", clase="nuevo",
         fecha="2026-09-25T15:49:33+02:00"),
    dict(id="goonies-issue3-el-mapa", clave="goonies",
         clase="actualiza", fecha="2026-09-24T18:33:28+02:00",
         titulo=dict(en="The Goonies: the map section, redone",
                     es="The Goonies: la sección del mapa, rehecha"),
         resumen=dict(
             en="As theNestruo asked in issue #3: the four rooms of each level "
                "drawn touching, with no caption between them; the cages open, "
                "showing the friend or the potion, with their padlocks on; "
                "under each level only what the picture cannot say, the keys, "
                "what each cage holds, which item is hidden and where each "
                "skull door leads; and the five round minimaps at 1:1, with "
                "the lines behind the levels. On the way: the hidden item's "
                "index matches the inventory table for all 23, and the caged "
                "friends add up to seven per round, which is what the exit "
                "door asks for.",
             es="Como pedía theNestruo en el issue #3: las cuatro salas de "
                "cada nivel pegadas, sin rótulo en medio; las jaulas abiertas, "
                "enseñando al amigo o el frasco, con sus candados; debajo de "
                "cada nivel solo lo que el dibujo no dice, las llaves, qué "
                "guarda cada jaula, cuál es el objeto escondido y a dónde "
                "lleva cada puerta de calavera; y los cinco minimapas de ronda "
                "a 1:1, con las rayas por detrás de los niveles. Por el "
                "camino: el índice del objeto escondido casa con la tabla del "
                "inventario en los 23, y los amigos enjaulados suman siete por "
                "ronda, justo los que pide la puerta de salida.")),
    dict(id="knightmare-issue1-bloques", clave="knightmare",
         clase="actualiza", fecha="2026-09-24T13:38:11+02:00",
         titulo=dict(en="Knightmare: the eight maps with their blocks",
                     es="Knightmare: los ocho mapas con sus bloques"),
         resumen=dict(
             en="What theNestruo asked for in issue #1: a second drawing of "
                "each of the eight maps with the 356 blocks of the stage lists "
                "on it, each showing what it drops, a life, 500 points, a bomb, "
                "a freeze, a grey block that walls the way, the EXIT sign that "
                "warps to another stage, a bridge or a side passage, with a "
                "white frame for the visible ones and a dotted magenta one for "
                "the hidden. Their row was measured in the emulator, not "
                "deduced: 220 minus the scroll counter.",
             es="Lo que pedía theNestruo en el issue #1: un segundo dibujo de "
                "cada uno de los ocho mapas con los 356 bloques de las listas "
                "de fase encima, cada uno enseñando lo que suelta, una vida, "
                "500 puntos, una bomba, una congelación, un bloque gris que "
                "cierra el paso, el cartel EXIT que salta a otra fase, un "
                "puente o un pasadizo lateral, con marco blanco los visibles y "
                "punteado magenta los escondidos. Su fila se midió en el "
                "emulador, no se dedujo: 220 menos el contador del "
                "desplazamiento.")),
    dict(id="yiearkungfu2-issue2-oleadas", clave="yiearkungfu2",
         clase="actualiza", fecha="2026-09-24T11:28:16+02:00",
         titulo=dict(en="Yie Ar Kung-Fu II: the twelve wave screens, and a "
                        "mirror that was not one",
                     es="Yie Ar Kung-Fu II: las doce pantallas de oleadas, y un "
                        "espejo que no lo era"),
         resumen=dict(
             en="theNestruo doubted, in issue #2, that the fight screens were "
                "built by mirroring, and he was right: measured pixel by "
                "pixel, 119, 102, 40 and 128 of the 304 pairs of cells differ "
                "in the four sceneries. And the twelve wave screens before "
                "each boss are now drawn from the ROM and checked against the "
                "emulator to zero bytes: they are the fight screen's own "
                "bands, reordered per stage, and nothing scrolls inside a "
                "screen.",
             es="theNestruo dudaba, en el issue #2, de que las pantallas de "
                "combate se montaran por espejo, y tenía razón: medidas píxel "
                "a píxel, en los cuatro decorados difieren 119, 102, 40 y 128 "
                "de las 304 parejas de casillas. Y las doce pantallas de "
                "oleadas de antes de cada jefe ya están dibujadas desde la ROM "
                "y cotejadas contra el emulador a cero bytes: son las bandas "
                "de la propia pantalla de combate, reordenadas por fase, y "
                "dentro de una pantalla no se desplaza nada.")),
    dict(id="twinbee-issue1-mapas", clave="twinbee",
         clase="actualiza", fecha="2026-09-22T16:15:36+02:00",
         titulo=dict(en="Twin Bee: the maps were wrong, and so was the "
                        "background",
                     es="Twin Bee: los mapas estaban mal, y el fondo también"),
         resumen=dict(
             en="theNestruo saw holes in the stage 5 shadows (issue #1) and "
                "the fault was in the drawing, not in the cartridge: the "
                "1,761-row strip carries the five stages one after another and "
                "each map was painted whole with its own tiles; and in play "
                "the VDP's register 7 is 0xE0, so the transparent tile is "
                "black, not blue. Redrawn per stage on a black background, and "
                "checked in the emulator: the shadow is solid.",
             es="theNestruo vio huecos en las sombras de la fase 5 (issue #1) "
                "y el fallo estaba en el dibujo, no en el cartucho: la tira de "
                "1.761 filas lleva las cinco fases seguidas y cada mapa se "
                "pintaba entera con sus propias casillas; y en partida el "
                "registro 7 del VDP vale 0xE0, así que la casilla transparente "
                "es negra, no azul. Redibujados por fase sobre fondo negro, y "
                "comprobado en el emulador: la sombra es maciza.")),
    dict(id="hypersports1-issue2-banador", clave="hypersports1",
         clase="actualiza", fecha="2026-09-22T14:32:00+02:00",
         titulo=dict(en="Hyper Sports 1: the athlete's swimsuit, and a pose "
                        "cut by the bar",
                     es="Hyper Sports 1: el bañador del atleta, y una pose "
                        "cortada por la barra"),
         resumen=dict(
             en="theNestruo was right in issue #2: the swimsuit is not in the "
                "drawing scripts. Only in the diving event, 0x63E8 swaps "
                "sprites 0-1 with 2-3 in the buffer, so the two yellow pieces "
                "come to the front and cover the shirt and the boots; the "
                "pool's VRAM dump confirms it. And pose 40 carries two "
                "transparent columns so the post of the horizontal bar shows "
                "through the athlete, so it now sits on the real scenery. New "
                "plates, and tests that check the athlete of each VRAM dump "
                "against the ROM pixel by pixel.",
             es="theNestruo tenía razón en el issue #2: el bañador no está en "
                "los guiones de dibujo. Solo en los saltos de trampolín, "
                "0x63E8 permuta los sprites 0-1 con los 2-3 en el búfer, y así "
                "las dos piezas amarillas pasan delante y tapan la camiseta y "
                "las botas; el volcado de VRAM de la piscina lo confirma. Y la "
                "pose 40 lleva dos columnas transparentes para que el poste de "
                "la barra fija asome a través del atleta, así que ahora va "
                "sobre el decorado real. Láminas nuevas, y tests que cotejan "
                "el atleta de cada volcado de VRAM contra la ROM píxel a "
                "píxel.")),
    dict(id="mahjong-en-tecla4", clave="mahjong-en",
         clase="actualiza", fecha="2026-09-20T11:13:18+02:00",
         titulo=dict(en="Mahjong Dojo's English patch: key 4 goes straight to the tutorial",
                     es="El parche del Mahjong Dojo: la tecla 4 lleva directa al tutorial"),
         resumen=dict(
             en="The title menu gains a fourth line, 4-key TUTORIAL, so nobody "
                "has to sit through the demo hand. And two faults in the "
                "tutorial's tiles are gone: the twenty it took for granted were "
                "the opponent's set, rotated 180 degrees, and the empty slot's "
                "tile numbers were the list interpreter's control codes, which "
                "cut the bottom row off every tile behind a gap. Both proved in "
                "bytes and verified in the emulator, slide by slide.",
             es="El menú del título gana una cuarta línea, 4-key TUTORIAL, para "
                "no tener que esperar a que el demo juegue su mano. Y fuera dos "
                "fallos en las fichas del tutorial: las veinte que daba por "
                "cargadas eran las del rival, giradas 180 grados, y los números "
                "de celda del hueco vacío eran los códigos de control del "
                "intérprete de listas, que cortaban la fila de abajo a toda "
                "ficha detrás de un hueco. Los dos, demostrados en bytes y "
                "comprobados en el emulador diapositiva a diapositiva.",
         )),
    dict(id="warinmiddleearth-semana-del-cartucho", clave="warinmiddleearth-patch",
         clase="actualiza", fecha="2026-09-18T18:27:11+02:00",
         enlace="https://github.com/antxiko/WarinMiddleEarth-MSX-Patch",
         titulo=dict(en="War in Middle Earth: a week inside the cartridge",
                     es="War in Middle Earth: una semana dentro del cartucho"),
         resumen=dict(
             en="Twenty-seven changes published between the 11th and the 18th: "
                "the three loading pictures and the end screens moved into ROM "
                "and compressed with ZX0, a map of what lives in each stretch "
                "of the 64 KB of RAM, the near view drawn through the name "
                "table and the cursor turned into a sprite (from 3.2 to 43 "
                "turns a second), the general map drawn in 0.7 seconds instead "
                "of 3.9, the battle refreshing only what changes, a troop "
                "strength bug in battle fixed after being wrong since 1988, "
                "Gollum made a hobbit, two more heroes, Tom Bombadil and "
                "Radagast, every unit on the map marked with the Ring, and the "
                "pre-battle screen at human speed. The patch's website still "
                "describes the cartridge as it was on the 10th; the repository "
                "has all of it.",
             es="Veintisiete cambios publicados entre el 11 y el 18: las tres "
                "imágenes de carga y las pantallas finales pasan a la ROM "
                "comprimidas con ZX0, un mapa de qué vive en cada tramo de los "
                "64 KB de RAM, la vista de cerca dibujada por la tabla de "
                "nombres y el cursor convertido en sprite (de 3,2 a 43 vueltas "
                "por segundo), el mapa general dibujado en 0,7 segundos en vez "
                "de 3,9, la batalla refrescando sólo lo que cambia, arreglada "
                "la fuerza de la tropa en batalla, rota desde 1988, Gollum "
                "convertido en hobbit, dos héroes más, Tom Bombadil y Radagast, "
                "cada unidad del mapa marcada con el Anillo, y la pantalla de "
                "antes de la batalla a velocidad humana. La web del parche "
                "sigue contando el cartucho tal como estaba el día 10; el "
                "repositorio lo tiene todo.",
         )),
    dict(id="penguinadventure", clave="penguinadventure",
         clase="nuevo", fecha="2026-09-16T12:10:00+02:00",
         titulo=dict(en="Penguin Adventure, taken apart",
                     es="Penguin Adventure, desmontado"),
         resumen=dict(
             en="The 128 KB sequel to Antarctic Adventure, explained byte for "
                "byte and commented to 44.6% with no routine left under the "
                "10% line. Out of it came two hidden keyboard codes, NORIKO "
                "and KAZUMI, which turn on a CONTINUE that does not exist "
                "without them: the nine keys the cartridge watches are exactly "
                "the letters of those two names. Both are verified in the "
                "emulator, not just read off the listing.",
             es="La continuación de Antarctic Adventure, 128 KB explicados byte "
                "a byte y comentados al 44,6 % sin dejar una sola rutina por "
                "debajo del listón del 10 %. De ahí salieron dos claves de "
                "teclado escondidas, NORIKO y KAZUMI, que encienden un "
                "CONTINUE que sin ellas no existe: las nueve teclas que el "
                "cartucho vigila son exactamente las letras de esos dos "
                "nombres. Las dos están comprobadas en el emulador, no sólo "
                "leídas del listado.",
         )),
    dict(id="f1spirit-100", clave="f1spirit",
         clase="actualiza", fecha="2026-09-15T14:21:39+02:00",
         titulo=dict(en="F-1 Spirit, at 100%",
                     es="F-1 Spirit, al 100 %"),
         resumen=dict(
             en="The last 504 bytes of the MegaROM are accounted for, and none of "
                "them was code: two compressed drawings nothing draws, three SCC "
                "waveforms no instrument points to, the bar of the split screen and "
                "the rows of two tables no reader reaches. And the demo's four "
                "recorded games, now with their reader.",
             es="Los últimos 504 bytes del MegaROM ya están explicados, y ninguno "
                "era código: dos dibujos comprimidos que no pinta nadie, tres formas "
                "de onda del SCC a las que no apunta ningún instrumento, la barra de "
                "la pantalla partida y filas de dos tablas a las que no llega su "
                "lector. Y las cuatro partidas grabadas de la demo, ya con quien las "
                "lee.")),
    dict(id="warinmiddleearth-cartucho", clave="warinmiddleearth-patch",
         clase="actualiza", fecha="2026-09-10T18:39:33+02:00",
         titulo=dict(en="War in Middle Earth: the tape, now a cartridge",
                     es="War in Middle Earth: la cinta, ahora en cartucho"),
         resumen=dict(
             en="The game is untouched: a 64 KB ASCII16 cartridge whose loader "
                "leaves RAM exactly as the tape loader leaves it and jumps to the "
                "same place. Checked byte for byte against the tape, RAM, VRAM, VDP "
                "and PSG, on four machines. Nine seconds instead of six and a half "
                "minutes.",
             es="El juego no se toca: un cartucho ASCII16 de 64 KB cuyo cargador "
                "deja la RAM exactamente como la deja el de la cinta y salta al "
                "mismo sitio. Cotejado byte a byte contra la cinta -RAM, VRAM, VDP y "
                "PSG- en cuatro maquinas. Nueve segundos en vez de seis minutos y "
                "medio.")),
    dict(id="holeinonepro", clave="holeinonepro", clase="nuevo",
         fecha="2026-09-09T17:49:39+02:00"),
    dict(id="serie-db", clave="serie-db", clase="nuevo",
         fecha="2026-09-09T08:42:16+02:00"),
    dict(id="twinbee", clave="twinbee", clase="nuevo",
         fecha="2026-09-09T01:33:11+02:00"),
    dict(id="bomberman", clave="bomberman", clase="nuevo",
         fecha="2026-09-08T16:27:46+02:00"),
    dict(id="boxing", clave="boxing", clase="nuevo",
         fecha="2026-09-07T17:53:17+02:00"),
    dict(id="knightmare", clave="knightmare", clase="nuevo",
         fecha="2026-09-07T14:35:38+02:00"),
    dict(id="yiearkungfu2", clave="yiearkungfu2", clase="nuevo",
         fecha="2026-09-07T10:25:53+02:00"),
    dict(id="gamemaster", clave="gamemaster", clase="nuevo",
         fecha="2026-09-06T12:40:39+02:00"),
    dict(id="trailblazer", clave="trailblazer", clase="nuevo",
         fecha="2026-09-06T08:39:47+02:00"),
    dict(id="goonies", clave="goonies", clase="nuevo",
         fecha="2026-09-06T01:10:05+02:00"),
    dict(id="hypersports3", clave="hypersports3", clase="nuevo",
         fecha="2026-09-05T20:49:28+02:00"),
    dict(id="soccer", clave="soccer", clase="nuevo",
         fecha="2026-09-05T13:18:27+02:00"),
    dict(id="pingpong", clave="pingpong", clase="nuevo",
         fecha="2026-09-05T09:45:46+02:00"),
    dict(id="roadfighter", clave="roadfighter", clase="nuevo",
         fecha="2026-09-04T22:52:44+02:00"),
    dict(id="descubrimiento", clave="descubrimiento", clase="nuevo",
         fecha="2026-09-04T18:30:22+02:00"),
    dict(id="mopiranger", clave="mopiranger", clase="nuevo",
         fecha="2026-09-04T17:24:27+02:00"),
    dict(id="yiearkungfu", clave="yiearkungfu", clase="nuevo",
         fecha="2026-09-04T11:44:23+02:00"),
    dict(id="baseball", clave="baseball", clase="nuevo",
         fecha="2026-09-04T08:09:43+02:00"),
    dict(id="kingsvalley", clave="kingsvalley", clase="nuevo",
         fecha="2026-09-04T06:42:22+02:00"),
    dict(id="warinmiddleearth-patch", clave="warinmiddleearth-patch", clase="nuevo",
         fecha="2026-09-03T14:48:48+02:00"),
    dict(id="3dgolf", clave="3dgolf", clase="nuevo",
         fecha="2026-09-03T12:05:35+02:00"),
    dict(id="casioworldopen", clave="casioworldopen", clase="nuevo",
         fecha="2026-09-03T10:49:34+02:00"),
    dict(id="holeinone", clave="holeinone", clase="nuevo",
         fecha="2026-09-03T08:21:14+02:00"),
    dict(id="tennis", clave="tennis", clase="nuevo",
         fecha="2026-09-02T13:32:50+02:00"),
    dict(id="golf", clave="golf", clase="nuevo",
         fecha="2026-09-02T09:06:14+02:00"),
    dict(id="skyjaguar", clave="skyjaguar", clase="nuevo",
         fecha="2026-09-01T21:18:08+02:00"),
    dict(id="nemesis", clave="nemesis", clase="nuevo",
         fecha="2026-08-30T16:57:19+02:00"),
    dict(id="hypersports2", clave="hypersports2", clase="nuevo",
         fecha="2026-08-30T13:17:34+02:00"),
    dict(id="cabbagepatch", clave="cabbagepatch", clase="nuevo",
         fecha="2026-08-30T10:20:19+02:00"),
    dict(id="hypersports1", clave="hypersports1", clase="nuevo",
         fecha="2026-08-30T02:16:25+02:00"),
    dict(id="hyperrally", clave="hyperrally", clase="nuevo",
         fecha="2026-08-30T01:42:22+02:00"),
    dict(id="war", clave="war", clase="nuevo",
         fecha="2026-08-29T19:05:04+02:00"),
    dict(id="demonia", clave="demonia", clase="nuevo",
         fecha="2026-08-29T18:31:14+02:00"),
    dict(id="hyperolympic2", clave="hyperolympic2", clase="nuevo",
         fecha="2026-08-29T15:02:35+02:00"),
    dict(id="hyperolympic1", clave="hyperolympic1", clase="nuevo",
         fecha="2026-08-29T15:02:12+02:00"),
    dict(id="mahjong-en", clave="mahjong-en", clase="nuevo",
         fecha="2026-08-29T12:08:09+02:00"),
    dict(id="billiards", clave="billiards", clase="nuevo",
         fecha="2026-08-29T01:44:05+02:00"),
    dict(id="mahjong", clave="mahjong", clase="nuevo",
         fecha="2026-08-28T23:51:06+02:00"),
    dict(id="supercobra", clave="supercobra", clase="nuevo",
         fecha="2026-08-22T10:58:55+02:00"),
    dict(id="frogger", clave="frogger", clase="nuevo",
         fecha="2026-08-20T12:14:37+02:00"),
    dict(id="timepilot", clave="timepilot", clase="nuevo",
         fecha="2026-08-20T10:56:00+02:00"),
    dict(id="pippols", clave="pippols", clase="nuevo",
         fecha="2026-08-20T09:58:06+02:00"),
    dict(id="f1spirit", clave="f1spirit", clase="nuevo",
         fecha="2026-08-19T19:45:54+02:00"),
    dict(id="monkey", clave="monkey", clase="nuevo",
         fecha="2026-08-19T01:27:36+02:00"),
    dict(id="athletic", clave="athletic", clase="nuevo",
         fecha="2026-08-18T23:31:07+02:00"),
    dict(id="pitfall", clave="pitfall", clase="nuevo",
         fecha="2026-08-17T16:18:15+02:00"),
    dict(id="antarctic", clave="antarctic", clase="nuevo",
         fecha="2026-08-13T15:42:25+02:00"),
    dict(id="stardust", clave="stardust", clase="nuevo",
         fecha="2026-08-06T09:14:07+02:00"),
    dict(id="colt36", clave="colt36", clase="nuevo",
         fecha="2026-08-05T14:08:25+02:00"),
    dict(id="alehop", clave="alehop", clase="nuevo",
         fecha="2026-08-04T16:16:54+02:00"),
    dict(id="temptations", clave="temptations", clase="nuevo",
         fecha="2026-08-04T09:21:22+02:00"),
]

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
        proyectos=DESENSAMBLADOS + HERRAMIENTAS,
        partes=[
            dict(id="numbers",
                 titulo=dict(en="The series in numbers", es="La serie en cifras"),
                 html=html_cifras),
            *[dict(id=g["id"], titulo=g["titulo"], proyectos=del_grupo(g["id"]))
              for g in GRUPOS],
            dict(id="method",
                 titulo=dict(en="How they are made", es="Cómo están hechos"),
                 html=html_metodo),
            # Antes era una seccion propia; con los botones de arriba va aqui.
            # Su id sigue siendo "tools": los enlaces viejos a #tools valen.
            dict(id="tools",
                 titulo=dict(en="The series from the inside", es="La serie por dentro"),
                 intro=dict(
                    en="Not a game: the measurements. What the disassemblies look like "
                       "when you put all of them side by side and measure again instead "
                       "of trusting what each one says about itself &mdash; which is how "
                       "you find out that the same routine goes by twelve names, and "
                       "that four published figures had quietly gone stale.",
                    es="Esto no es un juego: son las medidas. Lo que se ve en los "
                       "desensamblados cuando se ponen todos uno al lado del otro y se "
                       "vuelve a medir en vez de fiarse de lo que cada uno dice de sí "
                       "mismo &mdash;que es como se descubre que la misma rutina lleva "
                       "doce nombres, y que cuatro cifras publicadas se habían quedado "
                       "viejas sin que nadie se enterara&mdash;.",
                 ),
                 proyectos=HERRAMIENTAS),
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
        menu_feed="Feed",
        entrar="Open the section",
        feed_nuevo=dict(disassemblies="{}: disassembled", patches="{}: published",
                        tools="{}: published"),
        feed_actualiza="{}: updated",
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
        menu_feed="Novedades",
        entrar="Entrar en la sección",
        feed_nuevo=dict(disassemblies="{}: desensamblado", patches="{}: publicado",
                        tools="{}: publicada"),
        feed_actualiza="{}: novedades",
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
                if "intro" in p:
                    dentro = (f'<p class="n" style="margin-bottom:1.5rem;'
                              f'color:var(--suave)">{p["intro"][idioma]}</p>\n'
                              f'    {dentro}')
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


def visibles():
    """Las secciones que salen: una sin proyectos no sale ni en el menu."""
    return [c for c in CATEGORIAS if c["proyectos"]]


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
    # las novedades: lo que rompe un feed sin que se note hasta que un lector
    # lo rechaza o ensena todo como nuevo
    claves = {p["clave"] for p in DESENSAMBLADOS + PARCHES + HERRAMIENTAS}
    ids = [n["id"] for n in NOVEDADES]
    if len(ids) != len(set(ids)):
        raise SystemExit("NOVEDADES: hay un id repetido")
    anterior = None
    for n in NOVEDADES:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", n["id"]):
            raise SystemExit(f"NOVEDADES: id {n['id']!r} con caracteres que no van en un tag:")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", n["fecha"]):
            raise SystemExit(f"NOVEDADES {n['id']}: la fecha {n['fecha']!r} no es RFC 3339 con huso")
        fecha = datetime.fromisoformat(n["fecha"])
        if anterior is not None and fecha > anterior:
            raise SystemExit(f"NOVEDADES: {n['id']} esta mas abajo que una mas vieja")
        anterior = fecha
        if n["clave"] not in claves:
            raise SystemExit(f"NOVEDADES {n['id']}: la clave {n['clave']!r} no es de ningun proyecto")
        for otra in n.get("otras", ()):
            if otra not in claves:
                raise SystemExit(f"NOVEDADES {n['id']}: la clave {otra!r} no es de ningun proyecto")
        if n["clase"] not in ("nuevo", "actualiza"):
            raise SystemExit(f"NOVEDADES {n['id']}: clase {n['clase']!r}")
        for campo in ("titulo", "resumen"):
            if campo in n and set(n[campo]) != {"en", "es"}:
                raise SystemExit(f"NOVEDADES {n['id']}: {campo} tiene que ir en 'en' y 'es'")
    sin = claves - {c for n in NOVEDADES for c in (n["clave"], *n.get("otras", ()))}
    if sin:
        raise SystemExit(f"proyectos sin novedad en NOVEDADES: {sorted(sin)}")


# ------------------------------------------------------------------ el feed
FEED = dict(en=dict(ruta="feed.xml", pagina=""),
            es=dict(ruta="es/feed.xml", pagina="es/"))


def proyecto(clave):
    for p in DESENSAMBLADOS + PARCHES + HERRAMIENTAS:
        if p["clave"] == clave:
            return p
    raise KeyError(clave)


def categoria_de(clave):
    # La serie por dentro va ahora dentro de los desensamblados, pero su
    # noticia tiene que seguir diciendo "publicada": el feed no cambia.
    if any(p["clave"] == clave for p in HERRAMIENTAS):
        return "tools"
    for c in CATEGORIAS:
        if any(p["clave"] == clave for p in c["proyectos"]):
            return c["id"]
    raise KeyError(clave)


def texto_plano(s):
    """De un texto de la portada a texto para el XML: fuera las etiquetas, las
    entidades HTML resueltas a sus letras (&middot; -> el punto de verdad) y
    despues escapado lo que XML exige. Es el UNICO camino de un texto al feed."""
    return saxutils.escape(html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def titulo_de(n, idioma):
    if "titulo" in n:
        return n["titulo"][idioma]
    p, t = proyecto(n["clave"]), TXT[idioma]
    if n["clase"] == "nuevo":
        return t["feed_nuevo"][categoria_de(n["clave"])].format(p["titulo"])
    return t["feed_actualiza"].format(p["titulo"])


def resumen_de(n, idioma):
    if "resumen" in n:
        return n["resumen"][idioma]
    p = proyecto(n["clave"])
    return "%s. %s." % (p["meta"][idioma], p["datos"][idioma](idioma))


def enlace_de(n):
    if "enlace" in n:
        return n["enlace"]
    p = proyecto(n["clave"])
    return p["web"] or p["repo"]


def feed(idioma):
    """Atom 1.0 (RFC 4287). Un feed por idioma, enlazados entre si; el 'updated'
    del feed es la fecha de la novedad mas nueva, no la hora del build, para
    que regenerar sin novedades no cambie ni un byte."""
    t = TXT[idioma]
    otro = "es" if idioma == "en" else "en"
    lineas = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{idioma}">',
        f'  <title>{texto_plano(t["titulo"])}</title>',
        f'  <subtitle>{texto_plano(t["claim"])}</subtitle>',
        f'  <id>tag:{DOMINIO},2026:feed/{idioma}</id>',
        f'  <link rel="self" type="application/atom+xml" href="{SITIO}/{FEED[idioma]["ruta"]}"/>',
        f'  <link rel="alternate" type="text/html" hreflang="{idioma}" href="{SITIO}/{FEED[idioma]["pagina"]}"/>',
        f'  <link rel="alternate" type="application/atom+xml" hreflang="{otro}" href="{SITIO}/{FEED[otro]["ruta"]}"/>',
        f'  <updated>{NOVEDADES[0]["fecha"]}</updated>',
        f'  <author><name>{USUARIO}</name><uri>https://github.com/{USUARIO}</uri></author>',
    ]
    for n in NOVEDADES[:LIMITE]:
        lineas += [
            '  <entry>',
            f'    <id>tag:{DOMINIO},2026:novedad/{idioma}/{n["id"]}</id>',
            f'    <title>{texto_plano(titulo_de(n, idioma))}</title>',
            f'    <link rel="alternate" type="text/html" href="{saxutils.escape(enlace_de(n))}"/>',
            f'    <published>{n["fecha"]}</published>',
            f'    <updated>{n["fecha"]}</updated>',
            f'    <summary type="text">{texto_plano(resumen_de(n, idioma))}</summary>',
            '  </entry>',
        ]
    lineas.append('</feed>')
    return "\n".join(lineas) + "\n"


# Los enlaces viejos a una seccion o a una parte de la portada (/#patches,
# /#konami...) llevan ahora a su pagina. Sale de las listas: {ancla: ruta}.
def anclas_viejas():
    m = {}
    for c in visibles():
        m[c["id"]] = c["id"] + "/"
        for parte in c.get("partes", []):
            m[parte["id"]] = c["id"] + "/#" + parte["id"]
    return m


REDIRIGE = """
(function(){
  var m = %s;
  var h = decodeURIComponent(location.hash.slice(1));
  if (h && m.hasOwnProperty(h)) location.replace(m[h]);
})();
"""


def resumen(c, idioma, t):
    """En la portada, cada seccion es su rotulo, su intro y la puerta a su
    pagina. El id es el de la seccion: un /#patches sin JavaScript cae aqui."""
    return (f'\n<div class="resumen" id="{c["id"]}">\n'
            f'  <h2>{c["titulo"][idioma]}</h2>\n'
            f'  <p class="n" style="margin-bottom:1.2rem;color:var(--suave)">'
            f'{c["intro"][idioma]}</p>\n'
            f'  <p><a class="entrar" href="{c["id"]}/">{t["entrar"]} &rarr;</a></p>\n'
            f'</div>\n')


def pagina(idioma, c=None):
    """La portada (c=None) o la pagina de la seccion c. Las de seccion viven en
    <id>/ (ingles) y es/<id>/ (castellano): un nivel mas abajo que su portada."""
    t = TXT[idioma]
    otro = "es" if idioma == "en" else "en"
    raiz = "../" if c else ""
    sub = c["id"] + "/" if c else ""
    # lo que lleva al otro idioma: de / a es/ y de es/ a / (y lo mismo con <id>/)
    al_otro = ("es/" if idioma == "en" else "../") if not c else \
              ("../es/" + sub if idioma == "en" else "../../" + sub)
    otro_feed = ("es/feed.xml" if idioma == "en" else "../feed.xml") if not c else \
                ("../es/feed.xml" if idioma == "en" else "../../feed.xml")

    nav = ""
    for x in visibles():
        actual = ' aria-current="page"' if c is x else ""
        nav += f'<a class="sec" href="{raiz}{x["id"]}/"{actual}>{x["menu"][idioma]}</a>'
    nav += f'<a href="{raiz}feed.xml">{t["menu_feed"]}</a>'
    nav += f'<a href="https://github.com/{USUARIO}">{t["menu_gh"]}</a>'
    nav += (f'<a href="{al_otro}" style="margin-left:auto;color:var(--oro)">'
            f'{t["otro"][1]}</a>')

    ficha = "".join(f"<span>{x}</span>" for x in t["ficha"])
    if c:
        titulo = f'{c["titulo"][idioma]} &mdash; antxiko'
        cuerpo = seccion(c, idioma, t)
        script = ""
    else:
        titulo = t["titulo"]
        cuerpo = "".join(resumen(x, idioma, t) for x in visibles())
        script = "<script>" + REDIRIGE % json.dumps(anclas_viejas()) + "</script>\n"
    # El feed de este idioma y el del otro, para que el navegador o el lector lo
    # encuentren solos. Aunque la pagina no lleva <head>, el parser HTML5 mete
    # estos <link> en el head implicito: tienen que ir ANTES del primer <div>.
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title>
<link rel="alternate" type="application/atom+xml" hreflang="{idioma}" title="{t['menu_feed']}" href="{raiz}feed.xml">
<link rel="alternate" type="application/atom+xml" hreflang="{otro}" title="{TXT[otro]['menu_feed']}" href="{otro_feed}">
<style>{ESTILO}{EXTRA}</style>

<div class="w">
<header class="top">
  <h1><a href="{raiz or './'}" style="color:inherit;text-decoration:none">antxiko<span>/</span></a></h1>
  <p class="claim">{t['claim']}</p>
  <div class="ficha">{ficha}</div>
</header>
<nav>{nav}</nav>
{cuerpo}
<footer>{t['pie']}</footer>
</div>
{script}"""


def paginas():
    """(ruta, idioma, html) de todo lo que se escribe: dos portadas y, por cada
    seccion visible, su pagina en los dos idiomas."""
    for idioma, base in (("en", ""), ("es", "es/")):
        yield base + "index.html", idioma, pagina(idioma)
        for c in visibles():
            yield base + c["id"] + "/index.html", idioma, pagina(idioma, c)


def main():
    comprueba()
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ruta, idioma, texto in paginas():
        destino = os.path.join(raiz, ruta)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        print("  %s: %d KB (%s)" % (ruta, len(texto) // 1024, idioma))
    for idioma, f in FEED.items():
        destino = os.path.join(raiz, f["ruta"])
        xml = feed(idioma)
        with open(destino, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(xml)
        print("  %s: %d KB, %d entradas (%s)"
              % (f["ruta"], len(xml) // 1024, min(LIMITE, len(NOVEDADES)), idioma))
    return 0


if __name__ == "__main__":
    sys.exit(main())
