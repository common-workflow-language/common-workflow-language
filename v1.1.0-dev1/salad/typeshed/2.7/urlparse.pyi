# Stubs for urlparse (Python 2)

from typing import AnyStr, Dict, List, NamedTuple, Tuple, Sequence, Union, overload

uses_relative = []  # type: List[str]
uses_netloc = []  # type: List[str]
uses_params = []  # type: List[str]
non_hierarchical = []  # type: List[str]
uses_query = []  # type: List[str]
uses_fragment = []  # type: List[str]
scheme_chars = ...  # type: str
MAX_CACHE_SIZE = 0

def clear_cache() -> None: ...

class ResultMixin(object):
    @property
    def username(self) -> str: ...
    @property
    def password(self) -> str: ...
    @property
    def hostname(self) -> str: ...
    @property
    def port(self) -> int: ...

class SplitResult(NamedTuple('SplitResult', [
        ('scheme', str), ('netloc', str), ('path', str), ('query', str), ('fragment', str)
    ]), ResultMixin):
    def geturl(self) -> str: ...

class SplitResultU(NamedTuple('SplitResultU', [
        ('scheme', unicode),
	('netloc', unicode),
	('path', unicode),
	('query', unicode),
	('fragment', unicode)
    ]), ResultMixin):
    def geturl(self) -> unicode: ...

class ParseResult(NamedTuple('ParseResult', [
        ('scheme', str), ('netloc', str), ('path', str), ('params', str), ('query', str),
        ('fragment', str)
    ]), ResultMixin):
    def geturl(self) -> str: ...

class ParseResultU(NamedTuple('ParseResultU', [
        ('scheme', unicode),
	('netloc', unicode),
	('path', unicode),
	('params', unicode),
	('query', unicode),
        ('fragment', unicode)
    ]), ResultMixin):
    def geturl(self) -> unicode: ...

@overload
def urlparse(url: str, scheme: str = ..., allow_fragments: bool = ...) -> ParseResult: ...
@overload
def urlparse(url: unicode, scheme: unicode = ..., allow_fragments: bool = ...) -> ParseResultU: ...
@overload
def urlsplit(url: str, scheme: str = ..., allow_fragments: bool = ...) -> SplitResult: ...
@overload
def urlsplit(url: unicode, scheme: unicode = ..., allow_fragments: bool = ...) -> SplitResultU: ...
@overload
def urlunparse(data: Tuple[AnyStr, AnyStr, AnyStr, AnyStr, AnyStr, AnyStr]) -> AnyStr: ...
@overload
def urlunparse(data: Sequence[AnyStr]) -> AnyStr: ...
@overload
def urlunsplit(data: Tuple[AnyStr, AnyStr, AnyStr, AnyStr, AnyStr]) -> AnyStr: ...
@overload
def urlunsplit(data: Sequence[AnyStr]) -> AnyStr: ...
def urljoin(base: Union[str, unicode], url: Union[str, unicode], allow_fragments: bool = ...) -> str: ...
def urldefrag(url: Union[str, unicode]) -> str: ...
def unquote(s: str) -> str: ...
def parse_qs(qs: str, keep_blank_values: bool = ...,
             strict_parsing: bool = ...) -> Dict[str, List[str]]: ...
def parse_qsl(qs: str, keep_blank_values: int = ...,
              strict_parsing: bool = ...) -> List[Tuple[str, str]]: ...
