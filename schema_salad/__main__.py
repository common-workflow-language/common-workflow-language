from . import main
import sys
if sys.version_info >= (2,7):
    import typing

sys.exit(main.main())
