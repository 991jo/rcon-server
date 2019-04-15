def to_int32(value):
    """:return: A byte array containing the value as a 32 bit signed little
    endian integer.

    This raises an OverflowError when the value does not fit into a 32 bit
    Integer.

    :param value: int
    """
    # to_bytes raises an OverflowError when the value does not fit
    return value.to_bytes(4, byteorder="big", signed=True)
