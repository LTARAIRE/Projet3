# Projet 3 — Déplacement de l'hexapode : parcours pas à pas

> **But du projet** (sujet) : développer un paquet ROS qui commande l'hexapode
> via un message `geometry_msgs/TwistStamped`.
> **Règle du jeu** : tu écris le code **toi-même**. Ce document te donne les
> commandes, les noms (topics/messages), les algorithmes **en mots**, et un
> point de validation (✅) à chaque étape. Pas de code de nœud tout fait.

## Contexte de ta machine (déjà vérifié)

- ROS2 **Jazzy** est installé (`/opt/ros/jazzy`) — `rclpy`, `colcon`,
  `robot_state_publisher`, `joint_state_publisher_gui`, `rviz2`, `xacro` : OK.
- URDF du **groupe 1** disponible = **PhantomX** (`phantomx_description`, meshes STL).
- ⚠️ Le dossier `../Projet3_Deplacement/` est une tentative **trop complexe**
  (actions, services, interfaces custom). **Ne rien y copier.** On part propre et simple.

## Architecture cible (volontairement minimale)

```
   clavier ─► teleop_clavier (nœud 2, optionnel, tout à la fin)
                     │ publie
                     ▼
            /cmd_vel  (geometry_msgs/TwistStamped)
                     │ écoute
                     ▼
            hexapode (nœud 1 = le cœur)
              - reçoit la vitesse
              - génère la marche (gait)
              - calcule l'IK des pattes
                     │ publie
                     ▼
            /joint_states  (sensor_msgs/JointState)
                     │
                     ▼
   robot_state_publisher ─► TF ─► RViz (affichage)
```

Un **seul paquet** `mon_hexapode` (type `ament_python`), avec à terme :
- nœud `hexapode` (le moteur), nœud `teleop_clavier` (pilotage clavier, à la fin),
- un dossier `launch/`, et on réutilise l'URDF PhantomX.

---

## ⬜ Étape 0 — Activer ROS2 dans le terminal

**À refaire dans CHAQUE nouveau terminal :**

```bash
source /opt/ros/jazzy/setup.bash
```

Vérifier :
```bash
echo $ROS_DISTRO     # doit afficher : jazzy
ros2 pkg list | head # doit lister des paquets
```

✅ **Validé quand :** `echo $ROS_DISTRO` affiche `jazzy`.

> 💡 Pour ne pas le retaper : tu peux ajouter la ligne `source` à la fin de
> `~/.bashrc`. (Optionnel.)

---

## ⬜ Étape 1 — Créer le workspace et le paquet

Un *workspace* = ton dossier de travail. Un *paquet* = une brique dedans.

```bash
# 1. créer le workspace avec un sous-dossier src/
mkdir -p ~/ros2_hexapode/src
cd ~/ros2_hexapode/src

# 2. créer le paquet Python
ros2 pkg create --build-type ament_python mon_hexapode \
    --dependencies rclpy geometry_msgs sensor_msgs

# 3. compiler (À LA RACINE du workspace, pas dans src/)
cd ~/ros2_hexapode
colcon build --symlink-install

# 4. "activer" ton projet (à refaire dans chaque terminal, APRÈS le source de jazzy)
source install/setup.bash
```

> `--symlink-install` : pratique en Python, tu modifies tes fichiers sans
> recompiler à chaque fois.

**Structure obtenue** (regarde-la pour comprendre) :
```
ros2_hexapode/
├── src/
│   └── mon_hexapode/
│       ├── mon_hexapode/        ← tes fichiers .py de nœuds vont ICI
│       ├── package.xml          ← dépendances + infos du paquet
│       ├── setup.py             ← déclare tes nœuds (entry_points) ICI
│       ├── setup.cfg
│       └── test/
├── build/   (généré)
├── install/ (généré)
└── log/     (généré)
```

✅ **Validé quand :** `colcon build` réussit sans erreur.

---

## ⬜ Étape 2 — Voir le robot (URDF PhantomX) dans RViz

But : afficher l'hexapode et bouger ses pattes avec des curseurs.

À faire :
1. **Récupérer** l'URDF du groupe 1 (`phantomx_description`) dans ton workspace
   (copie le dossier dans `src/`, puis recompile). Les meshes STL doivent suivre.
2. **Inspecter** l'URDF : note les **noms des 18 articulations** (tu en auras besoin
   pour `/joint_states`) et regarde si les axes sont « droits » ou « tordus ».
   - commande utile : `ros2 topic echo /joint_states` une fois l'affichage lancé,
   - ou ouvre le fichier `.urdf` et cherche les balises `<joint name=...>`.
