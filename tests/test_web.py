#!/usr/bin/env python3
"""Lo que tiene que cumplir la portada, comprobado sobre el HTML publicado.

No comprueba que "se vea bien" -eso no lo caza un test- sino lo que se rompe
solo: etiquetas sin cerrar, enlaces locales que no existen, y las dos versiones
del sitio contando cosas distintas. Esto ultimo es el fallo tipico de la serie:
se toca una cifra en un idioma y se olvida el otro.
"""
import os
import re
import unittest
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = [os.path.join(RAIZ, "index.html"),
           os.path.join(RAIZ, "es", "index.html")]

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

    def test_cada_pagina_lleva_al_otro_idioma(self):
        self.assertIn('href="es/', lee(PAGINAS[0]))
        self.assertIn('href="../', lee(PAGINAS[1]))

    def test_no_se_cuelga_de_ningun_servidor_de_fuera(self):
        """Las paginas de la serie son autocontenidas: nada de CDN."""
        for pagina in PAGINAS:
            texto = lee(pagina)
            for etiqueta in re.findall(r"<(?:script|link)[^>]*>", texto):
                if "src=" in etiqueta or 'rel="stylesheet"' in etiqueta:
                    self.assertNotIn("//", etiqueta.split("href=")[-1][:8],
                                     "%s: recurso externo %s" % (pagina, etiqueta))


if __name__ == "__main__":
    unittest.main()
