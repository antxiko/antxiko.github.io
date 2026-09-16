#!/usr/bin/env python3
"""La carpeta de entregas: ficheros para los testers, con enlace que compartir.

    python3 tools/entregas.py

Copia a `d/<token>/` los ficheros de la lista ENTREGAS, calcula su sha256 y
escribe el indice. Para anadir una entrega, una entrada en la lista y volver a
correrlo.

QUE ES ESTA CARPETA Y QUE NO ES

El usuario la pidio el 2026-09-16, harto de buscar los ficheros por el disco
cada vez que hay que mandarle algo a alguien. La carpeta:

  - NO esta enlazada desde ninguna pagina del sitio, y su nombre es un token
    aleatorio, asi que no se llega a ella navegando ni adivinando.
  - Lleva `noindex,nofollow` en el indice y un `Disallow` en robots.txt.

Pero que quede dicho, porque no es lo mismo: **esto no es privado**. El repo
es publico; cualquiera que lo abra en GitHub ve estos ficheros aunque no haya
enlace, y un buscador la indexaria en cuanto alguien pegue el URL en un sitio
publico. Se aviso al usuario y eligio esto sabiendolo.

Por eso, y por lo que dicen los dos avisos legales del proyecto, aqui NO va
nada que no haga falta que este: ni la ROM original, ni los cuerpos de la
cinta sueltos, ni nada que no se le haya mandado ya a alguien.
"""
import hashlib
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import estilo_web                       # noqa: E402

# El token es el que hace que no se llegue de casualidad. NO se cambia: los
# enlaces ya repartidos dejarian de valer.
CARPETA = "d/b81e8b4d50"

PATCH = os.path.join(os.path.dirname(RAIZ), "WARINMIDDLEEARTH_PATCH")

# Una entrada por fichero entregado, la mas nueva ARRIBA.
ENTREGAS = [
    dict(origen=os.path.join(PATCH, "builds", "WIME03.ROM"),
         fecha="2026-09-16", para="Araubi",
         titulo="War in Middle Earth &mdash; cartucho, version 3",
         que="Lo de la WIME02 mas la <b>tecla F</b>: en la batalla, la pone a "
             "casi seis veces su velocidad. Se pulsa F para encenderla -sale "
             "&laquo;Batalla rapida: SI.&raquo; abajo- y otra vez para quitarla. "
             "No cambia nada de la partida: solo deja de repintar el tablero en "
             "cada vuelta, que es donde se iba el 89 % del tiempo."),
    dict(origen=os.path.join(PATCH, "builds", "WIME02.ROM"),
         fecha="2026-09-16", para="Araubi",
         titulo="War in Middle Earth &mdash; cartucho, version 2",
         que="Arreglado el <b>infiltrado del centro del campo</b> de la batalla: "
             "la figura que se movia sin atacar, daba vueltas o se volvia orco. "
             "Era la unidad que se llevaba a mano en la batalla ANTERIOR, que "
             "nadie reiniciaba. Y con ella se iba el bug de los heroes que "
             "desaparecian del mapa sin haber peleado."),
    dict(origen=os.path.join(PATCH, "builds", "WIME01.ROM"),
         fecha="2026-09-14", para="Araubi y Ruben",
         titulo="War in Middle Earth &mdash; cartucho, version 1",
         que="La primera con todo junto: el juego en cartucho, la musica en el "
             "menu, el mapa general ya dibujado, el cursor como sprite, la vista "
             "de cerca deprisa y la fuerza de la tropa arreglada."),
    dict(origen=os.path.join(PATCH, "work", "WarInMiddleEarth-kit.zip"),
         fecha="2026-09-16", para="Nestor",
         titulo="El kit: compilar el parche sin Python",
         que="Se descomprime y se corre <code>hazlo.bat</code> (o "
             "<code>sh hazlo.sh</code>). Solo hace falta <b>pasmo</b>. Lo "
             "editable es <code>src/nombres.asm</code>, que es el parche entero; "
             "lo demas viene cocido en <code>bin/</code>. Si no se toca nada, la "
             "ROM que sale es identica byte a byte a la de aqui."),
]


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(1 << 16), b""):
            h.update(trozo)
    return h.hexdigest()


