import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from structure_data.historique import CommandHistory
from structure_data.arbre import build_tree, tree_contains
from structure_data.sauvegarde import save_state, load_state


### Personnalisation de la commande d'aide ###
from discord.ext.commands import DefaultHelpCommand

class CustomHelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        # On supprime complètement la note finale
        return ""

    async def send_bot_help(self, mapping):
        """Affiche un help personnalisé, groupé, dans un embed."""
        ctx = self.context
        bot = ctx.bot

        # Petite fonction utilitaire pour formatter une commande
        def fmt(cmd_name):
            cmd = bot.get_command(cmd_name)
            if cmd is None:
                return None
            description = cmd.help or "Aucune description."
            return f"**!{cmd.qualified_name}** — {description}"

        sections = [
            ("1. Compte", ["compte", "moncompte", "users","supprimercompte"]),
            ("2. Historique", ["last", "historique", "vider_historique"]),
            ("3. Discussion", ["conseils", "reset", "speak"]),
            ("4. Autres", ["ping", "nettoyer"]),
        ]

        embed = discord.Embed(
            title="COMMANDES DISPONIBLES",
            color=discord.Color.blurple()
        )

        for titre, noms_cmds in sections:
            lignes = []
            for name in noms_cmds:
                row = fmt(name)
                if row:
                    lignes.append(row)

            if lignes:
                embed.add_field(
                    name=titre,
                    value="\n".join(lignes),
                    inline=False
                )

        await ctx.send(embed=embed)

help_command = CustomHelpCommand()


### Configuration du bot ###

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SAVE_FILE = "data/etat_bot.json"

user_histories = {}  # CommandHistory
conversation_root = build_tree() # Arbre de conversation et position de chaque utilisateur
user_positions = {}  # TreeNode courant
user_profiles = {}  # pseudo choisi par l'utilisateur
pending_account_creation = set()  # ensemble d'user_id en attente de pseudo



intents = discord.Intents.default()
intents.message_content = True  # très important pour lire le contenu des messages

bot = commands.Bot(command_prefix="!", intents=intents, help_command=help_command)

#### Événements du bot ####
@bot.event
async def on_ready():
    load_state(SAVE_FILE, user_histories, user_positions, user_profiles, CommandHistory, conversation_root)
    print(f"Connecté en tant que {bot.user}") # Affiche un message lorsque le bot est prêt


######### Commandes du bot #########

#commande pour créer ou modifier un pseudo utilisateur#
@bot.command(name="compte")
async def register_account(ctx):
    """Lance la création ou modification de ton pseudo."""
    user_id = ctx.author.id

    # On marque que cet utilisateur doit répondre avec son pseudo
    pending_account_creation.add(user_id)

    if user_id in user_profiles:
        await ctx.send(
            f"Tu as déjà un pseudo ! **{user_profiles[user_id]}**.\n"
            "Si tu veux le changer, envoie simplement le nouveau pseudo."
        )
    else:
        await ctx.send(
            "Quel pseudo souhaites-tu utiliser ?"
        )

## commande pour afficher le pseudo utilisateur ##
@bot.command(name="moncompte")
async def show_account(ctx):
    """Affiche le pseudo enregistré de l'utilisateur."""
    user_id = ctx.author.id

    if user_id not in user_profiles:
        await ctx.send("Tu n'as pas encore de pseudo. Utilise : `!compte nom`")
    else:
        await ctx.send(f"Ton pseudo actuel est : **{user_profiles[user_id]}**")


## commande pour lister tous les utilisateurs ##
@bot.command(name="users")
async def list_users(ctx):
    """Liste tous les utilisateurs qui ont un pseudo."""
    if not user_profiles:
        await ctx.send("Aucun utilisateur n'a encore créé de pseudo.")
        return

    pseudos = sorted(user_profiles.values(), key=str.lower)
    texte = "\n".join([f"- {pseudo}" for pseudo in pseudos])

    await ctx.send(f"Liste des utilisateurs enregistrés :\n```{texte}```")

