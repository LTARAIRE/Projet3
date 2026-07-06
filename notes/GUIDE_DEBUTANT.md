# Guide débutant — Refaire le projet hexapode pas à pas

> Objectif : construire toi-même, depuis zéro, un hexapode qui marche dans RViz,
> commandé par un message de vitesse. **Approche simple**, étape par étape.
> Ce guide te **guide** : il donne les commandes de base, les noms de topics et
> les algorithmes en mots — **à toi d'écrire le code**.

---

## Conseils de départ

- **Tu réutilises l'URDF de l'autre groupe** : pas besoin de modéliser le robot.
  Mais avant de coder, tu dois **l'inspecter** (voir Étape 2) : récupérer les
  **noms des articulations** et vérifier si les repères sont « droits » ou
  « tordus » (ça décide si l'IK sera simple ou compliquée).
- **Avance par petites étapes** : à chaque étape, tu dois voir un résultat
  concret avant de passer à la suite. Ne code pas tout d'un coup.
- **Teste tout le temps** avec les outils en ligne de commande (`ros2 topic
  echo`, etc.).

---

## Vocabulaire minimum

| Mot | Ce que c'est |
|-----|--------------|
| **Nœud** | un petit programme |
| **Topic** | un canal nommé où circulent des messages |
| **Publier / S'abonner** | envoyer / écouter des messages sur un topic |
| **Message** | une donnée structurée (ex. une vitesse, des angles…) |
| **URDF** | un fichier qui décrit le robot (pièces + articulations) |
| **FK / IK** | cinématique directe (angles→position) / inverse (position→angles) |
| **TF** | le système qui suit la position de chaque repère dans l'espace |

---

## Étape 0 — Préparer l'environnement

1. Vérifie que **ROS2 (Jazzy)** est installé : la commande `ros2 --version` doit répondre.
2. Apprends 4 commandes que tu utiliseras tout le temps :
   - `ros2 node list` → quels nœuds tournent
   - `ros2 topic list` → quels canaux existent
   - `ros2 topic echo <topic>` → voir ce qui circule
   - `ros2 topic info <topic>` → qui publie / écoute

**✅ Objectif atteint quand :** `ros2 --version` répond.

---

## Étape 1 — Créer le workspace et un paquet

Un *workspace* = un dossier de travail. Un *paquet* = une brique de ton projet.

Commandes de base :
- créer les dossiers : un dossier projet avec un sous-dossier `src/`
- créer un paquet Python dans `src/` :
  `ros2 pkg create --build-type ament_python mon_hexapode --dependencies rclpy geometry_msgs sensor_msgs`
- compiler : `colcon build` (à la racine du workspace)
- « activer » : `source install/setup.bash` (à refaire dans chaque terminal)

**✅ Objectif atteint quand :** `colcon build` réussit sans erreur.

---

## Étape 2 — Décrire un robot simple (URDF) et le voir dans RViz

But : afficher un hexapode fait de **cylindres** (pas besoin de pièces 3D).

Idée du modèle à décrire dans l'URDF :
- 1 **corps** (un cylindre plat au centre).
- Pour **chaque patte** (×6), 3 segments reliés par 3 articulations :
  1. **coxa** : tourne autour de l'axe **vertical (Z)** → oriente la patte à gauche/droite,
  2. **fémur** : tourne autour d'un axe **horizontal (Y)** → lève/baisse la patte,
  3. **tibia** : tourne aussi autour de **Y** → plie le « genou ».
- Place les 6 pattes **réparties tous les 60°** autour du corps.

Astuce : utilise **xacro** (un URDF avec des « macros ») pour décrire **une seule
patte** puis la répéter 6 fois avec un angle différent. C'est beaucoup moins
fastidieux.

Pour l'affichage : lance `robot_state_publisher` (te donne la position des
pièces), `joint_state_publisher_gui` (des curseurs pour bouger les articulations)
et **RViz**. Un fichier *launch* lancera les trois d'un coup.

**✅ Objectif atteint quand :** tu vois ton hexapode dans RViz et les curseurs
bougent les pattes.

> 💡 C'est l'étape la plus longue. Prends ton temps sur l'URDF : si une patte est
> bien faite, les 5 autres sont des copies.

---

## Étape 3 — Ton premier nœud qui anime le robot