3. **Afficher** : lance ensemble `robot_state_publisher`, `joint_state_publisher_gui`
   (les curseurs) et `rviz2`. Mets le **Fixed Frame** sur `base_link` dans RViz et
   ajoute l'affichage **RobotModel**.

> Tu peux d'abord les lancer à la main dans 3 terminaux pour comprendre, puis
> écrire **un fichier launch** qui fait les 3 d'un coup (voir Étape 7-bis launch).

✅ **Validé quand :** tu vois le PhantomX dans RViz et les curseurs bougent les pattes.

> 📝 **Livrable de cette étape : la liste des 18 noms d'articulations.** Recopie-la,
> tu t'en serviras à toutes les étapes suivantes.

---

## ⬜ Étape 3 — Ton premier nœud qui anime le robot

But : remplacer les curseurs par **ton** programme.

Le robot s'anime via le topic **`/joint_states`** (type `sensor_msgs/JointState`) :
il contient la **liste des noms** d'articulations + leurs **angles** (radians).

Squelette d'un nœud (toujours le même, à écrire toi-même) :
- une **classe** qui hérite de `Node` ;
- un **publisher** sur `/joint_states` ;
- un **timer** (~30 Hz) dont la fonction construit le message et le publie ;
- dans `main` : initialiser ROS, créer le nœud, le faire tourner (`spin`), fermer.

⚠️ Pense à **déclarer ton nœud dans `setup.py`** (section `entry_points`/`console_scripts`),
sinon `ros2 run` ne le trouvera pas. Puis `colcon build` + `source install/setup.bash`.

Pour commencer simple : publie des angles **fixes** (tous à 0), puis des angles qui
**varient avec un sinus** pour voir les pattes bouger.

Commandes :
```bash
ros2 run mon_hexapode <nom_du_noeud>
ros2 topic echo /joint_states
```

> ⚠️ Quand TON nœud publie `/joint_states`, **n'utilise plus** `joint_state_publisher_gui`
> en même temps (ils se battraient pour le même topic).

✅ **Validé quand :** ton nœud fait bouger les pattes dans RViz.

---

## ⬜ Étape 4 — La cinématique inverse (IK) d'UNE patte

But : « je veux le bout de la patte en (x, y, z) → quels sont les 3 angles ? »

Longueurs : L1 = coxa, L2 = fémur, L3 = tibia.

Algorithme **en mots** :
1. **coxa** = angle horizontal vers la cible → `atan2(y, x)`.
2. se ramener dans le **plan de la patte** : distance horizontale du pied (en
   retirant la longueur de coxa) + hauteur z → un triangle de côtés connus
   (L2, L3, distance pied↔épaule).
3. **fémur** et **tibia** : appliquer le **théorème d'Al-Kashi** (loi des cosinus)
   sur ce triangle.

Conseils :
- Travaille d'abord dans un **petit script Python séparé, SANS ROS**.
- Écris aussi la **FK** (angles → position) pour **vérifier** (tu dois retomber sur la cible).
- **Borne** les angles aux limites physiques (le genou ne plie pas à 360°).

✅ **Validé quand :** une position en entrée → 3 angles, et la FK confirme la position.

---

## ⬜ Étape 5 — Faire tenir le robot debout (pose de repos)

But : posture stable, pieds au sol, symétrique.

Méthode :
- choisis une **position de pied au repos** par patte (un peu en dehors du corps,
  z négatif sous le corps) ;
- passe les 6 positions dans ton **IK** → 18 angles ;
- publie-les en continu sur `/joint_states`.

✅ **Validé quand :** le robot tient une posture « araignée » stable et symétrique.

---

## ⬜ Étape 6 — Recevoir une commande de vitesse (Twist)

But : écouter l'ordre « avance / décale / tourne ».

Topic imposé par le sujet : **`/cmd_vel`**, type **`geometry_msgs/TwistStamped`**.
Champs utilisés :
- `twist.linear.x` → avant/arrière (m/s)
- `twist.linear.y` → latéral (m/s)
- `twist.angular.z` → rotation (rad/s)

À faire : ajoute à ton nœud un **subscriber** sur `/cmd_vel` qui **mémorise** la
dernière vitesse reçue dans des variables.

Tester sans clavier :
```bash
ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.05}}}'
```

✅ **Validé quand :** quand tu publies un Twist, ton nœud le reçoit (vérifie via un log).

---

## ⬜ Étape 7 — La marche tripode (générer le mouvement)

But : transformer la vitesse reçue en mouvement coordonné des pattes.

**Principe tripode** : 6 pattes = **2 groupes de 3** (un triangle sur deux). À tout
instant, un groupe pousse au sol, l'autre avance en l'air. On alterne. → toujours
3 pieds au sol = stable.

