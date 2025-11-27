def setup_historique_commands(bot, user_histories):
    """Déclare les commandes liées à l'historique."""

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