def tamano(n):
    return "%.1f KB" % (n / 1024.0) if n < 1 << 20 else "%.1f MB" % (n / 1048576.0)


def main():
    destino = os.path.join(RAIZ, *CARPETA.split("/"))
    os.makedirs(destino, exist_ok=True)

    filas = []
    for e in ENTREGAS:
        assert os.path.exists(e["origen"]), "no encuentro %s" % e["origen"]
        nombre = os.path.basename(e["origen"])
        shutil.copy(e["origen"], os.path.join(destino, nombre))
        datos = os.stat(e["origen"])
        filas.append(dict(e, nombre=nombre, bytes=datos.st_size,
                          sha=sha256(e["origen"])))

    p = []
    p.append('<meta charset="utf-8">')
    p.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    p.append('<meta name="robots" content="noindex,nofollow">')
    p.append("<title>Entregas</title>")
    p.append("<style>%s" % estilo_web.ESTILO)
    p.append(".e{border-top:1px solid var(--linea);padding:1.5rem 0}")
    p.append(".e h2{margin:0 0 .35rem;font-size:1.15rem}")
    p.append(".e h2 a{text-decoration:none}")
    p.append(".meta{font-size:12px;letter-spacing:.08em;text-transform:uppercase;"
             "color:var(--suave);margin-bottom:.75rem}")
    p.append(".meta b{color:var(--rojo);font-weight:400}")
    p.append(".sha{font-size:11px;color:var(--suave);word-break:break-all;margin-top:.6rem}")
    p.append(".aviso{border:1px solid var(--rojo);padding:1rem 1.25rem;margin:2rem 0;"
             "color:var(--suave)}")
    p.append(".aviso b{color:var(--rojo);font-weight:400}")
    p.append("</style>")
    p.append('<div class="w n">')
    p.append("<h1>Entregas</h1>")
    p.append('<p style="color:var(--suave)">Los ficheros que se han mandado, con '
             "su enlace. Esta pagina no esta enlazada desde ningun sitio y pide a "
             "los buscadores que no la indexen.</p>")
    p.append('<div class="aviso"><b>No se reparte.</b> Estos ficheros llevan '
             "dentro el juego de 1989, que tiene dueno. El enlace es para quien "
             "esta probando el parche, y no para publicarlo en ningun sitio.</div>")
    for f in filas:
        p.append('<div class="e">')
        p.append('<h2><a href="%s">%s</a></h2>' % (f["nombre"], f["titulo"]))
        p.append('<div class="meta">%s &middot; para <b>%s</b> &middot; %s &middot; %s</div>'
                 % (f["fecha"], f["para"], f["nombre"], tamano(f["bytes"])))
        p.append("<p>%s</p>" % f["que"])
        p.append('<div class="sha">sha256 %s</div>' % f["sha"])
        p.append("</div>")
    p.append("</div>")

    with open(os.path.join(destino, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")

    # Y que los buscadores no entren, por si acaso. Se bloquea el PADRE y no la
    # carpeta: robots.txt lo lee cualquiera, asi que poner ahi el token seria
    # justo lo contrario de esconderlo.
    robots = os.path.join(RAIZ, "robots.txt")
    linea = "Disallow: /%s/" % CARPETA.split("/")[0]
    if not os.path.exists(robots):
        with open(robots, "w", encoding="utf-8") as f:
            f.write("User-agent: *\n%s\n" % linea)
    else:
        with open(robots, encoding="utf-8") as f:
            hay = f.read()
        if linea not in hay:
            with open(robots, "a", encoding="utf-8") as f:
                f.write(linea + "\n")

    print("entregas en %s/ (%d ficheros)" % (CARPETA, len(filas)))
    for f in filas:
        print("  https://antxiko.github.io/%s/%s  (%s, para %s)"
              % (CARPETA, f["nombre"], tamano(f["bytes"]), f["para"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
