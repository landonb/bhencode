from . import EncodingError
from collections import OrderedDict


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

    def __encode_int(i: int) -> None:
        """Ben-encodes integer from int."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'i' + bytes(str(i), 'utf-8') + b'e')

    def __encode_tuple(t: tuple) -> None:
        """Converts the input tuple to lists and passes it the __encode_list function for encoding."""
        l = [i for i in t]
        __encode_list(l)

    def __encode_list(l: list) -> None:
        """Ben-encodes list from list."""
        nonlocal coded_byte_list
        coded_byte_list.append(b'l')
        for i in l:
            __select_encoder(i)
        coded_byte_list.append(b'e')

    def __encode_dict(d: dict) -> None:
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
        coded_byte_list.append(b'i' + bytes(str(i), 'utf-8') + b'e')

    # Non-standard ben-encoding.
    def __encode_none(i: None) -> None:
        """Ben-encodes None from nothing."""
        nonlocal coded_byte_list
        __encode_str(str(None))

    opt = {
        bytes: lambda x: __encode_byte_str(x),
        OrderedDict: lambda x: __encode_dict(x),
        dict: lambda x: __encode_dict(x),
        list: lambda x: __encode_list(x),
        str: lambda x: __encode_str(x),
        int: lambda x: __encode_int(x),
        tuple: lambda x: __encode_tuple(x),
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
            if isinstance(o, bytes):
                __encode_byte_str(o)
            elif isinstance(o, dict):
                __encode_dict(o)
            elif isinstance(o, list):
                __encode_list(o)
            elif isinstance(o, str):
                __encode_str(o)
            elif isinstance(o, int):
                __encode_int(o)
            elif isinstance(o, tuple):
                __encode_tuple(o)
            # The rest are non-standard ben-encodings, used for object hashing.
            elif isinstance(o, float):
                __encode_float(o)
            elif o is None:
                __encode_none(o)
            else:
                if strict:
                    nonlocal coded_byte_list
                    coded_byte_list = []
                    raise EncodingError("Unable to encode object: {0}".format(o.__repr__()))
                else:
                    print("Unable to encode object: {0}".format(str(o)))

    __select_encoder(obj)

    return b''.join(coded_byte_list)
