#!/usr/bin/env python3
# Anade Hole in One Professional a la lista de make_index.py, justo detras del
# Hole in One de 1984.
import io

ENTRADA = '''    dict(
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
'''

p = "tools/make_index.py"
s = io.open(p, encoding="utf-8").read()
assert "holeinonepro" not in s, "ya estaba"
ancla = '''    dict(
        clave="casioworldopen",'''
assert ancla in s
io.open(p, "w", encoding="utf-8").write(s.replace(ancla, ENTRADA + ancla, 1))
print("entrada anadida")
