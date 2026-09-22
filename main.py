import discord
from discord.ext import commands
from discord import app_commands
import random
from flask import Flask
from threading import Thread

# 1. SERVIDOR FLASK (PARA MANTENERLO ACTIVO)
app = Flask('')

@app.route('/')
def home():
    return "¡El bot está vivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. CONFIGURACIÓN DEL BOT DE DISCORD
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='t!', intents=intents)
bot.remove_command('help')

# SINCRONIZACIÓN DE COMANDOS SLASH
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"¡Bot encendido como {bot.user.name}! Sincronizados {len(synced)} comandos Slash.")
    except Exception as e:
        print(f"Error al sincronizar comandos Slash: {e}")

# --- MANEJO DE ERRORES DE PERMISOS ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes los permisos necesarios para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Te faltaron argumentos. Revisa el comando con `t!ayuda`.")

# --- COMANDOS SLASH ( / ) ---

@bot.tree.command(name="ping", description="Muestra la latencia del bot TECH")
async def slash_ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 ¡Pong! Latencia actual: `{latency}ms`")

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario")
@app_commands.describe(usuario="Usuario del que deseas ver la foto")
async def slash_avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    embed = discord.Embed(
        title=f"🖼️ Avatar de {usuario.display_name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=usuario.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Muestra la información de un usuario")
@app_commands.describe(usuario="Usuario del que deseas ver la información")
async def slash_userinfo(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    roles = [role.mention for role in usuario.roles if role != interaction.guild.default_role]
    
    embed = discord.Embed(
        title=f"👤 Información de {usuario.display_name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{usuario.id}`", inline=True)
    embed.add_field(name="📅 Creación de cuenta", value=f"<t:{int(usuario.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="📥 Ingreso al servidor", value=f"<t:{int(usuario.joined_at.timestamp())}:D>", inline=True)
    embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=", ".join(roles) if roles else "Sin roles", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="Borra una cantidad específica de mensajes")
@app_commands.describe(cantidad="Número de mensajes a borrar")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clear(interaction: discord.Interaction, cantidad: int):
    await interaction.channel.purge(limit=cantidad)
    await interaction.response.send_message(f"🧹 Se han borrado `{cantidad}` mensajes.", ephemeral=True)

@bot.tree.command(name="kick", description="Expulsa a un usuario del servidor")
@app_commands.describe(usuario="Usuario a expulsar", razon="Razón de la expulsión")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, usuario: discord.Member, razon: str = "No especificada"):
    await usuario.kick(reason=razon)
    embed = discord.Embed(
        title="👞 Usuario Expulsado",
        description=f"**{usuario.mention}** fue expulsado del servidor.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Razón", value=razon)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Banea a un usuario del servidor")
@app_commands.describe(usuario="Usuario a banear", razon="Razón del baneo")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, usuario: discord.Member, razon: str = "No especificada"):
    await usuario.ban(reason=razon)
    embed = discord.Embed(
        title="🔨 Usuario Baneado",
        description=f"**{usuario.mention}** fue baneado del servidor.",
        color=discord.Color.red()
    )
    embed.add_field(name="Razón", value=razon)
    embed.add_field(name="Moderador", value=interaction.user.mention)
    await interaction.response.send_message(embed=embed)

# --- COMANDOS SLASH DE ENTRETENIMIENTO ---
@bot.tree.command(name="8ball", description="Hazle una pregunta a la bola 8 mágica")
@app_commands.describe(pregunta="¿Qué deseas consultar?")
async def slash_8ball(interaction: discord.Interaction, pregunta: str):
    respuestas = [
        "En mi opinión, sí. 🟢", "Es totalmente cierto. ✨", "Definitivamente sí. 🚀",
        "Sin duda alguna. ✅", "Pregunta de nuevo más tarde... ⏳", "Mejor no decirte ahora. 🤫",
        "No cuentes con ello. 🔴", "Mi respuesta es no. ❌", "Mis fuentes dicen que no. 🛑", "Muy dudoso. 🤔"
    ]
    respuesta = random.choice(respuestas)
    
    embed = discord.Embed(
        title="🎱 Bola 8 Mágica",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="❓ Pregunta", value=f"*{pregunta}*", inline=False)
    embed.add_field(name="🔮 Respuesta", value=f"**{respuesta}**", inline=False)
    embed.set_footer(text=f"Consultado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dado", description="Lanza un dado de 6 caras")
