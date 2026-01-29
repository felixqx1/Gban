import discord
from discord import app_commands
from discord.ext import commands
import discordoauth2
import dotenv
import os
import json
import time
import datetime
import subprocess
import threading


dotenv.load_dotenv(".env")


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="g!", intents=intents)
tree = bot.tree

def run_web():
    subprocess.Popen(["python3", "web.py"])

thread = threading.Thread(target=run_web, daemon=True)
# start the web subprocess and run the bot only when executed as the main script

client = discordoauth2.Client(1464978953981788242, os.environ['OAUTH_TOKEN'], "http://localhost:8080/auth")

def verify_user(uid: int):
    f = open('auth.json',)
    auth = json.load(f)
    f.close()
    auth = str.split(auth[uid], ',')
    access = client.from_access_token(auth[0])
    f = open('user_info.json',)
    data = json.load(f)
    f.close()
    conns = []
    for i in access.fetch_connections():
        conns.append(f"{i['type']};{i['id']}")
    data[uid] = conns
    f = open('user_info.json', 'w')
    json.dump(data, f)
    f.close()

async def gban_ban(uid: discord.User, reason: str):
        f = open('bans.json',)
        data = json.load(f)
        f.close()

        data[str(uid.id)] = f"{reason}"

        f = open('bans.json', 'w')
        json.dump(data, f)
        f.close()

        f = open('user_info.json',)
        data = json.load(f)
        f.close()


        guilds = [guild.id for guild in bot.guilds]
        for gid in guilds:
            guild = bot.get_guild(gid)
            time.sleep(1)
            await(guild.ban(user=uid, reason=f"baned by the global ban system for the reason of: {reason}"))
        print(f"checking for shared accounts with {uid}({uid.id})")

        if data[str(uid.id)]:
            for k,v in data.items():
                print(f"checking {k} for shared accounts...")
                for conn in v:
                    for conn1 in data[str(uid.id)]:
                        if conn == conn1:
                            time.sleep(1)
                            user = await bot.fetch_user(int(k))
                            for gid in guilds:
                                guild = bot.get_guild(gid)
                                time.sleep(1)
                                await guild.ban(user=user, reason=f"baned by the global ban system for the reason of: {reason} (note: this is a enforcment ban due to shared account info with a gbaned user)")


@tree.command(name="gban", description="globaly bans a uid")
@app_commands.describe(uid="The uid/user to Gban")
@app_commands.describe(reason="the reason for the ban")
@app_commands.describe(proof="proof for the ban")
async def gban(interaction: discord.Interaction, uid: discord.User, reason: str, proof: discord.Attachment):
    if interaction.user.id == 975744322551054346:
        await interaction.response.send_message(f"baning {uid}({uid.id})...")
        await gban_ban(uid, reason)
        await interaction.followup.send(f"baned {uid}({uid.id}) for the reason of: {reason}\nproof: {proof.url}")
    elif interaction.user.id == 1379222794516172831:
        await interaction.response.send_message("dont even try it bitch :D")
    else:
        await interaction.response.send_message("You do not have permission to use this command.")

@tree.command(name="ungban", description="globaly unbans a uid")
@app_commands.describe(uid="The uid/user to Ungban")
@app_commands.describe(reason="the reason for the unban")
async def ungban(interaction: discord.Interaction, uid: discord.User, reason: str) -> None:
    if interaction.user.id == 975744322551054346:
        await interaction.response.send_message(f"unbaning {uid}({uid.id})...")
        f = open('bans.json',)
        data = json.load(f)
        f.close()
        if str(uid.id) in data:
            data.pop(str(uid.id))
            f = open('bans.json', 'w')
            json.dump(data, f)
            f.close()
            guilds = [guild.id for guild in bot.guilds]
            for gid in guilds:
                time.sleep(1)
                guild = bot.get_guild(gid)
                await(guild.unban(user=uid, reason=f"unbaned by global ban system for the reason of: {reason} (note we will nerver unban someone that was not banned by us)"))
        else:
            await interaction.followup.send(f"{uid} is not gbaned")
    elif interaction.user.id == 1379222794516172831:
        await interaction.response.send_message("dont even try it bitch :D")
    else:
        await interaction.response.send_message("You do not have permission to use this command.")

@tree.command(name="gban-list", description="gets the global ban list")
async def gban_list(ctx: discord.Interaction) -> None:
    embed = discord.Embed(
        title="global ban list",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    f = open('bans.json',)
    data = json.load(f)
    f.close()
    for uid in data:
        user = await bot.fetch_user(int(uid))
        embed.add_field(name=f"{user.name}({user.id})", value=data[uid], inline=False)
    await ctx.response.send_message(embed=embed)

@tree.command(name="verify-setup", description="sets up the verification system")
@app_commands.describe(channel="The channel to send the verification message in")
@app_commands.describe(role="The role to assign to verified users")
@commands.has_permissions(manage_guild=True)
async def verify_setup(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    embed = discord.Embed(
        title="Verification",
        description="Click the button below to verify yourself and gain access to the server!",
        color=discord.Color.green(),
    )
    #class VerifyButton(discord.ui.View):
      #  @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
        #async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

    #await channel.send(embed=embed, view=VerifyButton())
    #await interaction.response.send_message(f"Verification setup complete in {channel.mention} with role {role.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print("syncing....")
    await(tree.sync())
    print(f"bot {bot.user.name} is ready")
    f = open('bans.json',)
    data = json.load(f)
    f.close()
    guilds = [guild.id for guild in bot.guilds]
    for gid in guilds:
        guild = bot.get_guild(gid)
        for uid in data:
            print(f"banning {uid} in guild {guild.name}({guild.id})")
            user = await bot.fetch_user(int(uid))
            await(guild.ban(user=user, reason=f"baned by the global ban system for the reason of: {data[uid]}"))
            time.sleep(1)

@bot.event
async def on_guild_join(guild):
    print(f"joined guild: {guild.name}({guild.id})")
    f = open('bans.json',)
    data = json.load(f)
    f.close()
    for uid in data:
        print(f"banning {uid} in guild {guild.name}({guild.id})")
        user = await bot.fetch_user(int(uid))
        await(guild.ban(user=user, reason=f"baned by the global ban system for the reason of: {data[uid]}"))
        await(time.sleep(0.3))


if __name__ == "__main__":
    thread.start()
    bot.run(os.environ.get("TOKEN"))