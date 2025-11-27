import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from structure_data.historique import CommandHistory
from structure_data.arbre import build_tree, tree_contains


### Personnalisation de la commande d'aide ###
from discord.ext.commands import DefaultHelpCommand

class CustomHelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        # On supprime complètement la note finale
        return ""

help_command = CustomHelpCommand(no_category="Commandes disponibles")

### Configuration du bot ###

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

user_histories = {}  # Dictionnaire : user_id -> CommandHistory

# Arbre de conversation et position de chaque utilisateur
conversation_root = build_tree()
user_positions = {}  # dict : user_id -> TreeNode courant


intents = discord.Intents.default()
intents.message_content = True  # très important pour lire le contenu des messages

bot = commands.Bot(command_prefix="!", intents=intents, help_command=help_command)

#### Événements du bot ####
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}") # Affiche un message lorsque le bot est prêt


######### Commandes du bot #########
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

    # On enregistre la commande
    user_histories[user_id].add_command(message.content)
    
#commande ping#
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !") # Répond "Pong !" lorsque la commande !ping est utilisée
    

#commande pour démarrer la conversation#
@bot.command(name="conseils")
async def start_conversation(ctx):
    """Lance le questionnaire de conseils d'activités."""
    user_id = ctx.author.id
    user_positions[user_id] = conversation_root

    await ctx.send(
        conversation_root.text
        + "\n\nRéponds en tapant le numéro de ton choix (`1`, `2`, `3` ou `4`)."
    )
    
#commande pour reset la conversation#
@bot.command()
async def reset(ctx):
    """Repart de la racine de l'arbre de discussion pour !conseils."""
    user_id = ctx.author.id
    user_positions[user_id] = conversation_root

    await ctx.send(
        "La discussion de conseils a été réinitialisée.\n\n"
        + conversation_root.text
        + "\n\nRéponds par le numéro de ton choix."
    )
    
#commande pour parler d'un sujet#
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


#dernière commande rentrée#
@bot.command()
async def last(ctx):
    user_id = ctx.author.id
    history = user_histories.get(user_id)

    if history is None or history.last_command() is None:
        await ctx.send("Tu n'as pas encore d'historique.")
    else:
        await ctx.send(f"Dernière commande : `{history.last_command()}`")


@bot.command()
async def history(ctx):
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


#commande pour effacer tout l'historique#
@bot.command()
async def clear_history(ctx):
    user_id = ctx.author.id

    # On supprime complètement l'historique de ce user
    user_histories.pop(user_id, None)

    await ctx.send("Ton historique a été effacé !")



bot.run(TOKEN)
