import numpy as np

L1 = 0.052
L2 = 0.065
L3 = 0.133

LIM_COXA = 0.785
LIM_FEMUR = 1.000
LIM_TIBIA = 1.500


def cinematique_inverse(x, y, z):
    q1 = np.arctan2(y, x)

    r = np.sqrt(x**2 + y**2)
    rho = r - L1
    h = -z

    D2 = rho**2 + h**2
    cos_q3 = (D2 - L2**2 - L3**2) / (2 * L2 * L3)
    cos_q3 = np.clip(cos_q3, -1.0, 1.0)
    q3 = np.arccos(cos_q3)

    q2 = np.arctan2(h, rho) - np.arctan2(L3 * np.sin(q3), L2 + L3 * np.cos(q3))

    return q1, q2, q3


def cinematique_directe(q1, q2, q3):
    rho = L1 + L2 * np.cos(q2) + L3 * np.cos(q2 + q3)
    z = -(L2 * np.sin(q2) + L3 * np.sin(q2 + q3))

    x = rho * np.cos(q1)
    y = rho * np.sin(q1)
    return x, y, z


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=float, default=0.20)
    parser.add_argument('--y', type=float, default=0.0)
    parser.add_argument('--z', type=float, default=-0.06)
    args, _ = parser.parse_known_args()
    cible = (args.x, args.y, args.z)

    q1, q2, q3 = cinematique_inverse(*cible)
    print(f"Angles trouves (rad) : coxa={q1:.3f}  femur={q2:.3f}  tibia={q3:.3f}")

    if abs(q1) > LIM_COXA or abs(q2) > LIM_FEMUR or abs(q3) > LIM_TIBIA:
        print("ATTENTION : un angle depasse les limites de l'URDF !")
    else:
        print("Angles dans les limites : OK")

    pied = cinematique_directe(q1, q2, q3)
    print(f"Cible demandee  : {np.round(cible, 4)}")
    print(f"Pied recalcule  : {np.round(pied, 4)}")
    erreur = np.sqrt(sum((np.array(pied) - np.array(cible))**2))
    print(f"Erreur (m)      : {erreur:.6f}")

    import matplotlib.pyplot as plt

    rho_femur = L1
    rho_genou = L1 + L2 * np.cos(q2)
    z_genou = -L2 * np.sin(q2)
    rho_pied = L1 + L2 * np.cos(q2) + L3 * np.cos(q2 + q3)
    z_pied = -(L2 * np.sin(q2) + L3 * np.sin(q2 + q3))

    rhos = [0, rho_femur, rho_genou, rho_pied]
    zs = [0, 0, z_genou, z_pied]

    plt.figure(figsize=(6, 6))
    plt.plot(rhos, zs, 'b-o')
    plt.scatter([np.sqrt(cible[0]**2 + cible[1]**2)], [cible[2]],
                color='red', zorder=5, label='cible')
    plt.xlabel('rho (horizontal, m)')
    plt.ylabel('z (vertical, m)')
    plt.title('Patte vue de cote')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
