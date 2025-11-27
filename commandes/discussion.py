def setup_discussion_commands(bot, conversation_root, user_positions, tree_contains):
    """Déclare les commandes liées à l'arbre de discussion."""
    
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
