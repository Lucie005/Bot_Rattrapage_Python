class TreeNode:
    """Nœud d'un arbre de conversation."""
    def __init__(self, text, children=None, is_leaf=False):
        self.text = text              # question ou conclusion
        self.children = children or []  # liste de TreeNode
        self.is_leaf = is_leaf        # True si c'est une conclusion

    def add_child(self, node):
        self.children.append(node)


def build_tree():
    """
    Arbre de discussion :

    1) L'utilisateur choisit la saison qu'il vit actuellement
       (printemps / été / automne / hiver)
    2) Il dit s'il est introverti(e) ou extraverti(e)
    3) On propose une activité adaptée
    """

    # Question de départ : saison en cours
    root = TreeNode(
        "On va te proposer une activité sympa en fonction de la saison et de ton caractère !\n"
        "En ce moment, tu es en quelle saison ?\n"
        "1) Printemps\n"
        "2) Été\n"
        "3) Automne\n"
        "4) Hiver"
    )

    # Pour chaque saison, on pose la même question de personnalité
    printemps = TreeNode(
        "Tu es au printemps !\n"
        "Tu te considères plutôt comme :\n"
        "1) Introverti(e)\n"
        "2) Extraverti(e)"
    )

    ete = TreeNode(
        "Tu es en été !\n"
        "Tu te considères plutôt comme :\n"
        "1) Introverti(e)\n"
        "2) Extraverti(e)"
    )

    automne = TreeNode(
        "Tu es en automne !\n"
        "Tu te considères plutôt comme :\n"
        "1) Introverti(e)\n"
        "2) Extraverti(e)"
    )

    hiver = TreeNode(
        "Tu es en hiver !\n"
        "Tu te considères plutôt comme :\n"
        "1) Introverti(e)\n"
        "2) Extraverti(e)"
    )

    # On branche les 4 saisons sur la racine (ordre = numéros 1..4)
    root.add_child(printemps)  # 1
    root.add_child(ete)        # 2
    root.add_child(automne)    # 3
    root.add_child(hiver)      # 4

    # --- Feuilles : activités par saison + caractère ---

    # Printemps
    printemps.add_child(TreeNode(
        "Tu es introverti(e) au printemps !\n"
        "Activité conseillée : aller lire dans un parc fleuri ou faire une balade tranquille en nature.",
        is_leaf=True
    ))
    printemps.add_child(TreeNode(
        "Tu es extraverti(e) au printemps !\n"
        "Activité conseillée : organiser un pique-nique avec tes amis dans un parc.",
        is_leaf=True
    ))

    # Été
    ete.add_child(TreeNode(
        "Tu es introverti(e) en été !\n"
        "Activité conseillée : lire ou dessiner à la plage tôt le matin, ou regarder des films au frais chez toi.",
        is_leaf=True
    ))
    ete.add_child(TreeNode(
        "Tu es extraverti(e) en été !\n"
        "Activité conseillée : aller à la plage avec tes amis ou organiser un barbecue / soirée en extérieur.",
        is_leaf=True
    ))

    # Automne
    automne.add_child(TreeNode(
        "Tu es introverti(e) en automne !\n"
        "Activité conseillée : aller dans un café cosy avec un bon livre "
        "ou faire une promenade en forêt pour admirer les couleurs.",
        is_leaf=True
    ))
    automne.add_child(TreeNode(
        "Tu es extraverti(e) en automne ! \n"
        "Activité conseillée : organiser une soirée jeux de société ou un marathon Harry Potter avec des amis.",
        is_leaf=True
    ))

    # Hiver
    hiver.add_child(TreeNode(
        "Tu es introverti(e) en hiver !\n"
        "Activité conseillée : soirée plaid + chocolat chaud + série/film, ou jeux vidéo au chaud chez toi.",
        is_leaf=True
    ))
    hiver.add_child(TreeNode(
        "Tu es extraverti(e) en hiver !\n"
        "Activité conseillée : aller à la patinoire avec tes amis ou organiser une bataille de neige si possible !",
        is_leaf=True
    ))

    return root


def tree_contains(node: TreeNode, keyword: str) -> bool:
    """Parcourt l'arbre et vérifie si 'keyword' apparaît dans un des textes."""
    if keyword.lower() in node.text.lower():
        return True
    for child in node.children:
        if tree_contains(child, keyword):
            return True
    return False
