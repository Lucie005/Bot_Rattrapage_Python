import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from structure_data.historique import CommandHistory

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

    # On enregistre la commande
    user_histories[user_id].add_command(message.content)

#commande ping#
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !") # Répond "Pong !" lorsque la commande !ping est utilisée

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
