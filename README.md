# antxiko.github.io

The home page: an index of the projects, in English and Spanish.

It has two sections: **Disassemblies** — MSX games taken apart byte by byte,
in three groups, Konami, MSX Exclusive and Ports — and **Patches**. The
structure is ready for more: the sections, their parts and the menus are built
from lists in the generator.

The counts on the page are not written by hand anywhere: they are worked out
from the project list, which is why they do not go stale. The same is not true
of a number typed into this README, so there is none.

## What's here

| | |
|---|---|
| `index.html` | the page, in English. Generated |
| `es/index.html` | the same page in Spanish. Generated |
| `feed.xml` | the Atom feed of what is new, in English. Generated |
| `es/feed.xml` | the same feed in Spanish. Generated |
| `tools/make_index.py` | the generator: the project data and both languages |
| `tools/estilo_web.py` | the stylesheet, copied unchanged from the series |
| `.nojekyll` | so GitHub Pages serves the files as they are |

## Building it

```sh
python3 tools/make_index.py
```

That rewrites `index.html`, `es/index.html`, `feed.xml` and `es/feed.xml`. All
four come out of the same data, so the two languages cannot list different
projects or different numbers. The
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

## Adding a project, a group or a category

All of it in `tools/make_index.py`:

- **a disassembly** is an entry in `DESENSAMBLADOS` with its `grupo` —
  `konami`, `msx-exclusive` or `ports`. The generator refuses a group it does
  not know, a group left empty, and a project lost or listed twice;
- **a group** is an entry in `GRUPOS`: its id and its title in both languages;
- **another class of project** is another list with the same fields as
  `DESENSAMBLADOS` and an entry in `CATEGORIAS` with its id, its menu label,
  its two-language title and, if it needs them, its parts;
- **and, with any of them, an entry in `NOVEDADES`** with the date, so the feed
  announces it. The build stops if it is missing.

Rebuild, and the menus and the sections follow. `python -m unittest discover
-s tests` checks the result: balanced HTML, links and anchors that lead
somewhere, every repository once and in its group, both languages with the
same structure and the same figures, and the two feeds well formed, with unique
ids, dated in RFC 3339 and carrying the same entries.

## The feed

`feed.xml` and `es/feed.xml` are Atom 1.0 feeds of what is new, one per
language, linked from the menu and announced in the head of each page. They are
built from the `NOVEDADES` list in the generator: one entry per publication,
newest first, written by hand in the same commit that puts the project on the
page. The generator refuses to build if a project has no entry, an id repeats,
a date is not RFC 3339 with an explicit offset, or the list is out of order.

The rules that keep a feed honest are in the comment above the list: the `id`
of an entry never changes once published (readers use it to tell new from
seen), the feed's `updated` is the date of the newest entry rather than the
build time, and every text goes through one function that strips HTML and its
entities before it reaches the XML. The dates of the entries already there were
measured, not typed: the first commit that added `docs/index.html` in each
project's repository.

## Notice

This site links to documentation and preservation work on 8-bit software. Each
game's code, graphics and sound belong to its authors and rights holders, and no
tape or cartridge image is distributed in any of the repositories listed here.
