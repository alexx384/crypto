from pyasn1.type import univ, char, namedtype


""" ASN.1 structure description """


class _FileParameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
    )


class _Signature(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("r", univ.Integer()),
        namedtype.NamedType("s", univ.Integer())
    )


class _GroupGeneratorParameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("p_x", univ.Integer()),
        namedtype.NamedType("p_y", univ.Integer())
    )


class _CurveParameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("a", univ.Integer()),
        namedtype.NamedType("b", univ.Integer())
    )


class _FieldParameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("p", univ.Integer())
    )


class _Parameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("field", _FieldParameters()),
        namedtype.NamedType("curve", _CurveParameters()),
        namedtype.NamedType("generator", _GroupGeneratorParameters()),
        namedtype.NamedType("q", univ.Integer())
    )


class _PublicKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("q_x", univ.Integer()),
        namedtype.NamedType("q_y", univ.Integer())
    )


class _FirstKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("algorithm_id", univ.OctetString()),
        namedtype.NamedType("str_key_id", char.UTF8String()),
        namedtype.NamedType("public_key", _PublicKey()),
        namedtype.NamedType("parameters", _Parameters()),
        namedtype.NamedType("signature", _Signature())
    )


class _Keys(univ.Set):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType("first_key", _FirstKey())
    )


class Gost3410SignStruct(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('keys', _Keys()),
        namedtype.NamedType("file_parameters", _FileParameters())
    )
