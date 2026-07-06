# 📋 Commandes Utiles - Projet 3 Déplacement Hexapode

> **Référence complète** pour développer, tester et déboguer le Projet 3.
> *À garder ouvert en parallèle de ton travail.*

---

## 🔧 Configuration de base

### Activer ROS2 dans un terminal
**À faire dans CHAQUE nouveau terminal** :
```bash
source /opt/ros/jazzy/setup.bash
source ~/Bureau/RobotiqueAvancee/Projet3/install/setup.bash
```

**Vérification** :
```bash
 echo $ROS_DISTRO           # → doit afficher : jazzy
ros2 pkg list | head       # → doit lister des paquets ROS2
```

---

## 🏗️ Gestion du projet

### Compiler le workspace
**Depuis la racine du projet** (`~/Bureau/RobotiqueAvancee/Projet3/`) :
```bash
colcon build --symlink-install
```

### Vérifier la compilation
```bash
colcon build --symlink-install 2>&1 | grep -i error
# → Si vide = compilation OK
```

---

## 🚀 Lancer les nœuds

### Lancer le nœud principal (hexapode)
```bash
ros2 run hexapode hexapode_node
```

### Lancer la téléopération clavier
```bash
ros2 run hexapode teleop_clavier
```

### Lancer l'IK d'une patte (test)
```bash
ros2 run hexapode ik_patte --x 0.15 --y 0.05 --z -0.08
```

---

## 🎯 Lancer avec des fichiers launch

### Affichage RViz + robot_state_publisher + curseurs
```bash
ros2 launch hexapode etape1_affichage.launch.py
```

### Tester l'IK avec un launch
```bash
ros2 launch hexapode etape4_ik.launch.py x:=0.15 y:=0.05 z:=-0.08
```

---

## 📡 Manipuler les topics manuellement

### Publier une vitesse sur /cmd_vel
```bash
# Avancer à 0.05 m/s
ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.05, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}}'

# Avancer + tourner
ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.05}, angular: {z: 0.1}}}'

# Décalage latéral (strafe)
ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {y: 0.03}}}'

# STOP
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.0, y: 0.0}, angular: {z: 0.0}}}'
```

### Écouter un topic
```bash
# Voir les commandes de vitesse reçues
ros2 topic echo /cmd_vel

# Voir les angles des articulations
ros2 topic echo /joint_states

# Voir les TF (transformations)
ros2 topic echo /tf_static
```

---

## 🔍 Débogage et inspection

### Lister les nœuds actifs
```bash
ros2 node list
```

### Lister les topics actifs
```bash
ros2 topic list
```

### Voir qui publie/écoute un topic
```bash
ros2 topic info /cmd_vel
ros2 topic info /joint_states
```

### Voir les infos d'un nœud
```bash
ros2 node info /hexapode_node
```

### Graphique ROS2 (nœuds + topics)
```bash
rqt_graph
```

---

## 🎮 Commandes de téléopération clavier

| Touche | Action | Commande ROS équivalente |
|--------|--------|--------------------------|
| **Z** | Avancer | `twist.linear.x = +0.1` |
| **S** | Reculer | `twist.linear.x = -0.1` |
| **Q** | Gauche | `twist.linear.y = +0.1` |
| **D** | Droite | `twist.linear.y = -0.1` |
| **A** | Rotation gauche | `twist.angular.z = +0.5` |
| **E** | Rotation droite | `twist.angular.z = -0.5` |
| **Espace** | STOP | Tous les champs à 0 |
| **Ctrl+C** | Quitter | Arrête le nœud |

---

## 📊 Vérifications utiles

### Vérifier que le nœud hexapode_node reçoit bien /cmd_vel
```bash
# Terminal 1 : lance le nœud
ros2 run hexapode hexapode_node

# Terminal 2 : envoie une commande
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.05}}}'

# → Dans Terminal 1, tu dois voir :
# [INFO] [hexapode_node]: Vitesse : lin.x=0.050, lin.y=0.000, ang.z=0.000
```

