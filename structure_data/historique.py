# data_structures/history.py

class Node:
    """Un maillon de la liste chaînée."""
    def __init__(self, value):
        self.value = value
        self.next = None


class CommandHistory:
    """Liste chaînée pour stocker l'historique des commandes d'un utilisateur."""
    def __init__(self):
        self.head = None  # premier élément (le plus ancien)
        self.tail = None  # dernier élément (le plus récent)

    def add_command(self, command: str):
        """Ajoute une commande à la fin de la liste."""
        new_node = Node(command)

        # Si la liste est vide
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            # Sinon on accroche à la fin
            self.tail.next = new_node
            self.tail = new_node

    def last_command(self):
        """Retourne la dernière commande envoyée."""
        if self.tail is None:
            return None
        return self.tail.value

    def get_all(self):
        """Retourne toutes les commandes dans une liste Python."""
        current = self.head
        result = []
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def clear(self):
        """Vide complètement l'historique."""
        self.head = None
        self.tail = None
