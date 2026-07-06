import rclpy
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped, TransformStamped
from tf2_ros import TransformBroadcaster
from hexapode.ik_patte import cinematique_inverse
import numpy as np

X0 = 0.22
Z0 = -0.06
AMP_MAX = 0.02
GAIN = 0.30
LEVEE = 0.02
CADENCE = 1.0
FREQ = 30.0

LIM_COXA = 0.785
LIM_FEMUR = 1.000
LIM_TIBIA = 1.500

ANGLES_MONTAGE = [0.785, 1.570, 2.356, -0.785, -1.570, -2.356]
POS_MONTAGE = [(0.120, 0.060), (0.000, 0.100), (-0.120, 0.060),
               (0.120, -0.060), (0.000, -0.100), (-0.120, -0.060)]

vx = 0.0
vy = 0.0
w = 0.0
phase = 0.0

odom_x = 0.0
odom_y = 0.0
theta = 0.0

node = None
pub = None
br = None
noms = []


def recevoir_vitesse(msg):
    global vx, vy, w
    vx = msg.twist.linear.x
    vy = msg.twist.linear.y
    w = msg.twist.angular.z


def position_pied(i):
    rx, ry = POS_MONTAGE[i]
    vfx = -vx + w * ry
    vfy = -vy - w * rx
    module = np.sqrt(vfx**2 + vfy**2)

    if module < 1e-4:
        return X0, 0.0, Z0

    amp = min(AMP_MAX, GAIN * module)

    dx = vfx / module
    dy = vfy / module

    p = phase
    if i % 2 == 1:
        p = (p + 0.5) % 1.0

    if p < 0.5:
        s = p / 0.5
        along = -amp + 2 * amp * s
        dz = 0.0
    else:
        s = (p - 0.5) / 0.5
        along = amp - 2 * amp * s
        dz = LEVEE * np.sin(np.pi * s)

    offx = along * dx
    offy = along * dy

    a = ANGLES_MONTAGE[i]
    off_leg_x = np.cos(a) * offx + np.sin(a) * offy
    off_leg_y = -np.sin(a) * offx + np.cos(a) * offy

    x = X0 + off_leg_x
    y = 0.0 + off_leg_y
    z = Z0 + dz
    return x, y, z


def boucle():
    global phase, odom_x, odom_y, theta

    bouge = abs(vx) > 1e-3 or abs(vy) > 1e-3 or abs(w) > 1e-3

    if bouge:
        phase = (phase + CADENCE / FREQ) % 1.0
    else:
        phase = 0.0

    mv = np.sqrt(vx**2 + vy**2)
    if mv > 1e-3:
        amp = min(AMP_MAX, GAIN * mv)
        vitesse = 2 * amp * CADENCE
        vbx = vitesse * vx / mv
        vby = vitesse * vy / mv
    else:
        vbx = 0.0
        vby = 0.0

    odom_x += (vbx * np.cos(theta) - vby * np.sin(theta)) / FREQ
    odom_y += (vbx * np.sin(theta) + vby * np.cos(theta)) / FREQ
    theta += w / FREQ

    angles = []
    for i in range(6):
        x, y, z = position_pied(i)
        q1, q2, q3 = cinematique_inverse(x, y, z)
        q1 = float(np.clip(q1, -LIM_COXA, LIM_COXA))
        q2 = float(np.clip(q2, -LIM_FEMUR, LIM_FEMUR))
        q3 = float(np.clip(q3, -LIM_TIBIA, LIM_TIBIA))
        angles += [q1, q2, q3]

    stamp = node.get_clock().now().to_msg()

    msg = JointState()
    msg.header.stamp = stamp
    msg.name = noms
    msg.position = angles
    pub.publish(msg)

    t = TransformStamped()
    t.header.stamp = stamp
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_link'
    t.transform.translation.x = float(odom_x)
    t.transform.translation.y = float(odom_y)
    t.transform.translation.z = 0.0
    t.transform.rotation.z = float(np.sin(theta / 2.0))
    t.transform.rotation.w = float(np.cos(theta / 2.0))
    br.sendTransform(t)


def main():
    global node, pub, br, noms

    rclpy.init()
    node = rclpy.create_node('hexapode_node')

    pub = node.create_publisher(JointState, '/joint_states', 10)
    node.create_subscription(TwistStamped, '/cmd_vel', recevoir_vitesse, 10)
    br = TransformBroadcaster(node)

    for n in range(1, 7):
        for seg in ['coxa', 'femur', 'tibia']:
            noms.append(f'leg_{n}_{seg}_joint')

    node.create_timer(1 / FREQ, boucle)

    node.get_logger().info("Noeud hexapode demarre : en attente de /cmd_vel")
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