### Vérifier que teleop_clavier publie sur /cmd_vel
```bash
# Terminal 1 : lance teleop_clavier
ros2 run hexapode teleop_clavier

# Terminal 2 : écoute /cmd_vel
ros2 topic echo /cmd_vel

# → Appuie sur Z, Q, etc. dans Terminal 1
# → Dans Terminal 2, tu dois voir les messages TwistStamped
```

---

## 🧪 Tests des étapes

### Étape 6 : Reception de vitesse
```bash
ros2 run hexapode hexapode_node &
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/TwistStamped \
  '{twist: {linear: {x: 0.05, y: 0.02}, angular: {z: 0.1}}}'
# ✅ Validé si le nœud loggue la vitesse reçue
```

### Étape 3+5 : Pose de repos
```bash
ros2 launch hexapode etape1_affichage.launch.py &
ros2 run hexapode hexapode_node
# ✅ Validé si le robot tient debout dans RViz (sans les curseurs)
```

### Étape 4 : IK d'une patte
```bash
ros2 run hexapode ik_patte --x 0.15 --y 0.05 --z -0.08
# ✅ Validé si :
# - Angles affichés
# - Erreur FK ≈ 0.000000 m
# - Fenêtre matplotlib avec la patte et la cible
```

---

## 📁 Structure du projet

```
Projet3/
├── src/
│   └── hexapode/
│       ├── hexapode/
│       │   ├── __init__.py
│       │   ├── hexapode_node.py    # Nœud principal (déplacement)
│       │   ├── ik_patte.py         # Cinématique inverse
│       │   └── teleop_clavier.py   # Téléopération clavier
│       ├── launch/
│       │   ├── etape1_affichage.launch.py
│       │   └── etape4_ik.launch.py
│       ├── urdf/
│       │   └── hexapode.urdf
│       ├── rviz/
│       │   └── etape1.rviz
│       ├── package.xml
│       └── setup.py
├── build/
├── install/
└── log/
```

---

## 🔄 Workflow typique

### 1. Développer
- Modifie tes fichiers `.py` dans `src/hexapode/hexapode/`

### 2. Compiler
```bash
cd ~/Bureau/RobotiqueAvancee/Projet3
colcon build --symlink-install
```

### 3. Tester
```bash
source install/setup.bash
ros2 run hexapode hexapode_node
```

### 4. Déboguer
- Utilise `ros2 topic echo` pour vérifier les messages
- Utilise `ros2 node info` pour vérifier les connections
- Utilise `rqt_graph` pour visualiser le graphique ROS

---

## ⚠️ Résolution des problèmes courants

### Problème : Commande non trouvée (`ros2: command not found`)
**Solution** :
```bash
source /opt/ros/jazzy/setup.bash
```

### Problème : Nœud non trouvé (`Package not found`)
**Solution** :
```bash
colcon build --symlink-install
source install/setup.bash
```

### Problème : Modifications non prises en compte
**Solution** :
- Vérifie que tu as bien compilé (`colcon build`)
- Vérifie que tu as sourcé `install/setup.bash`
- Avec `--symlink-install`, les fichiers Python sont liés directement (pas besoin de recompiler pour chaque petit changement)

### Problème : RViz ne s'affiche pas
**Solution** :
```bash
# Vérifie que robot_state_publisher est lancé
ros2 node list
# Doit contenir : /robot_state_publisher

# Vérifie le Fixed Frame dans RViz
# Doit être : base_link ou odom
```

---

## 📚 Ressources

- **Sujet du projet** : `sujets_projets.pdf`
- **Étapes détaillées** : `ETAPES_PROJET3.md`
- **Journal d'avancement** : `JOURNAL_AVANCEMENT.md`
- **Documentation ROS2** : https://docs.ros.org/en/jazzy/
