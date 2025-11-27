def setup_utils_commands(bot):
    """Déclare les commandes utilitaires (ping, nettoyage, etc.)."""
    
    ## commande ping ##
    @bot.command(name="ping")
    async def ping(ctx):
        await ctx.send("Pong !") # Répond "Pong !" lorsque la commande !ping est utilisée
        
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