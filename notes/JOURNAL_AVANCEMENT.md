# Journal d'avancement — Projet 3 (déplacement hexapode)

> Récapitulatif **détaillé et expliqué** de tout ce qui a été fait, dans l'ordre.
> Sert de mémoire : tu peux le relire pour comprendre *pourquoi* chaque chose existe.

---

## Vue d'ensemble du projet

**But (sujet)** : un paquet ROS qui commande l'hexapode via un message
`geometry_msgs/TwistStamped` (une vitesse). À terme : on envoie une vitesse, le
robot marche dans la bonne direction dans RViz.

**Architecture cible (minimale)** :
```
   clavier ─► teleop_clavier (plus tard)
                 │ publie
                 ▼
        /cmd_vel  (geometry_msgs/TwistStamped)
                 │ écoute
                 ▼
        hexapode (nœud principal = le cœur)
          - reçoit la vitesse
          - génère la marche
          - calcule l'IK des pattes
                 │ publie
                 ▼
        /joint_states  (sensor_msgs/JointState)
                 │
                 ▼
   robot_state_publisher ─► TF ─► RViz
```

---

## Vocabulaire ROS2 (les mots à connaître)

| Mot | Définition simple |
|---|---|
| **Workspace** | dossier de travail. Contient `src/` (ton code) + `build/`, `install/`, `log/` (générés). |
| **Paquet (package)** | une brique du projet, créée dans `src/`. |
| **Nœud (node)** | un petit programme qui tourne. |
| **Topic** | un canal nommé où circulent des messages entre nœuds. |
| **Message** | une donnée structurée (ex. une vitesse, une liste d'angles). |
| **Publier / S'abonner** | envoyer / écouter des messages sur un topic. |
| **URDF** | fichier XML qui décrit le robot (pièces + articulations). |
| **TF** | système qui suit la position 3D de chaque repère du robot. |
| **FK / IK** | cinématique directe (angles→position) / inverse (position→angles). |

---

## ÉTAPE 0 — Environnement ROS2 (FAIT ✅)

ROS2 **Jazzy** est installé dans `/opt/ros/jazzy`.

⚠️ ROS2 n'est **pas actif par défaut** dans un terminal. Au début de **chaque
terminal**, il faut taper :
```bash
source /opt/ros/jazzy/setup.bash
```
Vérification : `echo $ROS_DISTRO` doit afficher `jazzy`.

**Pourquoi ?** Cette commande « branche » ROS2 dans le shell : elle rend la
commande `ros2` disponible et indique où trouver les paquets ROS.

---

## ÉTAPE 1 — Workspace + paquet (FAIT ✅)

Structure créée :
```
Projet3/
├── src/
│   └── hexapode/                 ← le paquet ROS2 (type ament_python)
│       ├── hexapode/             ← dossier des futurs nœuds (.py)
│       │   └── __init__.py
│       ├── urdf/
│       │   └── hexapode.urdf     ← description du robot (18 joints revolute)
│       ├── package.xml           ← nom + dépendances du paquet
│       ├── setup.py              ← déclare quoi installer + (futurs) nœuds
│       └── setup.cfg
├── build/   (généré par colcon)
├── install/ (généré par colcon)  ← LA COPIE utilisée à l'exécution
└── log/     (généré par colcon)
```

**Dépendances déclarées** dans `package.xml` : `rclpy`, `geometry_msgs`,
`sensor_msgs`.

**Compiler / activer** (à la racine `Projet3/`) :
```bash
colcon build --symlink-install
source install/setup.bash
```

**Le mécanisme clé à comprendre** :
```
   src/hexapode/   ──[ colcon build ]──►   install/hexapode/share/hexapode/
   (ce que tu édites)                       (la copie "officielle" utilisée à l'exécution)
```
`ros2 run` et `ros2 launch` utilisent la copie dans `install/`, **pas** tes
fichiers source directement. D'où la règle : **on modifie → on `colcon build` →
ensuite seulement c'est pris en compte**.

---

## ÉTAPE 1-bis — Corriger l'emplacement de l'URDF + setup.py (FAIT ✅)

**Problème rencontré** : l'URDF était d'abord en dehors du paquet (`src/urdf/`),
donc jamais copié dans `install/` → introuvable à l'exécution.

**Corrections faites** :
1. Déplacé l'URDF **dans** le paquet : `src/hexapode/urdf/hexapode.urdf`.
2. Dans `setup.py`, ajouté en haut :
   ```python
   import os
   from glob import glob
   ```
   et dans `data_files` (chaque ligne = « copie CES fichiers VERS CE dossier ») :
   ```python
   (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
   (os.path.join('share', package_name, 'launch'), glob('launch/*')),
   ```
3. Recompilé. **Vérification** : l'URDF apparaît bien dans
   `install/hexapode/share/hexapode/urdf/`. ✅

**Leçon** : tout fichier nécessaire à l'exécution (URDF, launch, meshes, config
RViz) doit vivre **dans** le paquet **et** être déclaré dans `setup.py`.

