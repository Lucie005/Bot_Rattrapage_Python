def setup_compte_commands(bot, user_profiles, user_histories,
                          user_positions, pending_account_creation):
    """Déclare toutes les commandes liées aux comptes utilisateur."""

    @bot.command(name="compte")
    async def register_account(ctx):
        """Lance la création ou modification de ton pseudo."""
        user_id = ctx.author.id

        # On marque que cet utilisateur doit répondre avec son pseudo
        pending_account_creation.add(user_id)

        if user_id in user_profiles:
            await ctx.send(
                f"Tu as déjà un pseudo : **{user_profiles[user_id]}**.\n"
                "Envoie-moi simplement le **nouveau pseudo** que tu souhaites utiliser."
            )
        else:
            await ctx.send(
                "Création de compte 📝\n"
                "Envoie-moi maintenant le **pseudo** que tu souhaites utiliser."
            )

    @bot.listen("on_message")
    async def handle_account_creation(message):
        """Gère la réponse de l'utilisateur après !compte."""
        if message.author.bot:
            return

        user_id = message.author.id

        if user_id not in pending_account_creation:
            return

        if message.content.startswith("!"):
            return

        username = message.content.strip()

        if len(username) < 2:
            await message.channel.send(
                "Ton pseudo doit faire au moins 2 caractères.\n"
                "Réessaie en envoyant simplement le pseudo que tu souhaites utiliser."
            )
            return

        user_profiles[user_id] = username
        pending_account_creation.remove(user_id)

        await message.channel.send(
            f"Compte créé avec succès ! 🎉\n"
            f"Ton pseudo est maintenant : **{username}**"
        )

    @bot.command(name="moncompte")
    async def show_account(ctx):
        """Affiche le pseudo enregistré de l'utilisateur."""
        user_id = ctx.author.id

        if user_id not in user_profiles:
            await ctx.send("Tu n'as pas encore de pseudo. Utilise : `!compte`.")
        else:
            await ctx.send(f"Ton pseudo actuel est : **{user_profiles[user_id]}**")

    @bot.command(name="users")
    async def list_users(ctx):
        """Liste tous les pseudos des utilisateurs ayant un compte."""
        if not user_profiles:
            await ctx.send("Aucun utilisateur n'a encore créé de pseudo.")
            return

        pseudos = sorted(user_profiles.values(), key=str.lower)
        texte = "\n".join([f"- {pseudo}" for pseudo in pseudos])

        await ctx.send(f"Liste des utilisateurs enregistrés :\n```{texte}```")

    @bot.command(name="supprimercompte")
    async def delete_account(ctx):
        """Supprime ton pseudo, ton historique et ta progression dans la discussion."""
        user_id = ctx.author.id

        if user_id not in user_profiles:
            await ctx.send("Tu n'as pas encore de compte à supprimer.")
            return

        old_name = user_profiles.pop(user_id)

        user_histories.pop(user_id, None)
        user_positions.pop(user_id, None)
        pending_account_creation.discard(user_id)

        await ctx.send(
            f"Le compte **{old_name}** et toutes les données associées ont bien été supprimés ✔️"
        )