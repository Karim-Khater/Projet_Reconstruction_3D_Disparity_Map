Pour que le programme fonctionne vous devez avoir un dossier nommé ``Disp_2_png`` pour sortir la carte de disparité en PNG dans ce dossier.

- J'ai testé avec tous les dossiers de validation et certains des dossiers de tests, tout a fonctionné sauf le dossier ``/Validation/WoodenHouse/`` dont le nom causait de problemes alors  je l'ai modifié mais toujours j'obtiens un erreur lorsque j'ai essayé d'exécuter la fonction de projection d'images multiples.
- J'ai testé avec seulement 16 images de grille de cameras de taille 4x4, mais cela devrait également fonctionner avec 3x3 et 5x5 etc. tant que la taille est supérieure à 2x2 (je n'ai pas implémenté le 2x2 car c'est comme si j'utilise la caméra situé au coin de la grille de caméras)
- les images doivent être placées de gauche à droite et de haut en bas.
- **A la ligne 286 :** vous pouvez fournir le chemin vers le jeu de données. Il doit inclure les images au format .PNG et les cartes de disparité au format .EXR, assurez-vous que chaque image correspond à chaque disparité avec le même numéro et doit commencer par 0.
- **Ligne 290 à 293 :** ici vous pouvez assigner les positions de la caméra à projeter (``pos_i2,pos_j2``) et la source de la caméra (``pos_i1,pos_j1``) pour la fonction ``project()`` qui projette une image ou une carte de disparité une fois.
- **ligne 307/308 :** ici vous pouvez assigner la position de la caméra dans la grille utilisée dans ``multiple_projection()``
- A la fin, dans le terminal utilisez ``python3 .\Comp_Disp.py`` pour executer le programme.


UPDATE (17/04/2022)
- ADDED error evaluation function for the multiple images projection function

