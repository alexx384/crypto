import lib


def main():
    print("===== Gelfond Shanks method =====")
    gamal = lib.ElGamal(dimension=16)
    print("generator g =", gamal.g)
    print("shared_key (g^x) =", gamal.shared_key)
    print("field p =", gamal.p)
    print("True x =", gamal.x)
    print("Computed x =", lib.gelfond(gamal.g, gamal.shared_key, gamal.p))
    print("=================================")

    print("======== Pollards method ========")
    p_x = 306
    p_y = 304
    q = 167
    q_x = 146
    q_y = 65
    p = 307
    a = 1
    d = 72

    print("True d =", d)
    print("Computed d =", lib.pollard(p, (p_x, p_y), (q_x, q_y), q, a, 100))
    print("=================================")

main()
