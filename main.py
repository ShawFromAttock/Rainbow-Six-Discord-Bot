import discord
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
queue_mentions = []
queue_names = []
used_match_numbers = []
server = ''
max_players = 10
half_players = int(max_players / 2)
global match_number
global host_member
verification_emoji = '👍'
verified_role_name = 'verified'
guild_id = 792025789080010754
verification_message = None
verification_channel_id = 1089865116872347648
allowed_channel_id = 1089880368599015434

map_pool = {
    'Border': "https://liquipedia.net/commons/images/thumb/b/bf/R6S_map_border.jpg/535px-R6S_map_border.jpg",
    'Clubhouse': "https://liquipedia.net/commons/images/thumb/a/ad/R6S_map_clubhouse.jpg/535px-R6S_map_clubhouse.jpg",
    'Chalet': "https://liquipedia.net/commons/images/thumb/1/19/R6S_map_chalet.jpg/535px-R6S_map_chalet.jpg",
    'Bank': "https://liquipedia.net/commons/images/thumb/0/05/R6S_map_bank.jpg/535px-R6S_map_bank.jpg",
    'Kafe': "https://liquipedia.net/commons/images/thumb/f/f2/R6S_map_kafe.jpg/535px-R6S_map_kafe.jpg",
    'Oregon': "https://liquipedia.net/commons/images/thumb/0/02/R6S_map_oregon.jpg/535px-R6S_map_oregon.jpg",
    'Skyscraper': "https://liquipedia.net/commons/images/thumb/c/ce/R6S_map_skyscraper.jpg/535px-R6S_map_skyscraper.jpg",
    'Theme Park': "https://liquipedia.net/commons/images/thumb/1/10/R6S_map_theme_park.jpg/534px-R6S_map_theme_park.jpg",
    'Villa': "https://liquipedia.net/commons/images/thumb/4/4d/R6S_map_villa.jpg/534px-R6S_map_villa.jpg"
}


def in_allowed_channel(ctx):
    return ctx.channel.id == allowed_channel_id


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    guild = bot.get_guild(guild_id)
    channel = guild.get_channel(verification_channel_id)
    if channel is not None:
        global verification_message
        async for message in channel.history():
            if message.author == bot.user and message.embeds and message.embeds[0].title == 'Verification':
                verification_message = message
                break
        else:
            await create_verification_message(channel)
            async for message in channel.history():
                if message.author == bot.user and message.embeds and message.embeds[0].title == 'Verification':
                    verification_message = message
                    break
    else:
        print(f'Could not find verification channel in guild {guild.name}')


@bot.event
async def create_verification_message(channel):
    embed = discord.Embed(title='Verification', description='React with 👍 to get verified', color=0x00ff00)
    message = await channel.send(embed=embed)
    await message.add_reaction(verification_emoji)


@bot.event
async def on_raw_reaction_add(payload):
    if verification_message is not None and payload.message_id == verification_message.id and str(
            payload.emoji) == verification_emoji and not payload.member.bot:
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, name=verified_role_name)
        member = guild.get_member(payload.user_id)
        await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    if payload.message_id == verification_message.id and str(payload.emoji) == verification_emoji:
        member = await guild.fetch_member(payload.user_id)
        if not member.bot:
            role = discord.utils.get(guild.roles, name=verified_role_name)
            await member.remove_roles(role)


@bot.command()
async def j(ctx):
    if ctx.channel.id != allowed_channel_id:
        print("error handled")
    else:
        player_mention = ctx.author.mention
        player_name = ctx.author.name
        for role in ctx.author.roles:
            if role.name.startswith('Team'):
                await ctx.send(f"{ctx.author.mention} you are already in a match.")
                return
        if player_mention in queue_mentions:
            await ctx.send(f'{player_mention} you are already in queue')

        else:
            await ctx.send(f'{player_mention} has joined the queue')
            queue_mentions.append(player_mention)
            queue_names.append(player_name)
            queue_length = len(queue_mentions)
            if queue_length == max_players:
                t1, t2 = await split(ctx)
                await assign_role_to_team1(ctx, t1, t2)
                queue_mentions.clear()
                queue_names.clear()