## commande pour supprimer le compte utilisateur ##   
@bot.command(name="supprimercompte")
async def delete_account(ctx):
    """Supprime ton pseudo, ton historique et ta progression dans la discussion."""
    user_id = ctx.author.id

    if user_id not in user_profiles:
        await ctx.send("Tu n'as pas encore de compte à supprimer.")
        return

    old_name = user_profiles.pop(user_id)

    # Nettoyage des données liées à l'utilisateur
    user_histories.pop(user_id, None)
    user_positions.pop(user_id, None)
    pending_account_creation.discard(user_id)

    await ctx.send(
        f"Le compte **{old_name}** et toutes les données associées ont bien été supprimés ✔️"
    )


## commande pour logger les commandes des utilisateurs ##
@bot.listen("on_message")
async def log_command(message):
    # ignorer les messages du bot
    if message.author.bot:
        return

    # On ne log que les commandes commençant par !
    if not message.content.startswith("!"):
        return

    user_id = message.author.id

    # Si l'utilisateur n'a pas encore d'historique → on lui en crée un
    if user_id not in user_histories:
        user_histories[user_id] = CommandHistory()

    # On enregistre la commande dans l'historique
    user_histories[user_id].add_command(message.content)


## commande pour gérer la conversation dans l'arbre ##
@bot.listen("on_message")
async def handle_conversation(message):
    # On ignore les bots
    if message.author.bot:
        return

    user_id = message.author.id

    # Si l'utilisateur n'est pas dans une conversation, on ne fait rien
    if user_id not in user_positions:
        return

    node = user_positions[user_id]

    # Si on est déjà sur une feuille (conclusion), on ne traite plus
    if node.is_leaf:
        return

    content = message.content.strip()

    # On attend un nombre (1, 2, 3, 4, etc.)
    if not content.isdigit():
        return

    index = int(content) - 1  # choix humain (1..n) -> index (0..n-1)

    if index < 0 or index >= len(node.children):
        await message.channel.send(
            f"Choix invalide. Réponds par un nombre entre 1 et {len(node.children)}."
        )
        return

    # On avance dans l'arbre
    next_node = node.children[index]
    user_positions[user_id] = next_node

    if next_node.is_leaf:
        await message.channel.send(
            next_node.text
            + "\n\nTu peux taper `!reset` pour recommencer les conseils."
        )
    else:
        await message.channel.send(
            next_node.text
            + f"\n\nRéponds par un nombre entre 1 et {len(next_node.children)}."
        )

## commande pour gérer la création de compte ##
@bot.listen("on_message")
async def handle_account_creation(message):
    """Gère la réponse de l'utilisateur après !compte."""
    if message.author.bot:
        return

    user_id = message.author.id

    # Si l'utilisateur n'est pas en phase de création de compte, on ne fait rien
    if user_id not in pending_account_creation:
        return

    # Si l'utilisateur tape une commande au lieu d'un pseudo, on ignore
    if message.content.startswith("!"):
        return

    username = message.content.strip()

    if len(username) < 2:
        await message.channel.send(
            "Ton pseudo doit faire au moins 2 caractères.\n"
            "Réessaie en envoyant simplement le pseudo que tu souhaites utiliser."
        )
        return

    # On enregistre le pseudo
    user_profiles[user_id] = username
    pending_account_creation.remove(user_id)

    await message.channel.send(
        f"Compte créé avec succès ! :D\n"
        f"Ton pseudo est maintenant : **{username}**"
    )


## commande ping ##
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong !") # Répond "Pong !" lorsque la commande !ping est utilisée

## commande pour démarrer la conversation ##
@bot.command(name="conseils")
async def start_conversation(ctx):
    """Lance le questionnaire de conseils d'activités."""
    user_id = ctx.author.id
    user_positions[user_id] = conversation_root

    await ctx.send(
        conversation_root.text
        + "\n\nRéponds en tapant le numéro de ton choix (`1`, `2`, `3` ou `4`)."
    )
    
## commande pour reset la conversation ##
@bot.command(name="reset")
async def reset(ctx):
    """Repart de la racine de l'arbre de discussion pour !conseils."""
    user_id = ctx.author.id
    user_positions[user_id] = conversation_root

    await ctx.send(
        "La discussion de conseils a été réinitialisée.\n\n"
        + conversation_root.text
        + "\n\nRéponds par le numéro de ton choix."
    )
    
