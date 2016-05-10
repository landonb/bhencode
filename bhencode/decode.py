# Last Modified: 2016.05.08 /coding: utf-8
#  vim:tw=0:ts=4:sw=4:et

from collections import OrderedDict
from collections.abc import Iterable

import bhencode

class Decode:

    def __init__(self, data: bytes, encoding='utf-8'):
        self.data = data
        self.encoding = encoding
        self.idx = 0

    def __read(self, i: int) -> bytes:
        """Returns a set number (i) of bytes from self.data."""
        b = self.data[self.idx: self.idx + i]
        self.idx += i
        if len(b) != i:
            raise bhencode.DecodingError(
                "Incorrect byte length returned between indexes of {0} and {1}. "
                "Possible unexpected End of File."
                    .format(str(self.idx), str(self.idx - i)))
        if self.encoding:
            b = b.decode(self.encoding)
        return b

    def __read_to(self, terminator: bytes) -> bytes:
        """Returns bytes from self.data starting at index (self.idx) until terminator character."""
        try:
            # noinspection PyTypeChecker
            i = self.data.index(terminator, self.idx)
            b = self.data[self.idx:i]
            self.idx = i + 1
            return b
        except ValueError:
            raise bhencode.DecodingError(
                'Unable to locate terminator character "{0}" after index {1}.'
                    .format(str(terminator), str(self.idx))
            )

    def __parse(self) -> object:
        """Selects the appropriate method to decode next bencode element and returns the result."""
        char = self.data[self.idx: self.idx + 1]
        if char in [b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0']:
            # FIXME: This'll raise ValueError if not an int...
            str_len = int(self.__read_to(b':'))
            return self.__read(str_len)
        elif char == b'T':
            self.idx += 1
            return True
        elif char == b'F':
            self.idx += 1
            return False
        elif char == b'i':
            self.idx += 1
            return int(self.__read_to(b'e'))
        elif char == b't':
            return tuple(self.__parse_list())
        elif char == b'l':
            return self.__parse_list()
        elif char == b'D':
            return OrderedDict(self.__parse_dict())
        elif char == b'd':
            return self.__parse_dict()
        elif char == b'f':
            self.idx += 1
            return float(self.__read_to(b'e'))
        elif char == b'N':
            self.idx += 1
            return None
        elif char == b'':
            raise bhencode.DecodingError('Unexpected End of File at index position of {0}.'
                .format(str(self.idx))
            )
        else:
            raise bhencode.DecodingError(
                'Invalid token character ({0}) at position {1}.'
                .format(str(char), str(self.idx))
            )

    def decode(self) -> Iterable:
        """Start of decode process. Returns final results."""
        if self.data[0:1] not in (b'd', b'l'):
            return self.__wrap_with_tuple()
        return self.__parse()

    def __wrap_with_tuple(self) -> tuple:
        """Returns a tuple of all nested bencode elements."""
        l = list()
        length = len(self.data)
        while self.idx < length:
            l.append(self.__parse())
        return tuple(l)

#    def __parse_dict(self) -> OrderedDict:
    def __parse_dict(self) -> dict:
        """Returns an Ordered Dictionary of nested bencode elements."""
        self.idx += 1
#        d = OrderedDict()
        d = dict()
        key_name = None
        while self.data[self.idx: self.idx + 1] != b'e':
            if key_name is None:
                key_name = self.__parse()
            else:
                d[key_name] = self.__parse()
                key_name = None
        self.idx += 1
        return d

    def __parse_list(self) -> list:
        """Returns an list of nested bencode elements."""
        self.idx += 1
        l = []
        while self.data[self.idx: self.idx + 1] != b'e':
            l.append(self.__parse())
        self.idx += 1
        return l


def decode_from_file(path: str) -> Iterable:
    """Convenience function. Reads file and calls decode()."""
    with open(path, 'rb') as f:
        b = f.read()
    return decode(b)


def decode(data: bytes) -> Iterable:
    """Convenience function. Initializes Decode class, calls decode method, and returns the result."""
    decoder = Decode(data)
    return decoder.decode()
