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

Para anadir otra categoria de proyectos (no desensamblados): otra lista con los
mismos campos que DESENSAMBLADOS y otra entrada en CATEGORIAS. El menu y las
secciones se generan de esa lista.
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
        clave="timepilot",
        titulo="Time Pilot",
        anio=1983,
        repo="https://github.com/antxiko/TimePilot-disassembly",
        web="https://antxiko.github.io/TimePilot-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 16 KB cartridge &middot; RC-703",
            es="Konami &middot; MSX1 &middot; cartucho de 16 KB &middot; RC-703",
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
        titulo="Frogger",
        anio=1983,
        repo="https://github.com/antxiko/Frogger-disassembly",
        web="https://antxiko.github.io/Frogger-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 8 KB cartridge &middot; RC-704",
            es="Konami &middot; MSX1 &middot; cartucho de 8 KB &middot; RC-704",
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
        clave="athletic",
        titulo="Athletic Land",
        anio=1984,
        repo="https://github.com/antxiko/AthleticLand-disassembly",
        web="https://antxiko.github.io/AthleticLand-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 16 KB cartridge &middot; RC-700",
            es="Konami &middot; MSX1 &middot; cartucho de 16 KB &middot; RC-700",
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
        titulo="Antarctic Adventure",
        anio=1984,
        repo="https://github.com/antxiko/AntarcticAdventure-disassembly",
        web="https://antxiko.github.io/AntarcticAdventure-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 16 KB cartridge &middot; RC-701",
            es="Konami &middot; MSX1 &middot; cartucho de 16 KB &middot; RC-701",
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
        titulo="Monkey Academy",
        anio=1984,
        repo="https://github.com/antxiko/MonkeyAcademy-disassembly",
        web="https://antxiko.github.io/MonkeyAcademy-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 16 KB cartridge &middot; RC-702",
            es="Konami &middot; MSX1 &middot; cartucho de 16 KB &middot; RC-702",
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
        clave="pitfall",
        titulo="Pitfall!",
        anio=1984,
        repo="https://github.com/antxiko/Pitfall-MSX-disassembly",
        web="https://antxiko.github.io/Pitfall-MSX-disassembly/",
        meta=dict(
            en="Activision &middot; MSX1 &middot; 16 KB cartridge",
            es="Activision &middot; MSX1 &middot; cartucho de 16 KB",
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
        titulo="Pippols",
        anio=1985,
        repo="https://github.com/antxiko/Pippols-disassembly",
        web="https://antxiko.github.io/Pippols-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 16 KB cartridge &middot; RC-729",
            es="Konami &middot; MSX1 &middot; cartucho de 16 KB &middot; RC-729",
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
        clave="f1spirit",
        titulo="F-1 Spirit &mdash; The Way to Formula 1",
        anio=1987,
        terminado=False,
        repo="https://github.com/antxiko/F1Spirit-disassembly",
        web="https://antxiko.github.io/F1Spirit-disassembly/",
        meta=dict(
            en="Konami &middot; MSX1 &middot; 128 KB MegaROM &middot; RC-752",
            es="Konami &middot; MSX1 &middot; MegaROM de 128 KB &middot; RC-752",
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
        titulo="Colt 36",
        anio=1987,
        repo="https://github.com/antxiko/Colt36-disassembly",
        web="https://antxiko.github.io/Colt36-disassembly/",
        meta=dict(
            en="Topo Soft &middot; MSX1 &middot; cassette tape",
            es="Topo Soft &middot; MSX1 &middot; cinta de cassette",
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
        titulo="War in Middle Earth",
        anio=1989,
        terminado=False,
        repo=None,
        web=None,
        meta=dict(
            en="Melbourne House / Dro Soft &middot; MSX1 &middot; cassette tape",
            es="Melbourne House / Dro Soft &middot; MSX1 &middot; cinta de cassette",
        ),
        claim=dict(
            en="In progress, and parked. It runs with all four pages in RAM and no "
               "BIOS at all, loaded by a Spectrum-style loader that hunts for RAM "
               "page by page; the five listings already reassemble byte for byte "
               "and the relocation was confirmed in the emulator. What is missing "
               "is the low block's graphics, which nothing has yet been seen to "
               "read: it waits on a full recorded game reaching the battle and the "
               "load/save screens.",
            es="En marcha, y aparcado. Corre con las cuatro páginas en RAM y sin "
               "BIOS, cargado por un cargador estilo Spectrum que busca RAM página "
               "por página; los cinco listados ya reensamblan byte a byte y la "
               "recolocación se confirmó en el emulador. Lo que falta son los "
               "gráficos del bloque bajo, que todavía no se ha visto quién los lee: "
               "espera una partida completa grabada que llegue a la batalla y a las "
               "pantallas de cargar y salvar.",
        ),
        datos=dict(
            en=lambda i: (f"{cif(48437, i)} of {cif(62261, i)} bytes explained "
                          f"(<b>77.80%</b>) &middot; <b>five listings</b>, all "
                          f"<b>byte for byte</b> &middot; {cif(13824, i)} bytes of "
                          f"graphics with no reader found yet"),
            es=lambda i: (f"{cif(48437, i)} de {cif(62261, i)} bytes explicados "
                          f"(<b>77,80 %</b>) &middot; <b>cinco listados</b>, todos "
                          f"<b>byte a byte</b> &middot; {cif(13824, i)} bytes de "
                          f"gráficos sin lector conocido todavía"),
        ),
        nota=dict(
            en="unfinished: the repository is a private backup, and there is no "
               "site yet",
            es="sin terminar: el repositorio es un respaldo privado y todavía no "
               "tiene web",
        ),
    ),
]

# Las cuentas de la cabecera salen de la lista, no de escribirlas a mano: al
# anadir un proyecto se ponen al dia solas. Un proyecto lleva 'terminado=False'
# cuando no esta al 100 %, y 'web' a None cuando todavia no tiene sitio
# publicado. Ojo: 'nota' NO sirve para esto, porque la llevan tambien los
# terminados que tienen alguna pregunta abierta.
N_JUEGOS = len(DESENSAMBLADOS)
N_CINTAS = sum(1 for p in DESENSAMBLADOS if "cinta" in p["meta"]["es"])
N_CARTUCHOS = N_JUEGOS - N_CINTAS
N_TERMINADOS = sum(1 for p in DESENSAMBLADOS if p.get("terminado", True))
N_CON_WEB = sum(1 for p in DESENSAMBLADOS if p.get("web"))
ANIOS = "%d-%d" % (min(p["anio"] for p in DESENSAMBLADOS),
                   max(p["anio"] for p in DESENSAMBLADOS))

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
    ),
    # Para anadir otra categoria: una lista de proyectos con estos mismos campos
    # y otra entrada aqui. El menu y las secciones salen de esta lista.
]