But : remplacer les curseurs par **ton** programme qui publie les angles.

Le robot s'anime via le topic **`/joint_states`** (type `sensor_msgs/JointState`),
qui contient : la liste des **noms** des articulations + leurs **angles** (en radians).

Structure d'un nœud (à coder toi-même, c'est toujours le même squelette) :
- une classe qui hérite de `Node`,
- un **publisher** sur `/joint_states`,
- un **timer** qui se déclenche ~30 fois/seconde et publie les angles,
- dans `main`, on initialise ROS, on crée le nœud, on le fait tourner.

Pour commencer **simple** : publie des angles **fixes** (ex. tout à 0), puis des
angles qui **varient avec une sinusoïde** pour voir les pattes bouger.

Commandes utiles :
- lancer ton nœud : `ros2 run mon_hexapode <nom_du_noeud>`
- vérifier : `ros2 topic echo /joint_states`

**✅ Objectif atteint quand :** ton nœud fait bouger les pattes dans RViz (même
n'importe comment au début).

---

## Étape 4 — La cinématique inverse d'UNE patte (le cœur)

But : « je veux le bout de la patte à la position (x, y, z), quels sont les 3
angles ? ». Avec ton modèle en cylindres aux axes « droits », l'algorithme est
**simple et analytique** (pas besoin de méthode numérique).

Algorithme (en mots) pour une patte de longueurs L1=coxa, L2=fémur, L3=tibia :

1. **Angle de la coxa** : c'est l'angle horizontal vers la cible →
   `coxa = atan2(y, x)`.
2. On se ramène dans le **plan de la patte** : on calcule la distance horizontale
   du pied (en enlevant la longueur de la coxa), et la hauteur (z). Ça donne un
   triangle dont on connaît les 3 côtés (L2, L3, et la distance pied↔épaule).
3. **Angles fémur et tibia** : on applique le **théorème d'Al-Kashi** (loi des
   cosinus) sur ce triangle pour trouver l'angle du genou (tibia) et l'angle
   d'élévation (fémur).

Conseils :
- Travaille d'abord **sur une seule patte**, dans un petit script Python séparé
  (sans ROS), et **vérifie avec la FK**.
- **FK (vérification)** : connaissant les 3 angles, recalcule la position du pied
  avec de la trigonométrie simple, et vérifie que tu retombes sur la cible.
- Pense à **borner les angles** aux limites physiques (le genou ne plie pas à 360°).

**✅ Objectif atteint quand :** tu donnes une position, l'IK te donne 3 angles,
et la FK confirme que le pied y est bien.

---

## Étape 5 — Faire tenir le robot debout (pose de repos)

But : une posture stable, pieds au sol, symétrique.

Méthode simple :
- choisis une **position de pied au repos** pour chaque patte : un peu en dehors
  du corps, à une hauteur sous le corps (z négatif).
- passe ces 6 positions dans ton **IK** → tu obtiens les 18 angles de la posture.
- publie-les en continu sur `/joint_states`.

**✅ Objectif atteint quand :** le robot tient une posture « araignée » stable et
symétrique dans RViz.

---

## Étape 6 — Recevoir une commande de vitesse (Twist)

But : écouter un ordre « avance / décale / tourne ».

Le standard ROS pour ça (imposé par le sujet) : le topic **`/cmd_vel`**, type
**`geometry_msgs/TwistStamped`**. On utilise 3 champs :
- `twist.linear.x` → vitesse avant/arrière (m/s)
- `twist.linear.y` → vitesse latérale (m/s)
- `twist.angular.z` → vitesse de rotation (rad/s)

À faire : ajoute à ton nœud un **subscriber** sur `/cmd_vel` qui **mémorise** la
dernière vitesse reçue (dans des variables).

Pour tester sans clavier, **envoie une consigne à la main** :
`ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.05}}}'`

