# Last Modified: 2016.05.08 /coding: utf-8
#  vim:tw=0:ts=4:sw=4:et

from collections import OrderedDict

#from exceptions import EncodingError
import bhencode

# Encoding keys:
#    str:         <len>: ...
#    bytes:       <len>: ...
#    bool:        T or F
#    int:         i ... e
#    tuple:       t ... e
#    list:        l ... e
#    OrderedDict: D ... e
#    dict:        d ... e
#    float:       f ... e
#    None:        N

# FIXME/EXPLAIN: Why is encode a fcn. and Decode a class?
def encode(obj, encoding='utf-8', strict=True):

    coded_byte_list = []

    def __encode_str(s: str) -> None:
        """Converts the input string to bytes and passes it the __encode_byte_str function for encoding."""
        b = bytes(s, encoding)
        __encode_byte_str(b)

    def __encode_byte_str(b: bytes) -> None:
        """Ben-encodes string from bytes."""
        nonlocal coded_byte_list
        length = len(b)
        coded_byte_list.append(bytes(str(length), encoding) + b':' + b)

    # Non-standard ben-encoding.
    def __encode_bool(b: bool) -> None:
        """Ben-encodes boolean from bool."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'T' if b else b'F')

    def __encode_int(i: int) -> None:
        """Ben-encodes integer from int."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'i' + bytes(str(i), 'utf-8') + b'e')

    def __encode_tuple(t: tuple) -> None:
        """Converts the input tuple to lists and passes it the __encode_list function for encoding."""
        l = [i for i in t]
        __encode_list(l, leader=b't')

    def __encode_list(l: list, leader=b'l') -> None:
        """Ben-encodes list from list."""
        nonlocal coded_byte_list
        coded_byte_list.append(leader)
        for i in l:
            __select_encoder(i)
        coded_byte_list.append(b'e')

    def __encode_ordered_dict(d: dict) -> None:
        """Ben-encodes dictionary from OrderedDict."""
        __encode_dict(d, b'D')

    def __encode_dict(d: dict, leader=b'd') -> None:
        """Ben-encodes dictionary from dict."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'd')
        # 2016.01.14: [lb] wonders why the master BencodePy project
        # doesn't sort the dictionary -- isn't that the whole point
        # of bencoding?
        # From https://en.wikipedia.org/wiki/Bencode:
        # "All keys must be byte strings and must appear in lexicographical order."
        # Thus, the original code seems wrong:
        #   for k in d:
        for k in sorted(d.keys()):
            __select_encoder(k)
            __select_encoder(d[k])
        coded_byte_list.append(b'e')

    # Non-standard ben-encoding.
    def __encode_float(i: float) -> None:
        """Ben-encodes floating point number from float."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'f' + bytes(str(i), 'utf-8') + b'e')

    # Non-standard ben-encoding.
    def __encode_none(i: None) -> None:
        """Ben-encodes None from nothing."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'N')

    opt = {
        str: lambda x: __encode_str(x),
        bytes: lambda x: __encode_byte_str(x),
        bool: lambda x: __encode_bool(x),
        int: lambda x: __encode_int(x),
        tuple: lambda x: __encode_tuple(x),
        list: lambda x: __encode_list(x),
        OrderedDict: lambda x: __encode_ordered_dict(x),
        dict: lambda x: __encode_dict(x),
        float: lambda x: __encode_float(x),
        None: lambda x: __encode_none(x),
    }

    def __select_encoder(o: object) -> bytes:
        """Calls the appropriate function to encode the passed object (obj)."""

        nonlocal opt

        t = type(o)
        if t in opt:
            opt[t](o)
        else:
            if isinstance(o, str):
                __encode_str(o)
            elif isinstance(o, bytes):
                __encode_byte_str(o)
            # isinstance(True, int) is True, so process bool before int.
            elif isinstance(o, bool):
                __encode_bool(o)
            elif isinstance(o, int):
                __encode_int(o)
            elif isinstance(o, tuple):
                __encode_tuple(o)
            elif isinstance(o, list):
                __encode_list(o)
            elif isinstance(o, OrderedDict):
                __encode_ordered_dict(o)
            elif isinstance(o, dict):
                __encode_dict(o)
            # The rest are non-standard ben-encodings, used for object hashing.
            elif isinstance(o, float):
                __encode_float(o)
            elif o is None:
                __encode_none(o)
            # FIXME: Should probably support 'set'.
            # Skipping types: 'complex', 'range', 'bytearray', 'memoryview',
            # 'frozenset', 'Ellipsis', 'type', 'NotImplemented', 'module'.
            else:
                if strict:
                    nonlocal coded_byte_list
                    coded_byte_list = []
                    raise bhencode.EncodingError("Unable to encode object: {0}".format(o.__repr__()))
                else:
                    print("Unable to encode object: {0}".format(str(o)))

    __select_encoder(obj)

    return b''.join(coded_byte_list)
