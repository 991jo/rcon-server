def to_int32(value):
    """:return: A byte array containing the value as a 32 bit signed little
    endian integer.

    This raises an OverflowError when the value does not fit into a 32 bit
    Integer.

    :param value: int
    """
    # to_bytes raises an OverflowError when the value does not fit
    return value.to_bytes(4, byteorder="little", signed=True)

def from_int32(value):
    """
    :return: A int from the given bytes.
    :param value: a array or iterable of bytes
    """

    return int.from_bytes(value, byteorder="little", signed=True)

def check_int32(value):
    """
    :return: True if the value fits in a 32 bit signed int, False
    otherwise.
    :param value: a int
    """
    try:
        to_int32(value)
        return True
    except Exception:
        return False