---

## ÉTAPE 2 — Afficher le robot dans RViz (FAIT ✅ — en manuel)

On a choisi la méthode **manuelle, 3 terminaux** (le fichier launch sera fait
plus tard). Dans chaque terminal : `source /opt/ros/jazzy/setup.bash` d'abord.

**Terminal 1 — robot_state_publisher** :
```bash
ros2 run robot_state_publisher robot_state_publisher \
    ~/Bureau/RobotiqueAvancee/Projet3/src/hexapode/urdf/hexapode.urdf
```
> ⚠️ On donne le **chemin du fichier** en argument. Surtout PAS
> `-p robot_description:=<tout le XML>` : la ligne de commande ne sait pas avaler
> un gros texte multi-lignes → ça plante. (Le nœud affiche un warning
> "backwards compatibility" : c'est normal, ça marche.)

**Terminal 2 — joint_state_publisher_gui** (les curseurs) :
```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

**Terminal 3 — RViz** :
```bash
rviz2
```

**Réglages dans RViz** :
1. Global Options → **Fixed Frame** = `base_link`.
2. **Add** → **RobotModel**.
3. RobotModel → **Description Topic** = `/robot_description`.

**Résultat** : l'hexapode (corps + 6 pattes) s'affiche, et les curseurs bougent
les pattes. ✅

---

## Comprendre ce qui se passe (questions/réponses)

**D'où sortent les curseurs ?**
`joint_state_publisher_gui` lit l'URDF (via `/robot_description`), repère toutes
les articulations mobiles (les 18 `revolute`) et crée **un curseur par
articulation**, automatiquement.

**Quelle unité ont les curseurs ?**
Des **radians** (joints `revolute` = rotation). Les bornes viennent des `<limit>`
de l'URDF :
| Articulation | Limites | En degrés |
|---|---|---|
| `*_coxa_joint`  | −0,785 → +0,785 rad | ≈ ±45° |
| `*_femur_joint` | −1,000 → +1,000 rad | ≈ ±57° |
| `*_tibia_joint` | −1,500 → +1,500 rad | ≈ ±86° |
(Rappel : 1 rad ≈ 57,3° ; π rad = 180°.)

**`/joint_states` est-il natif à ROS ?**
Oui. `sensor_msgs/JointState` est un **type de message standard** ROS2, et
`/joint_states` le **nom de topic conventionnel** pour l'état des articulations
(noms + angles). On réutilise ce standard.

**À quoi sert `robot_state_publisher` ?**
Il lit l'URDF + écoute `/joint_states`, calcule la **position 3D de chaque pièce**
(cinématique directe / FK) et publie ça en **TF**. RViz lit les TF pour dessiner.
Le flux complet :
```
curseurs ─► /joint_states ─► robot_state_publisher ─► TF ─► RViz
```

---

## Les 18 articulations du robot (à réutiliser partout)

Convention de nommage : `leg_<N>_<segment>_joint`, avec N de 1 à 6 et segment ∈
{coxa, femur, tibia}. Donc :
```
leg_1_coxa_joint, leg_1_femur_joint, leg_1_tibia_joint,
leg_2_coxa_joint, leg_2_femur_joint, leg_2_tibia_joint,
... jusqu'à leg_6_*
```
Tous de type `revolute`. **Tu réutiliseras ces noms exacts** quand TON nœud
publiera sur `/joint_states`.

---

## ÉTAPE 2-bis — Launch d'affichage + config RViz (FAIT ✅)

Pour ne plus lancer 3 terminaux à la main, on a créé **un launch** qui démarre
tout d'un coup, avec une **config RViz pré-réglée** (le robot s'affiche
directement, sans rien régler — idéal pour une démo).

**Fichiers créés** :
- `launch/etape1_affichage.launch.py` : lit l'URDF, le passe en **paramètre** à
  `robot_state_publisher`, puis lance `joint_state_publisher_gui` et `rviz2`.
- `rviz/etape1.rviz` : réglages RViz sauvegardés (Fixed Frame = `base_link`,
  RobotModel sur `/robot_description`, vue orbitale).
- `setup.py` : ajout de `glob('rviz/*')` dans `data_files` pour installer la config.

**Lancer** :
```bash
ros2 launch hexapode etape1_affichage.launch.py
```

**Pourquoi le launch sait passer l'URDF alors que la ligne de commande échouait ?**
Le launch **lit le fichier** (`open(...).read()`) et met son contenu dans le
paramètre `robot_description`. En ligne de commande, on essayait de coller tout le
XML comme argument `-p`, ce que le parseur ne sait pas faire (texte trop gros,
multi-lignes). Le launch fait le branchement proprement.

---

## ÉTAPE 4 — Cinématique inverse d'UNE patte (FAIT ✅)

**But** : « je veux le pied en (x, y, z) → quels sont les 3 angles ? »

### Le modèle géométrique (lu dans l'URDF)
| Segment | Longueur | Axe de rotation |
|---|---|---|
| coxa (L1) | 0,052 m | Z (vertical) |
| fémur (L2) | 0,065 m | Y (horizontal) |
| tibia (L3) | 0,133 m | Y (horizontal) |

Comme les axes sont « droits », l'IK est **analytique** (formules directes, pas de
méthode numérique).

### L'algorithme (fichier `hexapode/ik_patte.py`)
1. **coxa** : `q1 = atan2(y, x)` → orientation horizontale vers la cible.
2. **plan de la patte** : `rho = sqrt(x²+y²) − L1` (portée horizontale),
   `h = −z` (profondeur).
3. **triangle fémur-tibia (Al-Kashi)** :
   - `q3 = arccos((rho²+h² − L2² − L3²) / (2·L2·L3))` → angle du genou ;
   - `q2 = atan2(h, rho) − atan2(L3·sin(q3), L2 + L3·cos(q3))` → angle du fémur.
4. `np.clip(...)` sur le cosinus → sécurité si la cible est hors de portée.

### Vérification (très important pour le prof)
- **FK de contrôle** `cinematique_directe(q1,q2,q3)` : on recalcule la position du
  pied à partir des angles. Le **round-trip IK→FK** donne une **erreur de 0,000000 m**.
- **Limites** : on compare les 3 angles aux `<limit>` de l'URDF et on affiche un
  avertissement si on dépasse (ex. cible trop repliée → tibia > 1,5 rad).
- **Tracé matplotlib** : la patte vue de côté, le pied tombe pile sur la cible.

### Convention de signe (point subtil mais essentiel)
Notre FK utilise `z = −(L2·sin(q2) + L3·sin(q2+q3))` (signe **−**), alors que le
TP05 utilisait un `+`. Raison : dans l'URDF, l'axe du fémur est `+Y`, donc un `q2`
**positif baisse** la patte (z négatif). Le signe `−` rend notre modèle Python
**cohérent avec l'URDF** (sinon les pattes plieraient à l'envers dans RViz).

### Style de code
Aligné sur les TP : `import numpy as np`, fonctions `cinematique_directe` /
`cinematique_inverse`, angles `q1/q2/q3`, `print` en f-strings, bloc `__main__`.

---

## ÉTAPE 4-bis — Rendre l'IK paramétrable + launch (FAIT ✅)

Pour choisir la cible **au lancement** (et pas en dur dans le code) :
- **`argparse`** dans `main()` : le script lit `--x --y --z` (avec valeurs par défaut).
- **`entry_points`** dans `setup.py` (`ik_patte = hexapode.ik_patte:main`) : le
  script devient un exécutable lançable par `ros2 run`.
- **`launch/etape4_ik.launch.py`** : déclare les arguments `x/y/z`
  (`DeclareLaunchArgument`) et les transmet au programme (`LaunchConfiguration`).

**Lancer** :
```bash
ros2 run   hexapode ik_patte --x 0.15 --y 0.05 --z -0.08
ros2 launch hexapode etape4_ik.launch.py x:=0.15 y:=0.05 z:=-0.08
```

**Piège corrigé** : un launch ajoute `--ros-args` à un `Node`. Notre script n'est
pas un vrai nœud ROS → on a utilisé `parser.parse_known_args()` (ignore les
arguments inconnus) au lieu de `parse_args()`.

---

## Questions anticipées du prof (et réponses)

**Q1 — Pourquoi une IK analytique et pas numérique (Jacobien, optimisation) ?**
Parce que la patte a des axes « droits » (coxa sur Z, fémur/tibia sur Y) : la
géométrie se ramène à un triangle résolu par la loi des cosinus. C'est **exact,
instantané et sans risque de non-convergence**. Le numérique ne serait utile que si
la géométrie était « tordue ».

**Q2 — Comment avez-vous validé votre IK ?**
Par un **round-trip IK→FK** : on calcule les angles depuis une cible, puis on
recalcule la position avec la FK ; l'erreur est de l'ordre de 1e-6 m (0 en pratique).
On vérifie aussi que les angles **respectent les limites** de l'URDF, et on a un
**tracé** de contrôle.

**Q3 — Il y a deux solutions à l'IK (genou en haut / en bas). Laquelle ?**
La loi des cosinus donne `q3 = ±arccos(...)`. On prend la branche qui garde les
angles **dans les limites** physiques et oriente le genou de façon cohérente
(coude « vers le bas »). On pourrait choisir l'autre signe pour une autre posture.

**Q4 — Que se passe-t-il si la cible est hors de portée ?**
Le cosinus dépasserait ±1 → `arccos` renverrait NaN. On a mis un `np.clip` qui
borne le cosinus à [−1, 1] : la patte « tend » au maximum au lieu de planter. Le
contrôle des limites alerte aussi l'utilisateur.

**Q5 — Pourquoi votre FK diffère du robot_state_publisher ?**
`robot_state_publisher` fait **lui-même** la FK (à partir de l'URDF) pour
**afficher** le robot dans RViz. Notre FK Python sert seulement à **vérifier notre
IK** dans un script séparé. Ce sont deux usages différents.

**Q6 — Pourquoi le signe « − » dans z ? / Dans quel repère travaillez-vous ?**
On travaille dans le **repère de la coxa** (avant rotation). Le signe `−` vient de
l'axe `+Y` du fémur dans l'URDF : `q2 > 0` fait descendre la patte. C'est ce qui
garantit que nos angles correspondent à ce que RViz affichera.

**Q7 — Pourquoi un seul nœud et pas des services/actions ROS ?**
Le sujet impose une commande par `geometry_msgs/TwistStamped` (un flux continu de
vitesse). Un publisher/subscriber sur des topics suffit et reste simple. On a
volontairement écarté services/actions pour ne pas sur-complexifier (architecture
adaptée au besoin).

**Q8 — Pourquoi réutiliser l'URDF du groupe 1 ?**
Le projet 3 porte sur le **déplacement**, pas la modélisation. Réutiliser l'URDF
PhantomX (axes droits, dimensions connues) nous laisse concentrer l'effort sur la
cinématique et la marche, et garantit la cohérence entre équipes.

---

## Prochaine étape

**ÉTAPE 3+5 — Le nœud ROS qui anime les 6 pattes** : un vrai nœud `rclpy` qui, en
utilisant `cinematique_inverse`, calcule les 18 angles d'une posture de repos et
les publie en continu sur `/joint_states` → le robot tient debout dans RViz **sans
les curseurs**.

---

## Aide-mémoire commandes

| Pour… | Commande |
|---|---|
| Activer ROS2 | `source /opt/ros/jazzy/setup.bash` |
| Compiler | `colcon build --symlink-install` (à la racine `Projet3/`) |
| Activer le projet | `source install/setup.bash` |
| Afficher le robot (launch) | `ros2 launch hexapode etape1_affichage.launch.py` |
| Tester l'IK (run) | `ros2 run hexapode ik_patte --x 0.15 --y 0.05 --z -0.08` |
| Tester l'IK (launch) | `ros2 launch hexapode etape4_ik.launch.py x:=0.15 y:=0.05 z:=-0.08` |
| Lister topics | `ros2 topic list` |
| Écouter un topic | `ros2 topic echo /joint_states` |
| Qui publie/écoute | `ros2 topic info /joint_states` |
</content>
