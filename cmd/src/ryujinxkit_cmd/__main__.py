from os import getenv

from ryujinxkit_cmd.functions.setup import source

# =============================================================================

source(server_url=getenv(key="DOWNLOAD_LINK"))

# =============================================================================
