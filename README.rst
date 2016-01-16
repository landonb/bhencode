bhencode
========

A simple Bencoder for Python based on
`BencodePy <https://github.com/eweast/BencodePy>`__.

Differences from BencodePy
--------------------------

- The encoder handles the non-standard elements, ``float`` and ``None``.

- The dict encoder is fixed so that dicts are sorted lexically by
  key name, otherwise the bencode string differs between uses.

Usage
-----

The author uses ``bhencode`` to produce MD5 hashes of Python objects.

.. code-block:: python

    import bhencode
    import hashlib

    hashlib.md5(bhencode.encode(raw_data)).hexdigest()

Installation
------------

The easiest way to install this library is using pip.

.. code-block:: bash

    git clone https://github.com/landonb/bhencode.git

