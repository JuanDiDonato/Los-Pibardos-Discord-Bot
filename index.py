#Discord
import discord
from discord.ext import commands
from discord.utils import get
#otros
import datetime
from urllib import parse, request
import re
import youtube_dl
import os

#Prefix
bot = commands.Bot(command_prefix="<")

#Defino lista
lista = []

#Eventos
@bot.event
async def on_ready(): #cuando inicie, imprime en consola.
    await bot.change_presence(activity=discord.Game(name="Pone '<ayuda' para ver los comandos!"))
    print("[+] Bot conectado")

#Creacion de comandos

#Hola
@bot.command()
async def hola(ctx):
    await ctx.send("Que ondaa!")

#Help
@bot.command()
async def ayuda(ctx):
    await ctx.send(" LISTA DE COMANDOS :")
    await ctx.send(" '<hola' ==> (El bot saluda)")
    await ctx.send(" '<play' + [cancion] ==> (El bot busca y reproduce una cancion desde youtube, tenes que estar en un canal de voz)")
    await ctx.send(" '<pause' ==> (Pausa la musica)")
    await ctx.send(" '<unpause' ==> (Despausa la musica)")
    await ctx.send(" '<stop' ==> (Detiene la musica)")
    await ctx.send(" '<next' ==> (Pasa al siguiente en la lista)")
    await ctx.send(" '<sali' ==> (Desconecta al bot del canal)")
    await ctx.send(" '<info' ==> (Muestra informacion del server.)")
    await ctx.send(" '<entra' ==> (Conecta el bot al canal)")


#Conectar
@bot.command(pass_context = True)
async def entra(ctx):
    #identifica el canal de donde llaman al bot
    canal = ctx.message.author.voice.channel
    if not canal:
        await ctx.send('[-]No estas conectado a un canal de voz :(')
        return
    voz = get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.move_to(canal)
    else:
        voz = await canal.connect()

#Desconectar
@bot.command(pass_context = True)
async def sali(ctx):
    canal = ctx.message.author.voice.channel
    voz = get(bot.voice_clients, guild=ctx.guild)
    await voz.disconnect()

#Info del server
@bot.command()
async def info(ctx):
    #embed clase de discord que manda mensajes resaltados
    embed = discord.Embed(title=f"{ctx.guild.name}",
    description="Server de Los Pibardos",timestamp=datetime.datetime.utcnow(), color=discord.Color.red())
    embed.add_field(name="Creacion del todo poderoso, el dia" , value=f"{ctx.guild.created_at}") #con add_field agrego mas info (texto)
    embed.add_field(name="Diosito del server ", value=f"{ctx.guild.owner}")
    embed.add_field(name="Region del paraiso ", value=f"{ctx.guild.region}")
    embed.add_field(name="Server id ", value=f"{ctx.guild.id}")
    embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1268868861782298626/doLOgx55.jpg")
    await ctx.send(embed=embed)

#Pause
@bot.command(pass_context = True)
async def pause(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)

    #si el bot esta reproduciendo
    if voz and voz.is_playing():
        print('[+] Musica pausada')
        voz.pause()
        await ctx.send('[//] Musica pausada, me muteo un toque. Pone "<unpause" para continuar!')
    else:
        print('[-] No se esta reproduciendo nada.')
        await ctx.send('[-] No se esta reproduciendo nada =(')

#Unpause
@bot.command(pass_context = True)
async def unpause(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)

    if voz and voz.is_paused():
        print('[|>] Continuando la reproduccion')
        voz.resume()
        await ctx.send('[|>] Continuando la reproduccion (͠≖ ͜ʖ͠≖)')
    else:
        print('[-] No hay nada pausado')
        await ctx.send('[-] No hay nada pausado pibe :v')

#Stop
@bot.command(pass_context = True)
async def stop(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    lista.clear()
    if voz and voz.is_playing():
        print('[!] Musica detenida')
        voz.stop()
        await ctx.send('[!] Musica detenida :c ')
        canal = ctx.message.author.voice.channel
        voz = get(bot.voice_clients, guild=ctx.guild)
        await voz.disconnect()
    else:
        print('[!] No se esta reproduciendo nada')
        await ctx.send('[!] No se esta reproduciendo nada, no seas ortiva y pone algo :D ')

#Siguiente cancion
def next_song(ctx):
        if len(lista) > 1 :
            lista.pop(0)
            i = lista[0]
            #Borra Song.mp3 si existe
            cancion_activa = os.path.isfile('song.mp3')
            try:
                if cancion_activa:
                    os.remove('song.mp3')
            except PermissionError:
                pass
                return

            #Parametros de descarga
            ydl_op = {
                'format': 'bestaudio/best',
                'quiet' : True,
                'postprocessor': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality':'192',
                }],
            }

            voz = get(bot.voice_clients, guild=ctx.guild)

            #Descarga
            with youtube_dl.YoutubeDL(ydl_op) as ydl:
                print('[+] Descargando cancion')
                ydl.download([i])
            #Renombra la descarga a Song.mp3
            for file in os.listdir('./'):
                if file.endswith('.m4a') or file.endswith('.webm') or file.endswith('.mp3'):
                    name = file
                    print(f'[+] Renombrando Archivo: {file}')
                    os.rename(file,"song.mp3")
            #Play
            voz.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: next_song(ctx))
            voz.source = discord.PCMVolumeTransformer(voz.source)
            voz.source.volume = 0.8
        else:
            lista.clear()
            print('[!] La lista terminó.')


#Reproducir lista
@bot.command()
async def play(ctx, *, search):
    #Conecta al bot en el canal que lo llaman
    canal = ctx.message.author.voice.channel
    if not canal:
        await ctx.send('[-]No estas conectado a un canal de voz :(')
        return
    voz = get(bot.voice_clients,guild=ctx.guild)
    if voz and voz.is_connected():
        await voz.move_to(canal)
    else:
        voz = await canal.connect()
    #Lee lo que escribe el usuario y genera una url de busqueda
    query_string = parse.urlencode({"search_query": search})
    html_content = request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall( r"watch\?v=(\S{11})", html_content.read().decode())
    #url de respeusta
    url = "https://www.youtube.com/watch?v=" + search_results[0]

    #Parametros de descarga
    ydl_op = {
        'format': 'bestaudio/best',
        'quiet' : True,
        'postprocessor': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality':'192',
        }],
    }

    #Verifica si la lista tiene elementos
    if len(lista) != 0 :
        lista.append(url)
        print(lista)
        await ctx.send(f'[+] Se agrego "{search}" a la lista!')
    else:
        lista.append(url)
        #Elimina song.mp3, si existe
        cancion_activa = os.path.isfile('song.mp3')
        try:
            if cancion_activa:
                os.remove('song.mp3')
        except PermissionError:
            await ctx.send('[-] Ya hay una cancion reproduciendose!')
            return
        await ctx.send('[+] Todo listo, espera un toque :D')
        await ctx.send('[¡!] Si no inicia, proba desconectar al bot del server, y volve a intentar! ')

        voz = get(bot.voice_clients, guild=ctx.guild)
        #Descarga
        with youtube_dl.YoutubeDL(ydl_op) as ydl:
            print('[+] Descargando cancion')
            ydl.download([url])
        #Renombra la descarga a song.mp3
        for file in os.listdir('./'):
            if file.endswith('.m4a') or file.endswith('.webm') or file.endswith('.mp3'):
                name = file
                print(f'[+] Renombrando Archivo: {file}')
                os.rename(file,"song.mp3")
        #Play
        voz.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: next_song(ctx))
        voz.source = discord.PCMVolumeTransformer(voz.source)
        voz.source.volume = 0.8
        nombre_cancion = name.rsplit('-',2)
        await ctx.send(f'[+] Reproduciendo: {nombre_cancion[0]}')

#Next
@bot.command(pass_context = True)
async def next(ctx):
    voz = get(bot.voice_clients, guild=ctx.guild)
    if voz and voz.is_playing():
        print('[!] Musica detenida')
        voz.stop()
        await ctx.send('[+] Cambiando tema..')
        if len(lista) == 0:
            await ctx.send('[!] Ya no hay mas canciones en la lista :C')
    else:
        print('[!] No se esta reproduciendo nada')
        await ctx.send('[!] No se esta reproduciendo nada, no seas ortiva y pone algo :D ')

bot.run("ODcxNDY3OTg1NDk0MjI0OTA3.YQbvzg.M2m60QhMUz9pEVqNKFECTSB9_Fg")
