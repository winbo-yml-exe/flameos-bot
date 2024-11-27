import nextcord
import time
from nextcord.ext import commands, tasks
import json
import os

intents = nextcord.Intents.all()
flame = commands.Bot(intents=intents, command_prefix="f!")
serverdb = {}

try:
    if not os.path.isfile("serverdb.json"):
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
            print("Created serverdb.json")
    else:
        with open("serverdb.json", "r", encoding="utf-8") as sdbfile:
            serverdb = json.load(sdbfile)
            print("Loaded serverdb.json")
except:
    pass

@flame.event
async def on_ready():
    print(f"Logged on as {flame.user}")

@flame.slash_command(name="ping", description="Pong!")
async def ping(ctx):
    await ctx.send(f"Pong 🏓 {flame.latency * 1000:.2f}ms")

@flame.slash_command(name="echo", description="Echo anything you want (swear words will be reported)")
async def echo(ctx, message: str):
    await ctx.send(message)

@flame.slash_command(name="announce", description="Announce any message (staff only)")
@commands.has_permissions(administrator=True)
async def announce(ctx, message: str):
    await ctx.send(f"@everyone {message}", allowed_mentions=nextcord.AllowedMentions(everyone=True))

@flame.slash_command(name="mute", description="Mutes a user")
async def mute(ctx: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if ctx.user.guild_permissions.manage_roles:
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role is None:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        if mute_role in member.roles:
            await ctx.send(f"{member.mention} is already muted!")
        else:
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"Muted {member.mention} for {reason}")
    else:
        await ctx.send("You do not have permission to mute members.")

@flame.slash_command(name="unmute", description="Unmutes a user")
async def unmute(ctx: nextcord.Interaction, member: nextcord.Member):
    if ctx.user.guild_permissions.manage_roles:
        mute_role = nextcord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.response.send_message(f"Unmuted {member.mention}")
        else:
            await ctx.response.send_message("Member not muted.")
    else:
        await ctx.response.send_message("You do not have permission to unmute members.")

@flame.slash_command(name="ban", description="Bans a user")
async def ban(ctx: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if not ctx.user.guild_permissions.ban_members:
        embed = nextcord.Embed(title="Permission Denied", description="You do not have permission to ban members.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    
    if member == ctx.user:
        embed = nextcord.Embed(title="Invalid Action", description="You cannot ban yourself.", color=nextcord.Color.orange())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    
    if member.top_role >= ctx.user.top_role:
        embed = nextcord.Embed(title="Role Hierarchy Violation", description="You cannot ban a member with an equal or higher role.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        embed = nextcord.Embed(title="User Banned", description=f"Banned {member.mention} for: {reason}", color=nextcord.Color.green())
        await ctx.response.send_message(embed=embed, ephemeral=False)
    except nextcord.Forbidden:
        embed = nextcord.Embed(title="Error", description="I cannot ban this member. They may have a higher role.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
    except nextcord.HTTPException:
        embed = nextcord.Embed(title="Error", description="Failed to ban the member. Please try again later.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)

@flame.slash_command(name="unban", description="Unbans a user")
async def unban(ctx: nextcord.Interaction, member: nextcord.User):
    if not ctx.user.guild_permissions.ban_members:
        embed = nextcord.Embed(title="Permission Denied", description="You do not have permission to unban members.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        await ctx.guild.unban(member)
        embed = nextcord.Embed(title="User Unbanned", description=f"Unbanned {member.mention}.", color=nextcord.Color.green())
        await ctx.response.send_message(embed=embed, ephemeral=False)
    except nextcord.NotFound:
        embed = nextcord.Embed(title="Error", description="This user is not banned.", color=nextcord.Color.orange())
        await ctx.response.send_message(embed=embed, ephemeral=True)
    except nextcord.Forbidden:
        embed = nextcord.Embed(title="Error", description="I cannot unban this user. They may have a higher role.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
    except nextcord.HTTPException:
        embed = nextcord.Embed(title="Error", description="Failed to unban the user. Please try again later.", color=nextcord.Color.red())
        await ctx.response.send_message(embed=embed, ephemeral=True)
    
@flame.slash_command(name="purge", description="Deletes a number of messages")
async def purge(ctx: nextcord.Interaction, amount: int):
    if ctx.user.guild_permissions.manage_messages:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.response.send_message(f"Deleted {len(deleted) - 1} messages.")
    else:
        await ctx.response.send_message("You do not have permission to manage messages.")

@flame.slash_command(name="warn", description="Warns a member")
async def warn(interaction: nextcord.Interaction, member: nextcord.Member, reason: str):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    serverdb[str(interaction.guild.id)]["warns"][str(member.id)].append(reason)
    with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
        json.dump(serverdb, sdbfile, indent=2)
    await interaction.send(f"Warned {member.mention} for {reason}")


@flame.slash_command(name="unwarn", description="Removes a warn from a member")
async def unwarn(interaction: nextcord.Interaction, member: nextcord.Member, warningreason: str):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    if warningreason in serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)].remove(warningreason)
        with open("serverdb.json", "w", encoding="utf-8") as sdbfile:
            json.dump(serverdb, sdbfile, indent=2)
        embed = nextcord.Embed(color=nextcord.Colour.green(), title=f"Removed a warning from {member}", description=f"Removed the warning '{warningreason}' from '{member}'.")
        await interaction.send(embed=embed)
    else:
        embed = nextcord.Embed(color=nextcord.Colour.red(), title="Couldn't find such a warning", description=f"Couldn't find '{warningreason}' in {member}'s warnings.")
        await interaction.send(embed=embed)

@flame.slash_command(name="warns", description="Checks all warns given to a member")
async def warns(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        if serverdb[str(interaction.guild.id)]:
            try:
                if not serverdb[str(interaction.guild.id)]["warns"]:
                    serverdb[str(interaction.guild.id)]["warns"] = {}
                else:
                    pass
            except:
                serverdb[str(interaction.guild.id)]["warns"] = {}
        else:
            serverdb[str(interaction.guild.id)] = {}
            serverdb[str(interaction.guild.id)]["warns"] = {}
    except:
        serverdb[str(interaction.guild.id)] = {}
        serverdb[str(interaction.guild.id)]["warns"] = {}
    try:
        if not serverdb[str(interaction.guild.id)]["warns"][str(member.id)]:
            serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        else:
            pass
    except:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
    embed = nextcord.Embed(color=nextcord.Colour.red(), title=f"{member}'s warnings ({len(serverdb[str(interaction.guild.id)]['warns'][str(member.id)])})", description=", ".join(serverdb[str(interaction.guild.id)]['warns'][str(member.id)]))
    await interaction.send(embed=embed)

@flame.slash_command(name="clearwarns", description="Clears all warns given to a member")
async def clearwarns(interaction: nextcord.Interaction, member: nextcord.Member):
    try:
        serverdb[str(interaction.guild.id)]["warns"][str(member.id)] = []
        await interaction.send(f"Cleared all warnings for {member.mention}")
    except:
        await interaction.send(f"{member.mention} has no warnings")

@announce.error
async def announce_error(ctx, error):
    if isinstance(error, nextcord.ext.commands.MissingPermissions):
        await ctx.send("You need admin permissions to do this.")
        time.sleep(3)
        await ctx.message.delete()
    else:
        await ctx.send(f"{ctx.author.mention} An error has occured while running the command.")
        time.sleep(3)
        await ctx.message.delete()

flame.run("TOKEN")