## commande pour parler d'un sujet ##
@bot.command(name="speak")
async def speak_about(ctx, *, topic: str):
    """
    Commande du sujet :
    !speak about X → vérifie si le sujet X existe dans l'arbre
    On accepte aussi : !speak X
    """
    text = topic.strip()

    # Si l'utilisateur tape "about X", on enlève le "about "
    if text.lower().startswith("about "):
        text = text[6:]

    if not text:
        await ctx.send("Merci de préciser un sujet, par exemple : `!speak about hiver`.")
        return

    if tree_contains(conversation_root, text):
        await ctx.send(f"Oui, je parle de **{text}** quelque part dans mon arbre.")
    else:
        await ctx.send(f"Non, je ne parle pas de **{text}** dans mon arbre.")


## dernière commande rentrée ##
@bot.command(name="last")
async def last(ctx):
    """Affiche la dernière commande que tu as utilisée."""
    user_id = ctx.author.id
    history = user_histories.get(user_id)

    if history is None or history.last_command() is None:
        await ctx.send("Tu n'as pas encore d'historique.")
    else:
        await ctx.send(f"Dernière commande : `{history.last_command()}`")


## commande pour afficher tout l'historique ##
@bot.command(name="historique")
async def historique(ctx):
    """Affiche toutes les commandes que tu as utilisées depuis le début."""
    user_id = ctx.author.id
    history = user_histories.get(user_id)

    # Aucun historique créé pour cet utilisateur
    if history is None:
        await ctx.send("Tu n'as pas encore d'historique.")
        return

    all_cmds = history.get_all()

    # La liste chaînée existe mais est vide
    if not all_cmds:
        await ctx.send("Ton historique est vide.")
        return

    # Sinon on affiche tout l'historique
    text = "\n".join(all_cmds)
    await ctx.send(f"Voici ton historique :\n```{text}```")


## commande pour effacer tout l'historique ##
@bot.command(name="vider_historique")
async def vider_historique(ctx):
    """Efface complètement ton historique de commandes."""
    user_id = ctx.author.id

    # On supprime complètement l'historique de ce user
    user_histories.pop(user_id, None)

    await ctx.send("Ton historique a été effacé !")
    
## commande pour nettoyer les messages dans un salon ##    
@bot.command(name="nettoyer")
async def nettoyer(ctx, arg: str = None):
    """
    Nettoie les messages dans ce salon.
    - !nettoyer              → supprime ~50 messages récents (commandes + bot)
    - !nettoyer 120          → supprime ~120 messages récents
    - !nettoyer tout         → essaie de supprimer tous les messages possibles (limite Discord ~14 jours)
    """
    # Fonction qui décide quels messages supprimer
    def check(message):
        # On supprime :
        # - les messages du bot
        # - les messages de commandes (qui commencent par "!")
        return (
            message.author == ctx.bot.user
            or message.content.startswith("!")
        )

    # Cas: !nettoyer tout
    if arg is not None and arg.lower() == "tout":
        deleted = await ctx.channel.purge(limit=None, check=check)
        await ctx.send(
            f"Nettoyage complet effectué 🧹 ({len(deleted)} messages supprimés, dans la limite autorisée par Discord).",
            delete_after=5
        )
        return

    # Cas: !nettoyer 120 ou !nettoyer 50
    # si arg est un nombre → on l'utilise comme limite
    limite_par_defaut = 50

    if arg is None:
        limite = limite_par_defaut
    else:
        if not arg.isdigit():
            await ctx.send(
                "Utilisation : `!nettoyer`, `!nettoyer 120` ou `!nettoyer tout`.",
                delete_after=7
            )
            return
        limite = int(arg)

    if limite < 1:
        await ctx.send("La limite doit être au moins 1.", delete_after=5)
        return
    if limite > 500:
        limite = 500  # on évite d'aller trop haut d'un coup

    deleted = await ctx.channel.purge(limit=limite, check=check)

    await ctx.send(
        f"J'ai nettoyé {len(deleted)} messages dans ce salon ",
        delete_after=15
    )


def save_all():
    print("Sauvegarde de l'état du bot...")
    save_state(SAVE_FILE, user_histories, user_positions, user_profiles)

def save_all():
    print("Sauvegarde de l'état du bot...")
    save_state(SAVE_FILE, user_histories, user_positions, user_profiles)

def start():
    """Démarre le bot Discord."""
    print("Démarrage du bot...")
    bot.run(TOKEN)

