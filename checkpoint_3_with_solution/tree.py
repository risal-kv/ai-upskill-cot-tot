from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import VIZ_LAYOUT, dbg


@dataclass
class ThoughtNode:
    id: int
    player: str                 # "O" or "X" for the move that produced this node (ROOT for root)
    r: Optional[int]            # row of move that led here (None for root)
    c: Optional[int]            # col of move that led here (None for root)
    reason: Optional[str]       # rationale attached to the edge into this node
    score_after: int            # score of THIS state from O's perspective
    depth: int
    terminal: bool = False
    outcome: Optional[str] = None   # "O", "X", "draw", or None
    parent: Optional[int] = None
    children: List[int] = field(default_factory=list)


class ThoughtTree:
    """
    Stores the full explored tree. Each node represents a STATE after a move.
    Edge data (move, reason) are stored on the child node (r, c, reason).
    """
    def __init__(self):
        self._next_id = 0
        self.nodes: Dict[int, ThoughtNode] = {}
        self.root_id: Optional[int] = None

    def _new_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def add_root(self, score_after: int) -> int:
        nid = self._new_id()
        self.nodes[nid] = ThoughtNode(
            id=nid, player="ROOT", r=None, c=None, reason=None,
            score_after=score_after, depth=0, terminal=False, outcome=None,
            parent=None, children=[]
        )
        self.root_id = nid
        return nid

    def add_child(self, parent_id: int, player: str, r: int, c: int, reason: str, score_after: int,
                  terminal: bool, outcome: Optional[str]) -> int:
        nid = self._new_id()
        parent = self.nodes[parent_id]
        node = ThoughtNode(
            id=nid, player=player, r=r, c=c, reason=reason,
            score_after=score_after, depth=parent.depth + 1,
            terminal=terminal, outcome=outcome, parent=parent_id
        )
        self.nodes[nid] = node
        parent.children.append(nid)
        return nid

    # ----- visualization -----

    def pretty(self, node_id: Optional[int] = None, prefix: str = "") -> str:
        if node_id is None:
            node_id = self.root_id
        if node_id is None:
            return "<empty tree>"

        node = self.nodes[node_id]
        move_str = "root" if node.r is None else f"{node.player}→({node.r},{node.c})"
        term_str = f"  [terminal:{node.outcome}]" if node.terminal else ""
        line = f"{prefix}• (#{node.id}) {move_str} | score={node.score_after}{term_str}"
        if node.reason:
            line += f" — {node.reason}"

        lines = [line]
        for i, cid in enumerate(node.children):
            last = (i == len(node.children) - 1)
            branch = "└─ " if last else "├─ "
            child_prefix = prefix + ("   " if last else "│  ")
            lines.append(self.pretty(cid, prefix + branch))
            if len(self.nodes[cid].children) > 0:
                sub = self._pretty_children(self.nodes[cid], child_prefix)
                if sub:
                    lines[-1] = lines[-1].split("\n", 1)[0]
                    lines.append(sub)
        return "\n".join(lines)

    def _pretty_children(self, node: ThoughtNode, prefix: str) -> str:
        lines = []
        for i, cid in enumerate(node.children):
            last = (i == len(node.children) - 1)
            branch = "└─ " if last else "├─ "
            child = self.nodes[cid]
            move_str = f"{child.player}→({child.r},{child.c})"
            term_str = f"  [terminal:{child.outcome}]" if child.terminal else ""
            line = f"{prefix}{branch}• (#{child.id}) {move_str} | score={child.score_after}{term_str}"
            if child.reason:
                line += f" — {child.reason}"
            lines.append(line)
            if child.children:
                sub_prefix = prefix + ("   " if last else "│  ")
                lines.append(self._pretty_children(child, sub_prefix))
        return "\n".join(lines)

    def to_dot(self) -> str:
        if self.root_id is None:
            return "digraph G {}"
        lines = ["digraph G {", '  node [shape=box, fontname="Helvetica"];']
        for nid, n in self.nodes.items():
            label_move = "root" if n.r is None else f"{n.player}→({n.r},{n.c})"
            term = f"\\nterminal={n.outcome}" if n.terminal else ""
            reason = f"\\nreason={n.reason.replace('\\"','\\\\\"')}" if n.reason else ""
            lines.append(f'  n{nid} [label="#{nid} {label_move}\\nscore={n.score_after}{term}{reason}"];')
        for nid, n in self.nodes.items():
            for cid in n.children:
                lines.append(f"  n{nid} -> n{cid};")
        lines.append("}")
        return "\n".join(lines)
