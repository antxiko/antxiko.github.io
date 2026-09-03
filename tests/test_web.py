#!/usr/bin/env python3
"""Lo que tiene que cumplir la portada, comprobado sobre el HTML publicado.

No comprueba que "se vea bien" -eso no lo caza un test- sino lo que se rompe
solo: etiquetas sin cerrar, enlaces locales que no existen, y las dos versiones
del sitio contando cosas distintas. Esto ultimo es el fallo tipico de la serie:
se toca una cifra en un idioma y se olvida el otro.

Y la jerarquia: los desensamblados van en su seccion, repartidos en tres grupos
(Konami, exclusivos de MSX, conversiones), y los parches en la suya. Aqui se
comprueba que cada repositorio sale una vez, en el grupo que le toca, y que las
dos lenguas tienen la misma estructura con todos los rotulos traducidos.
"""
import os
import re
import sys
import unittest
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = [os.path.join(RAIZ, "index.html"),
           os.path.join(RAIZ, "es", "index.html")]
IDIOMA = {PAGINAS[0]: "en", PAGINAS[1]: "es"}

# Etiquetas que no se cierran nunca.
VACIAS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}


class Equilibrio(HTMLParser):
    """Lleva la pila de etiquetas abiertas y apunta lo que no cuadra."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila, self.fallos = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VACIAS:
            self.pila.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VACIAS:
            return
        if not self.pila:
            self.fallos.append(f"cierre huerfano </{tag}> en {self.getpos()}")
        elif self.pila[-1][0] != tag:
            abierta, donde = self.pila[-1]
            self.fallos.append(f"</{tag}> cierra <{abierta}> de {donde}")
            self.pila.pop()
        else:
            self.pila.pop()


def lee(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def modulo():
    """El generador, para cotejar el HTML contra sus datos."""
    sys.path.insert(0, os.path.join(RAIZ, "tools"))
    import make_index
    return make_index


def repos_de(html):
    return re.findall(r'href="https://github\.com/antxiko/([^"/]+)"', html)


def nombre_repo(p):
    return p["repo"].rsplit("/", 1)[1]


def estructura(texto):
    """La jerarquia de la pagina leida del HTML: {seccion: {parte: [repos]}},
    en el orden en que salen. La parte "" es lo que hay en la seccion fuera de
    cualquier parte (una seccion sin partes lo lleva todo ahi)."""
    trozos = re.split(r'<section id="([^"]+)">', texto)
    secciones = {}
    for sid, cuerpo in zip(trozos[1::2], trozos[2::2]):
        cuerpo = cuerpo.split("</section>")[0]
        partes = re.split(r'<div class="parte" id="([^"]+)">', cuerpo)
        d = {}
        if repos_de(partes[0]):
            d[""] = repos_de(partes[0])
        for pid, pcuerpo in zip(partes[1::2], partes[2::2]):
            d[pid] = repos_de(pcuerpo)
        secciones[sid] = d
    return secciones


def menu_de(texto):
    """El menu de arriba, el de las secciones de primer nivel."""
    return re.search(r"<nav>(.*?)</nav>", texto, re.S).group(1)


class TestPortada(unittest.TestCase):

    def test_el_html_esta_equilibrado(self):
        for pagina in PAGINAS:
            p = Equilibrio()
            p.feed(lee(pagina))
            p.close()
            sobran = [f"<{t}> sin cerrar en {d}" for t, d in p.pila]
            self.assertEqual(p.fallos + sobran, [],
                             "%s: %s" % (pagina, p.fallos + sobran))

    def test_los_enlaces_locales_existen(self):
        for pagina in PAGINAS:
            base = os.path.dirname(pagina)
            texto = lee(pagina)
            for href in re.findall(r'href="([^"]+)"', texto):
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                destino, _, ancla = href.partition("#")
                if not destino:
                    continue
                ruta = os.path.normpath(os.path.join(base, destino))
                if os.path.isdir(ruta):
                    ruta = os.path.join(ruta, "index.html")
                self.assertTrue(os.path.exists(ruta),
                                "%s: el enlace %s no lleva a ningun sitio"
                                % (pagina, href))

    def test_las_anclas_existen(self):
        for pagina in PAGINAS:
            texto = lee(pagina)
            ids = set(re.findall(r'id="([^"]+)"', texto))
            for href in re.findall(r'href="#([^"]+)"', texto):
                self.assertIn(href, ids,
                              "%s: el ancla #%s no existe" % (pagina, href))

    def test_los_dos_idiomas_enlazan_los_mismos_repositorios(self):
        """Si un proyecto se anade en un idioma y no en el otro, salta aqui."""
        repos = []
        for pagina in PAGINAS:
            repos.append(sorted(set(re.findall(
                r'href="https://github\.com/([^"/]+/[^"/]+)"', lee(pagina)))))
        self.assertEqual(repos[0], repos[1],
                         "las dos portadas no listan los mismos repositorios")

    def test_los_dos_idiomas_publican_las_mismas_cifras(self):
        """Las cifras se escriben dos veces; comparadas sin separador de miles."""
        cifras = []
        for pagina in PAGINAS:
            texto = re.sub(r"<[^>]+>", " ", lee(pagina))
            crudas = re.findall(r"\b\d[\d.,]*\b", texto)
            cifras.append(sorted(c.replace(".", "").replace(",", "")
                                 for c in crudas))
        self.assertEqual(cifras[0], cifras[1],
                         "las dos portadas publican cifras distintas")

    def test_las_cifras_de_la_cabecera_no_se_contradicen(self):
        """Las cuentas se calculan de la lista; aqui se comprueba que salen.

        Se publico una vez un "0 terminados al 100 %" por contar mal: la
        bandera estaba en un campo que llevaban todos. Esto lo caza.
        """
        mi = modulo()

        self.assertEqual(mi.N_JUEGOS, len(mi.DESENSAMBLADOS))
        self.assertEqual(mi.N_CINTAS + mi.N_CARTUCHOS, mi.N_JUEGOS,
                         "cintas + cartuchos tiene que dar el total")
        for nombre, n in (("terminados", mi.N_TERMINADOS),
                          ("con web", mi.N_CON_WEB),
                          ("cintas", mi.N_CINTAS),
                          ("cartuchos", mi.N_CARTUCHOS)):
            self.assertGreater(n, 0, "%s no puede ser cero" % nombre)
            self.assertLessEqual(n, mi.N_JUEGOS,
                                 "%s no puede pasar del total" % nombre)
        # y lo que se publica es lo que se ha calculado
        for ruta in PAGINAS:
            with open(ruta, encoding="utf-8") as f:
                pagina = f.read()
            for n, rotulo in ((mi.N_TERMINADOS, "terminados al 100 %"),
                              (mi.N_TERMINADOS, "finished at 100%")):
                if rotulo in pagina:
                    self.assertIn("<b>%d</b><span>%s</span>" % (n, rotulo),
                                  pagina, "%s no publica %d %s"
                                  % (os.path.basename(ruta), n, rotulo))

    def test_cada_pagina_lleva_al_otro_idioma(self):
        """El selector de idioma va en el menu de arriba, con su rotulo."""
        menu_en, menu_es = menu_de(lee(PAGINAS[0])), menu_de(lee(PAGINAS[1]))
        self.assertIn('href="es/"', menu_en)
        self.assertIn("En castellano", menu_en)
        self.assertIn('href="../"', menu_es)
        self.assertIn("In English", menu_es)

    def test_la_plataforma_se_llama_msx(self):
        """La primera generacion se llama MSX a secas: la familia es MSX, MSX2,
        MSX2+ y MSX turbo R, y "MSX1" no es nombre oficial. Se publico asi una
        temporada; esto evita que vuelva."""
        for pagina in PAGINAS:
            texto = re.sub(r"<[^>]+>", " ", lee(pagina))
            self.assertEqual(re.findall(r"\bMSX ?1\b", texto), [],
                             "%s: la plataforma vuelve a decir MSX1" % pagina)

    def test_no_se_cuelga_de_ningun_servidor_de_fuera(self):
        """Las paginas de la serie son autocontenidas: nada de CDN."""
        for pagina in PAGINAS:
            texto = lee(pagina)
            for etiqueta in re.findall(r"<(?:script|link)[^>]*>", texto):
                if "src=" in etiqueta or 'rel="stylesheet"' in etiqueta:
                    self.assertNotIn("//", etiqueta.split("href=")[-1][:8],
                                     "%s: recurso externo %s" % (pagina, etiqueta))

    # ---------------------------------------------------------- la jerarquia

    def test_los_grupos_son_los_pedidos(self):
        """Konami en su grupo; los tres de golf que no son de Konami, Ale
        Hop!, Temptations, Colt 36 y Demonia en los exclusivos de MSX; el resto
        en las conversiones. Y ninguno vacio."""
        mi = modulo()
        mi.comprueba()
        self.assertEqual([g["id"] for g in mi.GRUPOS],
                         ["konami", "msx-exclusive", "ports"])
        claves = {p["clave"] for p in mi.DESENSAMBLADOS}
        por_grupo = {g["id"]: {p["clave"] for p in mi.del_grupo(g["id"])}
                     for g in mi.GRUPOS}
        konami = {p["clave"] for p in mi.DESENSAMBLADOS
                  if p["meta"]["en"].startswith("Konami")}
        exclusivos = {"3dgolf", "holeinone", "casioworldopen", "alehop",
                      "temptations", "colt36", "demonia"}
        self.assertEqual(por_grupo["konami"], konami)
        self.assertEqual(por_grupo["msx-exclusive"], exclusivos)
        self.assertEqual(por_grupo["ports"], claves - konami - exclusivos)
        for gid, en_el in por_grupo.items():
            self.assertTrue(en_el, "el grupo %s se ha quedado sin juegos" % gid)
        # la lista crece, no encoge: los diecinueve publicados siguen ahi
        self.assertGreaterEqual(len(claves), 19)
        self.assertEqual(sum(len(g) for g in por_grupo.values()), len(claves))

    def test_cada_desensamblado_sale_una_vez_y_en_su_grupo(self):
        """Ningun repositorio perdido, ninguno repetido, cada uno en el grupo
        que dice su ficha y en el mismo orden; y ninguno fuera de su seccion."""
        mi = modulo()
        todos = sorted(nombre_repo(p) for p in mi.DESENSAMBLADOS)
        for pagina in PAGINAS:
            est = estructura(lee(pagina))
            des = est["disassemblies"]
            self.assertNotIn("", des,
                             "%s: hay tarjetas fuera de los grupos" % pagina)
            vistos = []
            for g in mi.GRUPOS:
                self.assertEqual(des[g["id"]],
                                 [nombre_repo(p) for p in mi.del_grupo(g["id"])],
                                 "%s: el grupo %s no lista lo que toca"
                                 % (pagina, g["id"]))
                vistos += des[g["id"]]
            self.assertEqual(sorted(vistos), todos,
                             "%s: se pierde o se repite un repositorio" % pagina)
            self.assertEqual(len(vistos), len(set(vistos)))
            for sid, partes in est.items():
                if sid == "disassemblies":
                    continue
                for repos in partes.values():
                    self.assertFalse(set(repos) & set(todos),
                                     "%s: un desensamblado en la seccion %s"
                                     % (pagina, sid))

    def test_los_parches_no_son_desensamblados(self):
        """Los parches tienen su seccion de primer nivel, hermana de la de los
        desensamblados, y las secciones salen en el orden de CATEGORIAS."""
        mi = modulo()
        for pagina in PAGINAS:
            est = estructura(lee(pagina))
            self.assertEqual(list(est), [c["id"] for c in mi.CATEGORIAS])
            self.assertEqual(est["patches"],
                             {"": [nombre_repo(p) for p in mi.PARCHES]})

    def test_los_dos_idiomas_tienen_la_misma_estructura(self):
        """Mismas secciones, mismas partes, mismos repos en cada una, en el
        mismo orden."""
        en, es = (estructura(lee(p)) for p in PAGINAS)
        self.assertEqual(en, es)

    def test_el_menu_lleva_a_cada_seccion_y_cada_parte(self):
        """Arriba, las secciones de primer nivel; dentro de una seccion con
        partes, su propio menu con todas ellas. Cada rotulo en su idioma."""
        mi = modulo()
        for pagina in PAGINAS:
            texto, idioma = lee(pagina), IDIOMA[pagina]
            menu = menu_de(texto)
            for c in mi.CATEGORIAS:
                self.assertIn('<a href="#%s">%s</a>' % (c["id"], c["menu"][idioma]),
                              menu, "%s: %s no esta en el menu" % (pagina, c["id"]))
                if not c.get("partes"):
                    continue
                cuerpo = re.search(r'<section id="%s">(.*?)</section>' % c["id"],
                                   texto, re.S).group(1)
                propio = re.search(r'<nav class="docs">(.*?)</nav>', cuerpo, re.S)
                self.assertIsNotNone(propio, "%s: %s no tiene menu propio"
                                     % (pagina, c["id"]))
                for p in c["partes"]:
                    self.assertIn('<a href="#%s">%s</a>'
                                  % (p["id"], p["titulo"][idioma]), propio.group(1))
                    self.assertIn('<div class="parte" id="%s">' % p["id"], cuerpo)
                    self.assertIn("<h3>%s" % p["titulo"][idioma], cuerpo)

    def test_los_rotulos_estan_en_los_dos_idiomas(self):
        """Cada rotulo de seccion, parte, grupo y menu tiene texto en 'en' y en
        'es', y los textos sueltos tienen las mismas claves en los dos."""
        mi = modulo()

        def bilingue(d, donde):
            self.assertEqual(set(d), {"en", "es"}, donde)
            for idioma, texto in d.items():
                self.assertTrue(isinstance(texto, str) and texto.strip(),
                                "%s: falta el texto en %s" % (donde, idioma))

        for c in mi.CATEGORIAS:
            for campo in ("titulo", "menu", "intro"):
                bilingue(c[campo], "%s.%s" % (c["id"], campo))
            for p in c.get("partes", []):
                bilingue(p["titulo"], "%s/%s" % (c["id"], p["id"]))
        for g in mi.GRUPOS:
            bilingue(g["titulo"], "grupo " + g["id"])
            # la cuenta del grupo dice el mismo numero en los dos idiomas
            proyectos = mi.del_grupo(g["id"])
            self.assertEqual(mi.cuenta(proyectos, "en").split()[0],
                             mi.cuenta(proyectos, "es").split()[0])
        self.assertEqual(set(mi.TXT["en"]), set(mi.TXT["es"]))
        for p in mi.DESENSAMBLADOS + mi.PARCHES:
            for campo in ("meta", "claim", "datos", "nota"):
                self.assertEqual(set(p[campo]), {"en", "es"},
                                 "%s.%s" % (p["clave"], campo))


if __name__ == "__main__":
    unittest.main()
