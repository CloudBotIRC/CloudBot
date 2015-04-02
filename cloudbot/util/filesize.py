"""
Zope Public License (ZPL) Version 2.1

A copyright notice accompanies this license document that identifies
the copyright holders.

This license has been certified as open source. It has also been
designated as GPL compatible by the Free Software Foundation (FSF).

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

 1. Redistributions in source code must retain the accompanying
    copyright notice, this list of conditions, and the following
    disclaimer.

 2. Redistributions in binary form must reproduce the accompanying
    copyright notice, this list of conditions, and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

 3. Names of the copyright holders must not be used to endorse or
    promote products derived from this software without prior written
    permission from the copyright holders.

 4. The right to distribute this software or to use it for any purpose
    does not give you the right to use Servicemarks (sm) or Trademarks
    (tm) of the copyright holders. Use of them is covered by separate
    agreement with the copyright holders.

 5. If any files are modified, you must cause the modified files to
    carry prominent notices stating that you changed the files and the
    date of any change.

Disclaimer

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This software consists of contributions made by Zope Corporation and
many individuals on behalf of Zope Corporation. Specific attributions
are listed in the accompanying credits file.
"""

traditional = [
    (1024 ** 5, 'P'),
    (1024 ** 4, 'T'),
    (1024 ** 3, 'G'),
    (1024 ** 2, 'M'),
    (1024 ** 1, 'K'),
    (1024 ** 0, 'B'),
]

alternative = [
    (1024 ** 5, ' PB'),
    (1024 ** 4, ' TB'),
    (1024 ** 3, ' GB'),
    (1024 ** 2, ' MB'),
    (1024 ** 1, ' KB'),
    (1024 ** 0, (' byte', ' bytes')),
]

verbose = [
    (1024 ** 5, (' petabyte', ' petabytes')),
    (1024 ** 4, (' terabyte', ' terabytes')),
    (1024 ** 3, (' gigabyte', ' gigabytes')),
    (1024 ** 2, (' megabyte', ' megabytes')),
    (1024 ** 1, (' kilobyte', ' kilobytes')),
    (1024 ** 0, (' byte', ' bytes')),
]

iec = [
    (1024 ** 5, 'Pi'),
    (1024 ** 4, 'Ti'),
    (1024 ** 3, 'Gi'),
    (1024 ** 2, 'Mi'),
    (1024 ** 1, 'Ki'),
    (1024 ** 0, ''),
]

si = [
    (1000 ** 5, 'P'),
    (1000 ** 4, 'T'),
    (1000 ** 3, 'G'),
    (1000 ** 2, 'M'),
    (1000 ** 1, 'K'),
    (1000 ** 0, 'B'),
]

# re.I style aliases
T = traditional
A = alternative
V = verbose
I = iec
S = si


def size(b, system=traditional):
    """Human-readable file size.

    Using the traditional system, where a factor of 1024 is used::
    
    >>> size(10)
    '10B'
    >>> size(100)
    '100B'
    >>> size(1000)
    '1000B'
    >>> size(2000)
    '1K'
    >>> size(10000)
    '9K'
    >>> size(20000)
    '19K'
    >>> size(100000)
    '97K'
    >>> size(200000)
    '195K'
    >>> size(1000000)
    '976K'
    >>> size(2000000)
    '1M'
    
    Using the SI system, with a factor 1000::

    >>> size(10, system=si)
    '10B'
    >>> size(100, system=si)
    '100B'
    >>> size(1000, system=si)
    '1K'
    >>> size(2000, system=si)
    '2K'
    >>> size(10000, system=si)
    '10K'
    >>> size(20000, system=si)
    '20K'
    >>> size(100000, system=si)
    '100K'
    >>> size(200000, system=si)
    '200K'
    >>> size(1000000, system=si)
    '1M'
    >>> size(2000000, system=si)
    '2M'
    
    """
    for factor, suffix in system:
        if b >= factor:
            break
    amount = int(b / factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix
