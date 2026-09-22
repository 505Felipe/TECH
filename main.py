import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Configuración de Flask (Servidor Web)
app = Flask('')

@app.route('/')
def home():
    return "Bot TECH en línea!"

def ejecutar_servidor():
    app.run(host='0.0.0.0', port=8080)

def mantener_vivo():
    t = Thread(target=ejecutar_servidor)
    t.start()

# Configuración del Bot de Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="t!", intents=intents)

@bot.event
async def on_ready():
    print(f'¡Bot conectado con éxito como {bot.user}!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 ¡Pong! Latencia: {round(bot.latency * 1000)}ms')

# ENCENDIDO
if __name__ == '__main__':
    mantener_vivo()
    token = os.environ.get("TOKEN")
    if token:
        bot.run(token)
    else:
        print("ERROR: No se encontró la variable TOKEN en Render.")
        