async def split(ctx):
    random.shuffle(queue_mentions)
    team1 = queue_mentions[:half_players]
    team2 = queue_mentions[half_players:]
    host = random.choice(queue_mentions)
    global host_member
    host_member = ctx.guild.get_member(int(host[2:-1]))
    host_role = discord.utils.get(ctx.guild.roles, name='Match Host')
    await host_member.add_roles(host_role)
    selected_map = random.choice(list(map_pool))
    map_url = map_pool[selected_map]
    embed = discord.Embed(title="The Match is SET!!",
                          color=0xFF5733)
    embed.add_field(name="Map:", value=selected_map,
                    inline=False)
    embed.add_field(name="Host:", value=host,
                    inline=False)
    embed.add_field(name="Team 1:", value='\n'.join(team1),
                    inline=True)
    embed.add_field(name="Team 2:", value='\n'.join(team2),
                    inline=True)
    embed.set_author(name="Fabian.G2",
                     icon_url="https://cdn.shopify.com/s/files/1/0548/8554/8183/files/2022-10-04-Staff_R6_Fabian.jpg?v=1664894229")
    embed.set_thumbnail(url=f"{map_url}")
    embed.set_footer(text="Refer to #match_settings to see the settings of the match.\n"
                          "Refer to the #match_rules to get to know the rules of the game.")
    await ctx.send(embed=embed)
    return team1, team2


async def assign_role_to_team1(ctx, t1, t2):
    global match_number
    match_number = random.randint(1, 50)
    while match_number in used_match_numbers:
        match_number = random.randint(1, 50)
    match_role = await ctx.guild.create_role(name=f'Match {match_number}')
    global host_member
    await host_member.add_roles(match_role)
    role1 = discord.utils.get(ctx.guild.roles, name="Team 1")
    for member in t1:
        member_id = int(member[2:-1])
        member_obj = await ctx.guild.fetch_member(member_id)
        await member_obj.add_roles(role1, match_role)

    role2 = discord.utils.get(ctx.guild.roles, name="Team 2")
    for member in t2:
        member_id = int(member[2:-1])
        member_obj = await ctx.guild.fetch_member(member_id)
        await member_obj.add_roles(role2, match_role)


@bot.command()
async def leave_queue(ctx):
    if ctx.channel.id != allowed_channel_id:
        print("error handled")
    else:
        player_mention = ctx.author.mention
        player_name = ctx.author.name
        if player_mention not in queue_mentions:
            await ctx.send(f'{ctx.author.mention} you are not in queue.')
        else:
            queue_mentions.remove(player_mention)
            queue_names.remove(player_name)
            await ctx.send(f'{ctx.author.mention} has left the queue.')


@bot.command()
async def show_queue(ctx):
    if ctx.channel.id != allowed_channel_id:
        print("error handled")
    else:
        if len(queue_names) == 0:
            embed = discord.Embed(title="**The Queue is empty.**",
                                  color=discord.Color.red())
        else:
            embed = discord.Embed(title="**Current Queue:**",
                                  description='\n'.join(queue_names),
                                  color=discord.Color.green())
        await ctx.send(embed=embed)


@bot.command()
async def conclude(ctx):
    if ctx.channel.id != allowed_channel_id:
        print("error handled")
    else:
        global match_number
        for role in ctx.author.roles:
            if role.name.startswith('Match'):
                match_number = int(role.name.split()[-1])
                break
        team1_role = discord.utils.get(ctx.guild.roles, name='Team 1')
        team2_role = discord.utils.get(ctx.guild.roles, name='Team 2')
        host_role = discord.utils.get(ctx.guild.roles, name='Match Host')
        match_role = discord.utils.get(ctx.guild.roles, name=f'Match {match_number}')
        user_has_host_role = host_role in ctx.author.roles

        if not user_has_host_role:
            await ctx.send(f'{ctx.author.mention} you must be the host of the match to use this command.')
            return

        bot_member = ctx.guild.get_member(bot.user.id)

        async for member in ctx.guild.fetch_members():
            if member == bot_member:
                continue
            if team1_role in member.roles or team2_role in member.roles or host_role in member.roles or match_role in member.roles:
                await member.remove_roles(team1_role, team2_role, host_role, match_role)
        await match_role.delete()
        await ctx.send(f'{ctx.author.mention} your match has concluded.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass
    else:
        await ctx.send(f'An error occurred: {str(error)}')


bot.run('MTA4ODg1MjE0NjYwMDAzNDM3NA.GoZ1nv.PCYFLudXmPbrRku0lSINAoGDerFpE_VkNpWK34')
