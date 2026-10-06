from .linux_basics import CONTENT as _BASICS
from .linux_file_permissions import BLOCKS as _PERMISSIONS

# lesson slug -> list of (block type name, content)
CONTENT = {**_BASICS, "linux-file-permissions": _PERMISSIONS}
