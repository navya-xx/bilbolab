import numpy as np
from numpy import sin, cos
from math import pi

def main():

    def R(psi):
        return np.array([
            [cos(psi), sin(psi), 0],
            [-sin(psi), cos(psi), 0],
            [0, 0, 1]
        ])


    c3 = [0, 1, -pi / 2]
    m_3_to_1 = np.array([1, 0, pi / 2])

    c1 = np.array([0,0,0])
    psi1 = 0

    c3_est = c1  - R(-psi1+pi/2) @ m_3_to_1
    print(c3_est)

    #
    # c3 = c1 - R(psi1-pi/2)@v
    #
    # print(c1_est)

if __name__ == '__main__':
    main()