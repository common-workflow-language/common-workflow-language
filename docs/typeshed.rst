How to add new types to the local Typeshed
------------------------------------------


If when running ``make mypy`` you receive errors about modules that can't be
found you may need to add type stubs for new modules to the ``typeshed/``
directory.

::

 mkdir out
 stubgen --py2 module_name
 mv out/module_name/* typeshed/2.7/
 make mypy

Note: the module name is not always the name of the PyPI package
(``CacheControl`` vs ``cachecontrol``).

Stubs are just that, you will still need to annotate whichever functions you
call.

Oftentimes it is simpler to comment out imports in the ``.pyi`` stubs that are
not needed yet. The goal is represent the public API, or at least the part we
use.