async def slash_dado(interaction: discord.Interaction):
    resultado = random.randint(1, 6)
    
    embed = discord.Embed(
        title="🎲 Lanzamiento de Dado",
        description=f"{interaction.user.mention} ha lanzado el dado...",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    embed.add_field(name="Resultado", value=f"```txt\n🎲 El dado cayó en: [ {resultado} ]\n```")
    await interaction.response.send_message(embed=embed)

# --- COMANDOS TRADICIONALES DE UTILIDAD Y MODERACIÓN ( t! ) ---

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 ¡Pong! Latencia actual: `{latency}ms`")

@bot.command(aliases=['av', 'pfp'])
async def avatar(ctx, usuario: discord.Member = None):
    usuario = usuario or ctx.author
    embed = discord.Embed(
        title=f"🖼️ Avatar de {usuario.display_name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=usuario.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(aliases=['ui', 'user'])
async def userinfo(ctx, usuario: discord.Member = None):
    usuario = usuario or ctx.author
    roles = [role.mention for role in usuario.roles if role != ctx.guild.default_role]
    
    embed = discord.Embed(
        title=f"👤 Información de {usuario.display_name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{usuario.id}`", inline=True)
    embed.add_field(name="📅 Creación de cuenta", value=f"<t:{int(usuario.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="📥 Ingreso al servidor", value=f"<t:{int(usuario.joined_at.timestamp())}:D>", inline=True)
    embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=", ".join(roles) if roles else "Sin roles", inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=['si', 'server'])
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 Información de {guild.name}",
        color=discord.Color.purple()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Dueño(a)", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="👥 Miembros", value=f"`{guild.member_count}`", inline=True)
    embed.add_field(name="💬 Canales", value=f"`{len(guild.channels)}`", inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=['purge', 'limpiar'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, cantidad: int):
    await ctx.channel.purge(limit=cantidad + 1)
    msg = await ctx.send(f"🧹 Se han borrado `{cantidad}` mensajes.")
    await msg.delete(delay=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, usuario: discord.Member, *, razon="No especificada"):
    await usuario.kick(reason=razon)
    embed = discord.Embed(
        title="👞 Usuario Expulsado",
        description=f"**{usuario.mention}** fue expulsado del servidor.",
        color=discord.Color.orange()
    )
    embed.add_field(name="Razón", value=razon)
    embed.add_field(name="Moderador", value=ctx.author.mention)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, usuario: discord.Member, *, razon="No especificada"):
    await usuario.ban(reason=razon)
    embed = discord.Embed(
        title="🔨 Usuario Baneado",
        description=f"**{usuario.mention}** fue baneado del servidor.",
        color=discord.Color.red()
    )
    embed.add_field(name="Razón", value=razon)
    embed.add_field(name="Moderador", value=ctx.author.mention)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, id_usuario: int):
    user = await bot.fetch_user(id_usuario)
    await ctx.guild.unban(user)
    await ctx.send(f"🔓 El usuario **{user.name}** ha sido desbaneado correctamente.")

# --- COMANDOS TRADICIONALES DE ENTRETENIMIENTO MEJORADOS CON EMBEDS ---

@bot.command(name="8ball")
async def ocho_ball(ctx, *, pregunta: str):
    respuestas = [
        "En mi opinión, sí. 🟢", "Es totalmente cierto. ✨", "Definitivamente sí. 🚀",
        "Sin duda alguna. ✅", "Pregunta de nuevo más tarde... ⏳", "Mejor no decirte ahora. 🤫",
        "No cuentes con ello. 🔴", "Mi respuesta es no. ❌", "Mis fuentes dicen que no. 🛑", "Muy dudoso. 🤔"
    ]
    respuesta = random.choice(respuestas)
    
    embed = discord.Embed(
        title="🎱 Bola 8 Mágica",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="❓ Pregunta", value=f"*{pregunta}*", inline=False)
    embed.add_field(name="🔮 Respuesta", value=f"**{respuesta}**", inline=False)
    embed.set_footer(text=f"Consultado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(aliases=['d'])
async def dado(ctx):
    resultado = random.randint(1, 6)
    
    embed = discord.Embed(
        title="🎲 Lanzamiento de Dado",
        description=f"{ctx.author.mention} ha lanzado el dado...",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    embed.add_field(name="Resultado", value=f"```txt\n🎲 El dado cayó en: [ {resultado} ]\n```")
    await ctx.send(embed=embed)

@bot.command(aliases=['m'])
async def moneda(ctx, eleccion: str = None):
    opciones = ['cara', 'cruz']
    resultado = random.choice(opciones)
    icono = "🪙" if resultado == 'cara' else "👑"
    
    embed = discord.Embed(
        title="🪙 Cara o Cruz",
        color=discord.Color.from_rgb(241, 196, 15)
    )
    
    if eleccion and eleccion.lower() in opciones:
        eleccion_user = eleccion.lower()
        if eleccion_user == resultado:
            mensaje_resultado = f"🎉 **¡Adivinaste!** La moneda cayó en **{resultado.upper()}** {icono}"
            embed.color = discord.Color.green()
        else:
            mensaje_resultado = f"❌ **¡Perdiste!** Elegiste `{eleccion_user}` pero cayó en **{resultado.upper()}** {icono}"
            embed.color = discord.Color.red()
    else:
        mensaje_resultado = f"La moneda se lanzó al aire y cayó en: **{resultado.upper()}** {icono}"

    embed.description = mensaje_resultado
    embed.set_footer(text=f"Lanzado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, mensaje: str):
    await ctx.message.delete()
    await ctx.send(mensaje)

# --- MENÚ DE AYUDA (MANTENIENDO TU TEXTO EXACTO) ---
@bot.command(aliases=['help'])
async def ayuda(ctx):
    embed = discord.Embed(
        title="🤖 Menú de Ayuda - TECH",
        description="Comandos disponibles para usar:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛠️ Utilidad",
        value=(
            "`t!ping` - Latencia del bot.\n"
            "`t!avatar [@usuario]` - Ver avatar de alguien.\n"
            "`t!userinfo [@usuario]` - dice la fecha en la que creo su cuenta, la fecha en la que se unio al servidor y sus roles\n"
            "`t!serverinfo` - Muestra la cantidad de mienbros, dueño y fecha de creacion del servidor."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Moderación",
        value=(
            "`t!clear <cantidad>` - Borra mensajes de un canal.\n"
            "`t!kick @usuario [razón]` - Expulsa a un usuario.\n"
            "`t!ban @usuario [razón]` - Banea a un usuario.\n"
            "`t!unban <ID_usuario>` - Remueve el ban por ID."
        ),
        inline=False
    )

    embed.add_field(
        name="🎉 Entretenimiento",
        value=(
            "`t!8ball <pregunta>` | `/8ball` - Pregunta a la bola 8 mágica.\n"
            "`t!dado` | `t!d` | `/dado` - Lanza un dado de 6 caras.\n"
            "`t!moneda <cara/cruz>` | `t!m` - Lanza una moneda o prueba tu suerte.\n"
            "`t!say <mensaje>` - El bot dice lo que tú escribas."
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# 3. ENCENDIDO
keep_alive()

# Coloca tu TOKEN aquí
# 3. ENCENDIDO
import os
from threading import Thread

def mantener_vivo():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# 1. Inicia el servidor web en segundo plano
mantener_vivo()

# 2. Inicia el bot de Discord
bot.correr(os.environ.get("TOKEN"))
