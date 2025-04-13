"""Arithmetic tools."""


def megabytes(byte_total: int):
    """
    Converts bytes to megabytes.

    :param byte_total: Quantity of bytes to convert.

    :returns: Provided byte-total in megabytes.
    """

    return byte_total / pow(2, 20)
