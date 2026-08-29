# antxiko.github.io

The home page: an index of the projects, in English and Spanish.

It lists two categories, **Disassemblies** — MSX games taken apart byte by
byte — and **Patches**, and the structure is ready for more: categories are a
list in the generator, and the menu and the sections are built from it.

The counts on the page are not written by hand anywhere: they are worked out
from the project list, which is why they do not go stale. The same is not true
of a number typed into this README, so there is none.

## What's here

| | |
|---|---|
| `index.html` | the page, in English. Generated |
| `es/index.html` | the same page in Spanish. Generated |
| `tools/make_index.py` | the generator: the project data and both languages |
| `tools/estilo_web.py` | the stylesheet, copied unchanged from the series |
| `.nojekyll` | so GitHub Pages serves the files as they are |

## Building it

```sh
python3 tools/make_index.py
```

That rewrites `index.html` and `es/index.html`. Both come out of the same data,
so the two languages cannot list different projects or different numbers. The
CSS goes inline in each page: nothing is fetched from a CDN, and the pages work
on their own.

## Where the numbers come from

Nothing on the page is written from memory. For each project:

- **the repository URL** is its `git remote -v`;
- **the figures and the sentences** come from that project's `README.md` /
  `README.es.md` and its `docs/`;
- **the website URL** is derived from the remote —
  `https://<user>.github.io/<repo>/` — and only for projects that actually have
  a `docs/index.html`. A project without one gets no website link;
- a project whose repository is not public gets **no link at all**, because a
  link a visitor cannot open is worse than none.

So when a project moves on — a site published, a percentage that goes up — the
figures here have to be re-read from that project before they are changed here.

## The design

The look is the series': `tools/estilo_web.py` is the same file the games'
websites use, copied over unchanged. The only thing added on top is the project
card, kept in `EXTRA` inside the generator and built out of the same variables
(`--panel`, `--linea`, `--oro`…) and the same grid mechanism as the figure
tiles, so it sits in light and dark themes exactly like the rest.

## Adding a category

In `tools/make_index.py`, write another list of projects with the same fields as
`DESENSAMBLADOS`, add an entry to `CATEGORIAS` with its id, its menu label and
its two-language title, and rebuild. The nav and the sections follow.

## Notice

This site links to documentation and preservation work on 8-bit software. Each
game's code, graphics and sound belong to its authors and rights holders, and no
tape or cartridge image is distributed in any of the repositories listed here.
