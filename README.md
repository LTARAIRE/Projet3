# Projet 3 — Déplacement de l'hexapode (ROS2)

Paquet ROS2 qui fait marcher un robot hexapode à partir d'une commande de vitesse
(`geometry_msgs/TwistStamped`). On envoie une vitesse, le nœud génère une marche
tripode, calcule la cinématique inverse des 6 pattes et publie les 18 angles sur
`/joint_states`. Le robot se déplace dans RViz (odométrie `odom → base_link`).

## Prérequis

- ROS2 Jazzy (`/opt/ros/jazzy`)
- Pour le pilotage clavier : `sudo apt install ros-jazzy-teleop-twist-keyboard`

## Compilation

```bash
cd ~/Bureau/RobotiqueAvancee/Projet3
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Lancement (4 terminaux)

Dans chaque terminal : `source /opt/ros/jazzy/setup.bash` puis `source install/setup.bash`.

```bash
# Terminal 1 : le robot (URDF -> TF)
ros2 run robot_state_publisher robot_state_publisher \
    ~/Bureau/RobotiqueAvancee/Projet3/src/hexapode/urdf/hexapode.urdf

# Terminal 2 : affichage
rviz2 -d src/hexapode/rviz/hexapode.rviz

# Terminal 3 : le noeud (marche + cinematique + odometrie)
ros2 run hexapode hexapode_node
```

## Piloter le robot

### Au clavier (terminal 4)

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

Touches : `i` avancer, `,` reculer, `j`/`l` tourner, `J`/`L` (Maj) latéral, `k` stop,
`q`/`z` régler la vitesse. Le terminal du clavier doit avoir le focus.

### En ligne de commande (sans clavier)

```bash
ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.1}}}'
```

- `linear.x` : avancer / reculer
- `linear.y` : latéral gauche / droite
- `angular.z` : tourner

## Structure

```
src/hexapode/
├── hexapode/
│   ├── hexapode_node.py   marche tripode + cinematique inverse + odometrie
│   └── ik_patte.py        cinematique inverse / directe
├── urdf/hexapode.urdf     description du robot (18 articulations)
├── rviz/hexapode.rviz     configuration d'affichage
├── setup.py
└── package.xml
```
