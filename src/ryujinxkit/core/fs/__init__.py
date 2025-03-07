from .node import Node
from .resolver import resolver

[
    resolver[node].mkdir(parents=True, exist_ok=True)
    for node in [
        Node.RYUJINXKIT_ROAMING_DATA,
        Node.RYUJINX_ROAMING_DATA,
        Node.RYUJINXKIT_SAVE_FOLDER,
    ]
]
