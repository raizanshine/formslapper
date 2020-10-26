from dataclasses import dataclass, field


@dataclass(init=False)
class Option:
    label: str
    value: str
