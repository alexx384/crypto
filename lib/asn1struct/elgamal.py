from pyasn1.type import univ, char, namedtype


""" ASN.1 structure description """


class _Payload(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("payload_id", univ.OctetString()),
        namedtype.NamedType("file_len", univ.Integer())
    )


class _Ciphertext(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("a_y", univ.Integer()),
        namedtype.NamedType("c", univ.Integer())
    )


class _Parameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("prime", univ.Integer()),
        namedtype.NamedType("generator", univ.Integer())
    )


class _PublicKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("a_x", univ.Integer())
    )


class _FirstKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("algorithm_id", univ.OctetString()),
        namedtype.NamedType("str_key_id", char.UTF8String()),
        namedtype.NamedType("public_key", _PublicKey()),
        namedtype.NamedType("parameters", _Parameters()),
        namedtype.NamedType("ciphertext", _Ciphertext())
    )


class _Keys(univ.Set):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("first_key", _FirstKey())
    )


class ElGamalStruct(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('keys', _Keys()),
        namedtype.NamedType('payload', _Payload()),
    )