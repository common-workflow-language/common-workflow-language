from . import main
import sys
if sys.version_info != (2,6):
    import typing

sys.exit(main.main())
