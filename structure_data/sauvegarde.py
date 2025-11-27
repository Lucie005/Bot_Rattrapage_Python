import json
import os


def save_state(filepath, user_histories, user_positions, user_profiles):
    """
    Sauvegarde l'état du bot dans un fichier JSON.
    - user_histories : dict[user_id -> CommandHistory]
    - user_positions : dict[user_id -> TreeNode courant]
    """
    data = {
        "histories": {},
        "positions": {},
        "users": {}

    }

    # On convertit les historiques en listes de chaînes
    for user_id, history in user_histories.items():
        data["histories"][str(user_id)] = history.get_all()

    # On sauvegarde la position sous forme de texte du node
    for user_id, node in user_positions.items():
        data["positions"][str(user_id)] = node.text
        
    # Sauvegarder les pseudos
    for user_id, username in user_profiles.items():
        data["users"][str(user_id)] = username


    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state(filepath, user_histories, user_positions, user_profiles, history_class, conversation_root):
    """
    Recharge l'état du bot à partir du fichier JSON, si il existe.
    - history_class : la classe à utiliser pour recréer les historiques (CommandHistory)
    - conversation_root : racine de l'arbre, pour retrouver les nodes par leur texte
    """
    if not os.path.exists(filepath):
        return  # première exécution, rien à charger

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    ####### Reconstituer les historiques #######
    
    for user_id_str, commands in data.get("histories", {}).items():
        h = history_class()
        for cmd in commands:
            h.add_command(cmd)
        user_histories[int(user_id_str)] = h

    ####### Reconstituer les positions dans l'arbre #######

    def find_node_by_text(node, text):
        if node.text == text:
            return node
        for child in node.children:
            found = find_node_by_text(child, text)
            if found is not None:
                return found
        return None

    for user_id_str, node_text in data.get("positions", {}).items():
        node = find_node_by_text(conversation_root, node_text)
        if node is not None:
            user_positions[int(user_id_str)] = node

    ####### Reconstituer les pseudos #######
    for user_id_str, username in data.get("users", {}).items():
        user_profiles[int(user_id_str)] = username