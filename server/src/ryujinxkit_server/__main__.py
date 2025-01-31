from ryujinxkit_server.constants.server import SERVER
from ryujinxkit_server.session import Session

# =============================================================================

with Session:
    SERVER.run(debug=True)

# =============================================================================
