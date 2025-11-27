import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import DefaultHelpCommand

from structure_data.historique import CommandHistory
from structure_data.arbre import build_tree, tree_contains
from structure_data.sauvegarde import save_state, load_state

from commandes.compte import setup_compte_commands
from commandes.historique import setup_historique_commands
from commandes.discussion import setup_discussion_commands
from commandes.utils import setup_utils_commands

# Chargement du token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Fichier de sauvegarde
os.makedirs("data", exist_ok=True)
SAVE_FILE = "data/etat_bot.json"

# Structures de données globales
user_histories = {}              # user_id -> CommandHistory
conversation_root = build_tree() # racine de l'arbre de discussion
user_positions = {}              # user_id -> TreeNode courant
user_profiles = {}               # user_id -> pseudo
pending_account_creation = set() # user_id en attente de pseudo

# Help personnalisé
class CustomHelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        return ""

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        def fmt(cmd_name):
            cmd = bot.get_command(cmd_name)
            if cmd is None:
                return None
            description = cmd.help or "Aucune description."
            return f"**!{cmd.qualified_name}** — {description}"

        sections = [
            ("1. Compte", ["compte", "moncompte", "users", "supprimercompte"]),
            ("2. Historique", ["last", "historique", "vider_historique"]),
            ("3. Discussion", ["conseils", "reset", "speak"]),
            ("4. Autres", ["ping", "nettoyer"]),
        ]

        embed = discord.Embed(
            title="Commandes disponibles",
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

# Intents et bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=help_command)

# Listener : enregistrement de l'historique des commandes
@bot.listen("on_message")
async def log_command(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content.startswith("!"):
        return

    user_id = message.author.id

    if user_id not in user_histories:
        user_histories[user_id] = CommandHistory()

    command_only = content.split()[0].lower()
    user_histories[user_id].add_command(command_only)

# Listener : gestion de la progression dans l'arbre de discussion
@bot.listen("on_message")
async def handle_conversation(message):
    if message.author.bot:
        return

    user_id = message.author.id

    if user_id not in user_positions:
        return

    node = user_positions[user_id]

    if node.is_leaf:
        return

    content = message.content.strip()

    if not content.isdigit():
        return

    index = int(content) - 1

    if index < 0 or index >= len(node.children):
        await message.channel.send(
            f"Choix invalide. Réponds par un nombre entre 1 et {len(node.children)}."
        )
        return

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

# Enregistrement des commandes par catégorie
setup_compte_commands(bot, user_profiles, user_histories, user_positions, pending_account_creation)
setup_historique_commands(bot, user_histories)
setup_discussion_commands(bot, conversation_root, user_positions, tree_contains)
setup_utils_commands(bot)

# Événement de démarrage
@bot.event
async def on_ready():
    load_state(SAVE_FILE, user_histories, user_positions, user_profiles,
               CommandHistory, conversation_root)
    print(f"Connecté en tant que {bot.user}")

# Sauvegarde et démarrage (appelés depuis start.py)
def save_all():
    print("Sauvegarde de l'état du bot...")
    save_state(SAVE_FILE, user_histories, user_positions, user_profiles)

def start():
    print("Démarrage du bot...")
    bot.run(TOKEN)
