import collections
from six.moves import urllib
from typing import List, Text, Dict, Union, Any
from . import schema
from .schema import shortname

class TypeDef(object):
    def __init__(self, name, init):
        # type: (Text, Text) -> None
        self.name = name
        self.init = init

class CodeGenBase(object):
    def __init__(self):
        # type: () -> None
        self.collected_types = collections.OrderedDict()  # type: collections.OrderedDict[Text, TypeDef]
        self.vocab = {}  # type: Dict[Text, Text]

    def declare_type(self, t):
        # type: (TypeDef) -> TypeDef
        if t not in self.collected_types:
            self.collected_types[t.name] = t
        return t

    def add_vocab(self, name, uri):
        # type: (Text, Text) -> None
        self.vocab[name] = uri

    def prologue(self):
        # type: () -> None
        raise NotImplementedError()

    def safe_name(self, n):
        # type: (Text) -> Text
        return schema.avro_name(n)

    def begin_class(self, classname, extends, doc, abstract):
        # type: (Text, List[Text], Text, bool) -> None
        raise NotImplementedError()

    def end_class(self, classname):
        # type: (Text) -> None
        raise NotImplementedError()

    def type_loader(self, t):
        # type: (Union[List[Any], Dict[Text, Any]]) -> TypeDef
        raise NotImplementedError()

    def declare_field(self, name, typedef, doc, optional):
        # type: (Text, TypeDef, Text, bool) -> None
        raise NotImplementedError()

    def declare_id_field(self, name, typedef, doc):
        # type: (Text, TypeDef, Text) -> None
        raise NotImplementedError()

    def uri_loader(self, inner, scoped_id, vocab_term, refScope):
        # type: (TypeDef, bool, bool, Union[int, None]) -> TypeDef
        raise NotImplementedError()

    def idmap_loader(self, field, inner, mapSubject, mapPredicate):
        # type: (Text, TypeDef, Text, Union[Text, None]) -> TypeDef
        raise NotImplementedError()

    def typedsl_loader(self, inner, refScope):
        # type: (TypeDef, Union[int, None]) -> TypeDef
        raise NotImplementedError()

    def epilogue(self, rootLoader):
        # type: (TypeDef) -> None
        raise NotImplementedError()
