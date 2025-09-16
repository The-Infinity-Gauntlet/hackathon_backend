from typing import Dict, Iterable, List


class SafeOrderingMixin:
    """Mixin para aplicar ordenação com whitelist de campos.

    Configure no view:
      - ordering_map: Dict[str, str] com campos permitidos (client -> ORM field)
      - default_ordering: str | List[str] com ordenação padrão (ex.: "description")
    """

    ordering_map: Dict[str, str] = {}
    default_ordering: Iterable[str] | str = ()

    def parse_ordering(self, ordering_param: str | None) -> List[str]:
        if not ordering_param:
            # normalize default_ordering to list[str]
            if isinstance(self.default_ordering, str):
                return [self.default_ordering]
            return list(self.default_ordering) or []

        parts = str(ordering_param).split(",")
        out: List[str] = []
        for part in parts:
            p = part.strip()
            if not p:
                continue
            desc = p.startswith("-")
            key = p[1:] if desc else p
            field = self.ordering_map.get(key)
            if not field:
                continue
            out.append(("-" if desc else "") + field)
        if not out:
            # fallback to default
            if isinstance(self.default_ordering, str):
                return [self.default_ordering]
            return list(self.default_ordering) or []
        return out

    def apply_ordering(self, qs, ordering_param: str | None):
        order_bys = self.parse_ordering(ordering_param)
        return qs.order_by(*order_bys) if order_bys else qs