**✅ Objectif atteint quand :** quand tu publies un Twist, ton nœud le reçoit (tu
peux l'afficher dans les logs pour vérifier).

---

## Étape 7 — La marche tripode (générer le mouvement)

But : transformer la vitesse reçue en mouvement coordonné des pattes.

**Principe tripode** : on sépare les 6 pattes en **2 groupes de 3** (un triangle
sur deux). À tout instant, un groupe est **au sol** (il pousse), l'autre est **en
l'air** (il avance). Puis on alterne. → 3 pieds toujours au sol = stable.

Algorithme (en mots), répété pour chaque patte à chaque tour de boucle :
1. fais avancer un compteur de **phase** entre 0 et 1 (le cycle de marche).
2. donne à chaque patte une phase **décalée** : groupe A à la phase actuelle,
   groupe B décalé d'un demi-cycle (0,5).
3. selon la phase de la patte :
   - **première moitié (appui)** : le pied glisse au sol **vers l'arrière** par
     rapport à la vitesse demandée → le corps avance. (z reste au sol.)
   - **deuxième moitié (transfert)** : le pied **se lève** (suis une petite courbe,
     ex. un sinus pour la hauteur) et revient **vers l'avant**.
4. cette position cible du pied → passe-la dans ton **IK** → angles → publie.

Pour la **direction** : la vitesse `linear.x/y` donne le sens du déplacement des
pieds au sol ; pour **tourner** (`angular.z`), chaque pied bouge tangentiellement
(comme sur un manège).

Commence **simple** : ne gère d'abord que **avancer tout droit**. Quand ça marche,
ajoute le strafe, puis la rotation.

**✅ Objectif atteint quand :** quand tu publies une vitesse avant, les pattes
font un vrai cycle de marche (appui + transfert alternés).

---

## Étape 8 — (Bonus) Faire avancer le corps dans la scène

Au début, le robot marche « sur place ». Pour qu'il **se déplace** dans RViz :
- garde une position (x, y) et un cap, et **ajoute** à chaque tour
  `vitesse × temps écoulé` (c'est l'**odométrie**).
- publie cette position comme une **TF** entre un repère fixe `odom` et le corps
  `base_link`.
- dans RViz, mets le repère de référence (« Fixed Frame ») sur `odom`.

**✅ Objectif atteint quand :** le robot se déplace sur la grille au lieu de
rester centré.

---

## Étape 9 — Le clavier (téléopération)

But : piloter au clavier au lieu de taper des commandes.

À faire : un **deuxième nœud** qui lit une touche et **publie** un Twist sur
`/cmd_vel` (ex. `Z`=avancer → `linear.x = vitesse`, `Espace`=stop → tout à 0).

**✅ Objectif atteint quand :** tu pilotes le robot au clavier en direct.

---

## Étape 10 — Les tests

But : prouver que ça marche (et impressionner le prof).

Idées de tests simples (sur tes fonctions FK/IK, sans ROS) :
- **round-trip** : IK puis FK → on doit retomber sur la position demandée.
- les angles trouvés restent **dans les limites**.
- la pose de repos est **symétrique** (mêmes hauteurs).

Lance-les avec `pytest`.

**✅ Objectif atteint quand :** tes tests passent au vert.

---

## Récap de l'ordre + ce que tu apprends

| Étape | Tu obtiens | Notion clé |
|-------|-----------|------------|
| 1 | workspace + paquet | structure ROS2 |
| 2 | robot affiché | URDF / RViz |
| 3 | pattes qui bougent | nœud + publisher + `/joint_states` |
| 4 | IK d'une patte | cinématique (le cœur) |
| 5 | robot debout | pose de repos |
| 6 | reçoit une vitesse | subscriber + `/cmd_vel` (Twist) |
| 7 | il marche | démarche tripode |
| 8 | il se déplace | odométrie + TF |
| 9 | pilotage clavier | 2e nœud |
| 10 | c'est validé | tests |

---

## Les commandes que tu utiliseras le plus

| Pour… | Commande |
|-------|----------|
| Créer un paquet | `ros2 pkg create --build-type ament_python <nom> --dependencies rclpy geometry_msgs sensor_msgs` |
| Compiler | `colcon build` |
| Activer | `source install/setup.bash` |
| Lancer un nœud | `ros2 run <paquet> <noeud>` |
| Voir les nœuds / topics | `ros2 node list` / `ros2 topic list` |
| Écouter un topic | `ros2 topic echo <topic>` |
| Envoyer une vitesse | `ros2 topic pub -r 30 /cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.05}}}'` |
| Tout lancer (launch) | `ros2 launch <paquet> <fichier>.launch.py` |

> Quand tu bloques sur une étape, demande-moi : je t'explique l'idée et te
> débloque, **sans te donner la solution toute faite**, pour que tu apprennes.