Algorithme **en mots**, à chaque tour de boucle, pour chaque patte :
1. fais avancer un compteur de **phase** entre 0 et 1 (cycle de marche) ;
2. décale les groupes : groupe A à la phase actuelle, groupe B décalé de 0,5 ;
3. selon la phase de la patte :
   - **1ʳᵉ moitié (appui)** : le pied glisse au sol **vers l'arrière** (le corps avance), z au sol ;
   - **2ᵉ moitié (transfert)** : le pied **se lève** (courbe en sinus) et revient **vers l'avant** ;
4. cette position cible du pied → passe-la dans l'**IK** → angles → publie.

Direction : `linear.x/y` = sens de déplacement des pieds au sol ; pour tourner
(`angular.z`), chaque pied bouge **tangentiellement** (comme sur un manège).

> Commence par **avancer tout droit uniquement**. Quand ça marche : ajoute le
> strafe (latéral), puis la rotation.

✅ **Validé quand :** une vitesse avant déclenche un vrai cycle de marche (appui + transfert alternés).

---

## ⬜ Étape 7-bis — Le fichier launch (tout lancer d'un coup)

But : ne plus lancer 3 terminaux à la main.

À faire : un fichier `launch/hexapode.launch.py` qui démarre `robot_state_publisher`
(avec l'URDF), `rviz2`, et ton nœud `hexapode`. Pense à déclarer le dossier `launch/`
dans `setup.py` (`data_files`) pour qu'il soit installé.

```bash
ros2 launch mon_hexapode hexapode.launch.py
```

✅ **Validé quand :** une seule commande lance tout.

---

## ⬜ Étape 8 — (Bonus) Déplacer le corps dans la scène

Pour que le robot avance dans RViz au lieu de marcher sur place :
- garde une position (x, y) + un cap, ajoute à chaque tour `vitesse × temps écoulé`
  (= **odométrie**) ;
- publie une **TF** entre un repère fixe `odom` et `base_link` ;
- dans RViz, mets le **Fixed Frame** sur `odom`.

✅ **Validé quand :** le robot se déplace sur la grille.

---

## ⬜ Étape 9 — Le clavier (téléopération)

But : piloter au clavier au lieu de taper des commandes.

À faire : un **2ᵉ nœud** `teleop_clavier` qui lit une touche et **publie** un Twist
sur `/cmd_vel` (ex. `Z` = avancer, `Espace` = stop). À déclarer aussi dans `setup.py`.

✅ **Validé quand :** tu pilotes le robot au clavier en direct.

---

## ⬜ Étape 10 — Les tests

But : prouver que ça marche.

Idées (sur tes fonctions FK/IK, sans ROS) :
- **round-trip** : IK puis FK → on retombe sur la position demandée ;
- les angles restent **dans les limites** ;
- la pose de repos est **symétrique**.

```bash
cd ~/ros2_hexapode
colcon test            # ou : pytest src/mon_hexapode/test
```

✅ **Validé quand :** tes tests passent au vert.

---

## Récap de l'ordre

| Étape | Tu obtiens | Notion clé |
|---|---|---|
| 0 | ROS2 actif | `source` |
| 1 | workspace + paquet | structure ROS2 / colcon |
| 2 | robot affiché | URDF / RViz |
| 3 | pattes qui bougent | nœud + publisher + `/joint_states` |
| 4 | IK d'une patte | cinématique (le cœur) |
| 5 | robot debout | pose de repos |
| 6 | reçoit une vitesse | subscriber + `/cmd_vel` (Twist) |
| 7 | il marche | démarche tripode |
| 7-bis | tout lancer d'un coup | launch |
| 8 | il se déplace | odométrie + TF |
| 9 | pilotage clavier | 2ᵉ nœud |
| 10 | c'est validé | tests |

## Aide-mémoire des commandes

| Pour… | Commande |
|---|---|
| Activer ROS2 | `source /opt/ros/jazzy/setup.bash` |
| Créer un paquet | `ros2 pkg create --build-type ament_python <nom> --dependencies rclpy geometry_msgs sensor_msgs` |
| Compiler | `colcon build --symlink-install` |
| Activer ton projet | `source install/setup.bash` |
| Lancer un nœud | `ros2 run <paquet> <noeud>` |
| Voir nœuds / topics | `ros2 node list` / `ros2 topic list` |
| Écouter un topic | `ros2 topic echo <topic>` |
| Qui publie/écoute | `ros2 topic info <topic>` |
| Envoyer une vitesse | `ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.05}}}'` |
| Tout lancer | `ros2 launch <paquet> <fichier>.launch.py` |

> Quand tu bloques sur une étape, demande-moi : je t'explique l'idée et te
> débloque **sans te donner la solution toute faite**.
</content>
</invoke>