TXT = dict(
    en=dict(
        titulo="antxiko &mdash; commented disassemblies of 8-bit games",
        claim="Old 8-bit binaries taken apart byte by byte and commented, with the "
              "tools to rebuild them: nothing gets claimed that the binary does not "
              "show, and the source has to give the original back, byte for byte. "
              f"Right now that means {N_JUEGOS} MSX games.",
        ficha=[f"<b>{N_JUEGOS}</b> games", f"<b>{ANIOS}</b>",
               "MSX &middot; MSX1",
               f"<b>{N_CINTAS}</b> tapes &middot; <b>{N_CARTUCHOS}</b> cartridges"],
        menu_num="The numbers", menu_met="How they are made", menu_gh="GitHub",
        otro=("es/", "En castellano"),
        h_num="The series in numbers",
        cifras=[(str(N_JUEGOS), "games taken apart"),
                (str(N_TERMINADOS), "finished at 100%"),
                (str(N_CON_WEB), "with a website"),
                (str(N_CINTAS), "cassette tapes"),
                (str(N_CARTUCHOS), "cartridges"),
                ("3", "builds of Antarctic Adventure")],
        h_met="How they are made",
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
               "MSX &middot; MSX1",
               f"<b>{N_CINTAS}</b> cintas &middot; <b>{N_CARTUCHOS}</b> cartuchos"],
        menu_num="Las cifras", menu_met="Cómo están hechos", menu_gh="GitHub",
        otro=("../", "In English"),
        h_num="La serie en cifras",
        cifras=[(str(N_JUEGOS), "juegos desmontados"),
                (str(N_TERMINADOS), "terminados al 100 %"),
                (str(N_CON_WEB), "con web publicada"),
                (str(N_CINTAS), "cintas de cassette"),
                (str(N_CARTUCHOS), "cartuchos"),
                ("3", "compilaciones de Antarctic Adventure")],
        h_met="Cómo están hechos",
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


def pagina(idioma):
    t = TXT[idioma]
    menu = [("#numbers", t["menu_num"])]
    menu += [("#" + c["id"], c["menu"][idioma]) for c in CATEGORIAS]
    menu += [("#method", t["menu_met"]),
             ("https://github.com/" + USUARIO, t["menu_gh"])]
    nav = "".join(f'<a href="{h}">{x}</a>' for h, x in menu)
    nav += (f'<a href="{t["otro"][0]}" style="margin-left:auto;color:var(--oro)">'
            f'{t["otro"][1]}</a>')

    cifras = "".join(f'<div class="cifra"><b>{v}</b><span>{e}</span></div>'
                     for v, e in t["cifras"])
    ficha = "".join(f"<span>{x}</span>" for x in t["ficha"])

    secciones = ""
    for c in CATEGORIAS:
        tarjetas = "".join(tarjeta(p, idioma, t) for p in c["proyectos"])
        secciones += (f'\n<section id="{c["id"]}">\n'
                      f'  <h2>{c["titulo"][idioma]}</h2>\n'
                      f'  <p class="n" style="margin-bottom:2rem;color:var(--suave)">'
                      f'{c["intro"][idioma]}</p>\n'
                      f'  <div class="proyectos">{tarjetas}</div>\n'
                      f'</section>\n')

    metodo = "".join(f"<p>{x}</p>" for x in t["met"])

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

<section id="numbers">
  <h2>{t['h_num']}</h2>
  <div class="cifras">{cifras}</div>
</section>
{secciones}
<section id="method">
  <h2>{t['h_met']}</h2>
  <div class="n">{metodo}</div>
</section>

<footer>{t['pie']}</footer>
</div>
"""


def main():
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
