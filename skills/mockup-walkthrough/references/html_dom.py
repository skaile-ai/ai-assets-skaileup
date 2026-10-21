"""html_dom.py — minimal parent/child DOM tree shared by both renderers' validators.

The flat attribute collector in each `validator.py` is enough for
attribute-presence checks; the target, content-fidelity and floorplan checks
need parent/child relationships (e.g. "is this node wrapped by an <a>", "how
many <tr> inside this <table>'s <tbody>"). Stdlib only.

Validators import this module through a `sys.path` insert of their parent
directory (`references/`), which travels with the installed skill directory.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class DomNode:
    __slots__ = ("tag", "attrs", "parent", "children")

    def __init__(
        self,
        tag: str,
        attrs: dict[str, str],
        parent: "DomNode | None",
    ) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list["DomNode"] = []


class DomTreeParser(HTMLParser):
    """Builds a minimal parent/child tree of tag/attrs nodes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = DomNode("#root", {}, None)
        self._stack: list[DomNode] = [self.root]

    def _open(self, tag: str, attrs: list, self_closing: bool) -> None:
        node = DomNode(tag, dict(attrs), self._stack[-1])
        self._stack[-1].children.append(node)
        if not self_closing and tag not in VOID_TAGS:
            self._stack.append(node)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self._open(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self._open(tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):
            if self._stack[i].tag == tag:
                del self._stack[i:]
                return


def parse_dom(path: Path) -> DomNode:
    parser = DomTreeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.root


def iter_nodes(node: DomNode):
    yield node
    for child in node.children:
        yield from iter_nodes(child)


def find_all(node: DomNode, predicate) -> list[DomNode]:
    return [n for n in iter_nodes(node) if predicate(n)]


def find_first(node: DomNode, predicate) -> DomNode | None:
    for n in iter_nodes(node):
        if predicate(n):
            return n
    return None
