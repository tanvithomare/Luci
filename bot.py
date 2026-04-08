from tkinter.ttk import Button

import discord
from discord.ext import commands
import os
import random
import socket
from dotenv import load_dotenv
from flask.views import View


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True  
intents.guilds = True
bot = commands.Bot(command_prefix='::', intents=intents)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
async def check_connectivity():
    """Test basic network connectivity"""
    print("🔍 Checking network connectivity...")
    
    # Test DNS resolution
    try:
        ip = socket.gethostbyname("discord.com")
        print(f"✅ DNS resolution working: discord.com → {ip}")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # Test basic connectivity
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com", timeout=5) as resp:
                print(f"✅ HTTP connection working (status: {resp.status})")
    except Exception as e:
        print(f"❌ HTTP connection failed: {e}")
        return False
    
    return True
#Channel IDs and Role IDs 
CHANNELS = {
    'rules': 1466886910109679688,   # Channel ID for rules
    'roles': 1466887593978364038,   # Channel ID for roles
    'tickets': 1480293022746017812, # Channel ID for tickets
    'welcome': 1480988688308506664, # Channel ID for welcome messages
    'ticket_category': 1481105087312171290, # Category ID for ticket channels
    'logs': 1481073417888338090, # Channel ID for logs
    'verify': 1466886987884789864, # Channel ID for verification 
    'colors': 1466887154197205033, # Channel ID for colors
}
EMOJI_TO_ROLE = {
    #Gender
    '♂️':[1466889269644890125],
    '♀️':[1466889473793982639],
    '🤔':[1466889656095211582],
    #Agegroups
    '👶':[1466889702580686995],
    '👦':[1466889816946905278],
    '👴':[1480618276697411685],
    '💀':[1480618334453104650],
    #Location
    '🗽':[1466972826593525894], #NA
    '🦜':[1466973010362765598], #SA
    '🐘':[1466973599268081766], #AFR
    '🐼':[1466973337296306340], #APAC
    '🏰':[1466972954771587152], #EU
    #StudyStatus
    '💼':[1480620636736065619], #Employed
    '🙅‍♂️':[1480621044778926121], #Not Employed
    '🧑‍🎓':[1480620945356886047], #Student
    #Majors/Jobs
    '♻️':[1480622215253983555], #AGR ENV 
    '🏥':[1480622348397838531], #Healthcare
    '🏛️':[1480622728229945531], #POLISCI
    '💼':[1480622835104878775], #Business
    '⚛️':[1480623169386709052], #Physical sciences
    '💻':[1480623659159916714], #Computer science
    '📚':[1480623812499345570], #Education
    '🛠️':[1480624107312779344], #Trade
    #Interests
    '🎮':[1480624410424197632], #Gaming
    '🎨':[1480987593662267532], #Art
    '🌱':[1480624953245176004], #Gardening
    '🍳':[1480625044139806771], #Cooking
    '🏋️':[1480625199740092508], #Gym
    '📚':[1480988137248391188], #Reading
        #DM Status
    '✅':[1481818544000864276], #DMs Open
    '❓':[1481818649160319006], #Ask to DM
    '❌':[1481818701031276797], #DMs Closed
    #Colors
    '🔴':[1491477305871302747], #Red
    '🟢':[1491479570644340857], #Green
    '🔵':[1491477612953079949], #Blue
    '🟡':[1491477686152073226], #Yellow
    '🟣':[1491477817819660379], #Purple
    '⚫':[1491478749978562743], #Black
    '⚪':[1491478853149921439], #White
    '🟤':[1491478914554531850], #Brown
    '🟠':[1491478666293809332], #Orange
    '🟥':[1491478582248345692], #Pink
}
AUTOASSIGNED_ROLES = [1465861141686390784, 1466883673478402172, 1466884441560453263, 1466884272320155668]
STAFF_ROLES= [1465861085952217211]
def is_staff():
    async def predicate(ctx):
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return False
        
        # Check for staff roles
        for role in ctx.author.roles:
            if role.id in STAFF_ROLES:
                return True
        
        # Check for administrator permission
        if ctx.author.guild_permissions.administrator:
            return True
        
        await ctx.send("❌ You don't have permission to use this command.")
        return False
    return commands.check(predicate)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
@bot.event
async def on_member_join(member):
    """Automatically assign the "Newcomer" role to new members when they join the server."""
    guild = member.guild
    welcome_channel = guild.get_channel(CHANNELS['welcome'])
    if welcome_channel:
        welcome_embed = discord.Embed(
            title=f"Welcome {member.name}!",
            description="We're glad to have you here! Check out our rules and roles channels to get started.",
            color=0x00ff00
        )
        welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await welcome_channel.send(embed=welcome_embed)
        for role_id in AUTOASSIGNED_ROLES:
            role = guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"Assigned {role.name} to {member.display_name}")
                except Exception as e:
                    print(f"Failed to assign {role_id}: {e}")
@bot.event
async def on_raw_reaction_add(payload):
    """Handle reaction add - assign roles"""
    # Ignore bot's own reactions
    if payload.user_id == bot.user.id:
        return

    # Only process reactions in the roles or colors channel
    if payload.channel_id != CHANNELS['roles'] and payload.channel_id != CHANNELS['colors']:
        return

    print(f'\n🔍 Reaction ADDED by user {payload.user_id}')
    print(f'  Emoji: {payload.emoji}')

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        print('  ❌ Guild not found')
        return

    member = guild.get_member(payload.user_id)
    if not member:
        print('  ❌ Member not found')
        return

    # Get the emoji as a string
    emoji_str = str(payload.emoji)
    print(f'  Emoji string: "{emoji_str}"')
    
    # Check if this emoji is in our mapping
    if emoji_str not in EMOJI_TO_ROLE:
        print(f'  ❌ Emoji "{emoji_str}" not found in mapping')
        print(f'  Available emojis: {list(EMOJI_TO_ROLE.keys())}')
        return

    role_data = EMOJI_TO_ROLE[emoji_str]
    print(f'  Found role data: {role_data} (type: {type(role_data)})')
    
    # Handle both list and single integer cases
    if isinstance(role_data, int):
        role_ids = [role_data]
        print(f'  ⚠️ Converted single integer to list: {role_ids}')
    elif isinstance(role_data, list):
        role_ids = role_data
    else:
        print(f'  ❌ Invalid role data type: {type(role_data)}')
        return

    print(f'  Processing role IDs: {role_ids}')

    # Add each role INDIVIDUALLY
    for single_role_id in role_ids:  # Use a different variable name to avoid confusion
        print(f'  Attempting to add role ID: {single_role_id} (type: {type(single_role_id)})')
        
        # Make sure single_role_id is an integer
        if not isinstance(single_role_id, int):
            print(f'  ❌ Role ID is not an integer: {single_role_id}')
            continue
            
        role = guild.get_role(single_role_id)
        if not role:
            print(f'  ❌ Role ID {single_role_id} not found in guild')
            continue

        # Check if member already has the role
        if role in member.roles:
            print(f'  ⏭️ {member.display_name} already has {role.name}')
            continue

        try:
            await member.add_roles(role, reason=f"Reaction role: {emoji_str}")
            print(f'  ✅ Added {role.name} to {member.display_name}')
        except discord.Forbidden:
            print(f'  ❌ Forbidden: Cannot add {role.name} - check role hierarchy')
        except discord.HTTPException as e:
            print(f'  ❌ HTTP Error: {e}')
        except Exception as e:
            print(f'  ❌ Unexpected error: {e}')

@bot.event
async def on_raw_reaction_remove(payload):
    """Handle reaction remove - remove roles"""
    # Only process reactions in the roles or colors channel
    if payload.channel_id != CHANNELS['roles'] and payload.channel_id != CHANNELS['colors']:
        return

    print(f'\n🔍 Reaction REMOVED by user {payload.user_id}')
    print(f'  Emoji: {payload.emoji}')

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        print('  ❌ Guild not found')
        return

    member = guild.get_member(payload.user_id)
    if not member:
        print('  ❌ Member not found')
        return

    # Get the emoji as a string
    emoji_str = str(payload.emoji)
    print(f'  Emoji string: "{emoji_str}"')
    
    # Check if this emoji is in our mapping
    if emoji_str not in EMOJI_TO_ROLE:
        print(f'  ❌ Emoji "{emoji_str}" not found in mapping')
        return

    role_data = EMOJI_TO_ROLE[emoji_str]
    print(f'  Found role data: {role_data} (type: {type(role_data)})')
    
    # Handle both list and single integer cases
    if isinstance(role_data, int):
        role_ids = [role_data]
        print(f'  ⚠️ Converted single integer to list: {role_ids}')
    elif isinstance(role_data, list):
        role_ids = role_data
    else:
        print(f'  ❌ Invalid role data type: {type(role_data)}')
        return

    print(f'  Processing role IDs: {role_ids}')

    # Remove each role INDIVIDUALLY
    for single_role_id in role_ids:  # Use a different variable name
        print(f'  Attempting to remove role ID: {single_role_id} (type: {type(single_role_id)})')
        
        # Make sure single_role_id is an integer
        if not isinstance(single_role_id, int):
            print(f'  ❌ Role ID is not an integer: {single_role_id}')
            continue
            
        role = guild.get_role(single_role_id)
        if not role:
            print(f'  ❌ Role ID {single_role_id} not found in guild')
            continue

        # Check if member has the role
        if role not in member.roles:
            print(f'  ⏭️ {member.display_name} does not have {role.name}')
            continue

        try:
            await member.remove_roles(role, reason=f"Reaction removed: {emoji_str}")
            print(f'  ✅ Removed {role.name} from {member.display_name}')
        except discord.Forbidden:
            print(f'  ❌ Forbidden: Cannot remove {role.name} - check permissions')
        except discord.HTTPException as e:
            print(f'  ❌ HTTP Error: {e}')
        except Exception as e:
            print(f'  ❌ Unexpected error: {e}')

@bot.command()
@is_staff()
async def rules(ctx):
    channel = bot.get_channel(CHANNELS['rules'])
    if channel:
        top_banner_path = os.path.join(ASSETS_DIR, 'Rules.png')
        if os.path.exists(top_banner_path):
            try:
                # Create a file object from local image
                with open(top_banner_path, 'rb') as f:
                    picture = discord.File(f, filename='Rules.png')
                
                # Create embed with local file as image
                top_banner_embed = discord.Embed(color=0x0099ff)
                top_banner_embed.set_image(url="attachment://Rules.png")
                await channel.send(file=picture, embed=top_banner_embed)
            except Exception as e:
                print(f"Error sending top banner: {e}")
                await channel.send("Failed to load banner image.")
        embed = discord.Embed(
            title="📜 Server Rules",
            description="Please follow these rules to keep our community safe and friendly:",
            color=0x0099ff
        )
        embed.add_field(name="1️⃣ Be Respectful", value="Treat everyone with respect and kindness.", inline=False)
        embed.add_field(name="2️⃣ No Spam", value="Avoid excessive messages or advertisements.", inline=False)
        embed.add_field(name="3️⃣ No Hate Speech", value="Zero tolerance for hate or discrimination.", inline=False)
        embed.add_field(name="4️⃣ Follow Discord TOS", value="Abide by Discord's terms of service.", inline=False)
        embed.add_field(name="5️⃣ Keep it SFW", value="No NSFW content in any chats", inline=False)
        embed.add_field(name="6️⃣ No Self-Promotion", value="No advertising without permission.", inline=False)
        embed.set_footer(text="Violations may result in warnings or bans. Thank you for being part of our community!")
        
        await channel.send(embed=embed)
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        embed.add_field(name="1️⃣ Warning", value="Mods may give you a verbal warning.", inline=False)
        embed.add_field(name="2️⃣ Mute", value="You may be muted for a set period of time if mods do not see you complying.", inline=False)
        embed.add_field(name="4️⃣ Ban", value="Repeated violations or severe offenses may lead to a ban.", inline=False)
        embed.set_footer(text="Please adhere to the rules to maintain a positive community environment.")
    else:
        await ctx.send("Rules channel not found.")

@bot.command()
@is_staff()
async def roles(ctx):
    channel = bot.get_channel(CHANNELS['roles'])
    if channel:
        roles_banner = os.path.join(ASSETS_DIR, 'Roles.png')
        if os.path.exists(roles_banner):
            try:
                # Create a file object from local image
                with open(roles_banner, 'rb') as f:
                    picture = discord.File(f, filename='Roles.png')
                
                # Create embed with local file as image
                roles_banner = discord.Embed(color=0x0099ff)
                roles_banner.set_image(url="attachment://Roles.png")
                await channel.send(file=picture, embed=roles_banner)
            except Exception as e:
                print(f"Error sending top banner: {e}")
                await channel.send("Failed to load banner image.")
        main_embed = discord.Embed(
            title="🎭 Reaction Roles",
            description="React to the messages below to get roles based on your interests and info!\n\n**Click on any reaction to add/remove roles.**",
            color=0x00ff99
        )
        main_embed.add_field(name="How it works", value="1️⃣ Find the section you want\n2️⃣ React with the corresponding emoji\n3️⃣ Roles will be automatically assigned!", inline=False)
        main_embed.set_footer(text="You can add or remove roles at any time by clicking the reactions.")
        await channel.send(embed=main_embed)
        
        # Age Section Banner
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        
        # Age/Gender Section
        age_embed = discord.Embed(
            title="👤 Age & Gender",
            description="Select your age group and gender identity:",
            color=0xff69b4
        )
        age_embed.add_field(name="♂️ Male", value="Male gender role", inline=True)
        age_embed.add_field(name="♀️ Female", value="Female gender role", inline=True)
        age_embed.add_field(name="👶 18-20", value="Young role", inline=True)
        age_embed.add_field(name="👦 21-24", value="Young adult role", inline=True)
        age_embed.add_field(name="👴 25-30", value="Adult role", inline=True)
        age_embed.add_field(name="💀 30+", value="Unc Status role", inline=True)
        age_message = await channel.send(embed=age_embed)
        
        # Add age/gender reactions
        age_emojis = ['♂️', '♀️', '👶', '👦', '👴', '💀']
        for emoji in age_emojis:
            await age_message.add_reaction(emoji)
        
        # Location Section Banner
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        
        # Location Section
        location_embed = discord.Embed(
            title="🌍 Location",
            description="Select your geographical region:",
            color=0x00ff00
        )
        location_embed.add_field(name="🗽 North America", value="USA, Canada, Mexico", inline=True)
        location_embed.add_field(name="🦜 South America", value="Brazil, Argentina, etc.", inline=True)
        location_embed.add_field(name="🐘 Africa", value="All African countries", inline=True)
        location_embed.add_field(name="🐼 Asia-Pacific", value="Japan, Australia, etc.", inline=True)
        location_embed.add_field(name="🏰 Europe", value="EU and UK", inline=True)
        location_message = await channel.send(embed=location_embed)
        
        # Add location reactions
        location_emojis = ['🗽', '🦜', '🐘', '🐼', '🏰']
        for emoji in location_emojis:
            await location_message.add_reaction(emoji)
        
        # Employment Section Banner
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        
        # Employment/Education Section
        employment_embed = discord.Embed(
            title="💼 Employment & Education",
            description="Select your current status:",
            color=0xffaa00
        )
        employment_embed.add_field(name="💼 Employed", value="Currently working (includes Business role)", inline=True)
        employment_embed.add_field(name="🙅‍♂️ Not Employed", value="Currently not working", inline=True)
        employment_embed.add_field(name="🧑‍🎓 Student", value="Currently studying (includes Education role)", inline=True)
        employment_message = await channel.send(embed=employment_embed)
        
        # Add employment reactions
        employment_emojis = ['💼', '🙅‍♂️', '🧑‍🎓']
        for emoji in employment_emojis:
            await employment_message.add_reaction(emoji)
        
        # Industry Section Banner
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        
        # Industry/Interest Section
        industry_embed = discord.Embed(
            title="🔧 Industry & Interests",
            description="Select your field of work or interest:",
            color=0xaa00ff
        )
        industry_embed.add_field(name="♻️ Agriculture/Environment", value="Farming, environmental science", inline=True)
        industry_embed.add_field(name="🏥 Healthcare", value="Medical, nursing, health services", inline=True)
        industry_embed.add_field(name="🏛️ Political Science", value="Politics, government, law", inline=True)
        industry_embed.add_field(name="⚛️ Physical Sciences", value="Physics, chemistry, astronomy", inline=True)
        industry_embed.add_field(name="💻 Computer Science", value="Programming, IT, software", inline=True)
        industry_embed.add_field(name="📚 Education", value="Teaching, academia", inline=True)
        industry_embed.add_field(name="🛠️ Trade", value="Construction, electrical, plumbing", inline=True)
        industry_message = await channel.send(embed=industry_embed)
        
        # Add industry reactions
        industry_emojis = ['♻️', '🏥', '🏛️', '⚛️', '💻', '📚', '🛠️']
        for emoji in industry_emojis:
            await industry_message.add_reaction(emoji)

        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        
        # Interest Section
        interest_embed = discord.Embed(
            title=" Hobbies & Interests",
            description="Select your hobbies:",
            color=0xaa00ff
        )
        interest_embed.add_field(name="🎮 Gaming", value= "Video, console gaming" , inline=True)
        interest_embed.add_field(name="🎨 Art", value="Drawing, painting, sculpture", inline=True)
        interest_embed.add_field(name="🌱 Gardening", value="Planting, tending to gardens", inline=True)
        interest_embed.add_field(name="🍳 Cooking", value="Any chefs in the making", inline=True)
        interest_embed.add_field(name="🏋️Gym", value="Working out", inline=True)
        interest_embed.add_field(name="📚 Reading", value="Readers of all genres", inline=True)
        interest_message = await channel.send(embed=interest_embed)
        
        # Add interest reactions
        interest_emojis = ['🎮', '🎨', '🌱', '🍳', '🏋️', '📚']
        for emoji in interest_emojis:
            await interest_message.add_reaction(emoji)
        
        # Interest Section
        between_banner = os.path.join(ASSETS_DIR, 'Between.png')
        if os.path.exists(between_banner):
            try:
                # Create a file object from local image
                with open(between_banner, 'rb') as f:
                    picture = discord.File(f, filename='Between.png')
                
                # Create embed with local file as image
                between_banner = discord.Embed(color=0x0099ff)
                between_banner.set_image(url="attachment://Between.png")
                await channel.send(file=picture, embed=between_banner)
            except Exception as e:
                print(f"Error sending between banner: {e}")
                await channel.send("Failed to load banner image.")
        dms_embed = discord.Embed(
            title=" DM Status",
            description="Select your DM preferences:",
            color=0xaa00ff
        )
        dms_embed.add_field(name="✅ DMs Open", value="I want to receive direct messages", inline=True)
        dms_embed.add_field(name="❓ Ask to Dm", value="I prefer not to receive direct messages without permission", inline=True)
        dms_embed.add_field(name="❌ DMs Closed", value="I prefer not to receive direct messages", inline=True)
        dms_message = await channel.send(embed=dms_embed)

        # Add DM reactions
        dms_emojis = ['✅', '❌' ,'❓']
        for emoji in dms_emojis:
            await dms_message.add_reaction(emoji)
    else:
        await ctx.send("Roles channel not found.")
@bot.command()
@is_staff()
async def colors(ctx):
    channel = bot.get_channel(CHANNELS['colors'])
    if channel:
        colors_banner = os.path.join(ASSETS_DIR, 'Colors.png')
        if os.path.exists(colors_banner):
            try:
                # Create a file object from local image
                with open(colors_banner, 'rb') as f:
                    picture = discord.File(f, filename='Colors.png')
                
                # Create embed with local file as image
                colors_banner = discord.Embed(color=0x0099ff)
                colors_banner.set_image(url="attachment://Colors.png")
                await channel.send(file=picture, embed=colors_banner)
            except Exception as e:
                print(f"Error sending top banner: {e}")
                await channel.send("Failed to load banner image.")
        colors_embed = discord.Embed(
            title="Color Roles",
            description="Select your preferred color role:",
            color=0x0099ff
        )
        colors_embed.add_field(name="🔴 Red", value="A vibrant red color role.", inline=True)
        colors_embed.add_field(name="🟢 Green", value="A fresh green color role.", inline=True)
        colors_embed.add_field(name="🔵 Blue", value="A calming blue color role.", inline=True)
        colors_embed.add_field(name="🟡 Yellow", value="A bright yellow color role.", inline=True)
        colors_embed.add_field(name="🟣 Purple", value="A royal purple color role.", inline=True)
        colors_embed.add_field(name="⚫ Black", value="A sleek black color role.", inline=True)
        colors_embed.add_field(name="⚪ White", value="A clean white color role.", inline=True)
        colors_embed.add_field(name="🟤 Brown", value="A warm brown color role.", inline=True)
        colors_embed.add_field(name="🟠 Orange", value="A bold orange color role.", inline=True)
        colors_embed.add_field(name="🟥 Pink", value="A soft pink color role.", inline=True)
        await channel.send(embed=colors_embed)
        colors_embed.set_footer(text="You can change your color role at any time by clicking the reactions.")
        colors_emojis = ['🔴', '🟢', '🔵', '🟡', '🟣', '⚫', '⚪', '🟤', '🟠', '🟥']
        for emoji in colors_emojis:
            await channel.last_message.add_reaction(emoji)
    else:
        await ctx.send("Colors channel not found.")

@bot.command()
@is_staff()
async def verify(ctx):
    channel = bot.get_channel(CHANNELS['verify'])
    if channel:
        verify_banner = os.path.join(ASSETS_DIR, 'Verify.png')
        if os.path.exists(verify_banner):
            try:
                # Create a file object from local image
                with open(verify_banner, 'rb') as f:
                    picture = discord.File(f, filename='Verify.png')
                
                # Create embed with local file as image
                verify_banner_embed = discord.Embed(color=0x0099ff)
                verify_banner_embed.set_image(url="attachment://Verify.png")
                await channel.send(file=picture, embed=verify_banner_embed)
            except Exception as e:
                print(f"Error sending verify banner: {e}")
                await channel.send("Failed to load banner image.")
        verify_embed = discord.Embed(
            title="Necessary Materials",
            description="According to Discord and Discord TOS, we are NOT breaking any rules or laws by asking members to age verify. You can simply decline to share this information but will be kicked or banned if suspected to be underage. With that being said, all verification information including pictures will be deleted after the verification process is over.",
            color=0x0099ff
        )
        verify_embed.add_field(name="A Piece of Paper and pen", value="Please have a piece of paper and a pen ready.", inline=False)
        verify_embed.add_field(name="Your ID", value="Please have a valid government-issued ID ready.", inline=False)
        verify_embed.add_field(name="You", value="Please be available to answer any questions during the verification process.", inline=False)
        steps_embed= discord.Embed(
            title="Verification Steps",
            description="1️⃣ Take a clear picture of you with the piece of paper with the server name and the current date written on it. Your face should be visible.\n2️⃣ Take a clear picture of your ID.\n3️⃣ Create a support ticket in #tickets and attach the pictures. A staff member will review your information and verify you if you are 18 or older.",
            color=0x0099ff
        )
        await channel.send(embed=verify_embed)
        await channel.send(embed=steps_embed)
    else:
        await ctx.send("Welcome channel not found.")

@bot.command()
@is_staff()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Delete a specified number of messages"""
    if amount <= 0:
        await ctx.send("Please specify a positive number of messages to delete.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Deleted {len(deleted)-1} messages.", delete_after=3)

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    """Calculate a random compatibility percentage between two users."""
    if user1 == user2:
        await ctx.send("You cannot ship a user with themselves!")
        return
    compatibility = random.randint(0, 100)
    await ctx.send(f"❤️ The compatibility between {user1.mention} and {user2.mention} is **{compatibility}%**! ❤️")
    cooldown = 60  # Cooldown in seconds
    await ctx.send(f"⏳ You can use the ship command again in {cooldown} seconds.")

@bot.command()
@is_staff()
async def reminder(ctx, time: int, *, message: str):
    """Set a reminder that will send a message after a specified number of seconds."""
    await ctx.send(f"⏰ Reminder set for {time} seconds from now!")
    await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=time))
    await ctx.send(f"⏰ Reminder: {message}")
@bot.command()
async def slap(ctx, user: discord.Member):
    """Slap another user with a random image."""
    slap_images = [
        "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
        "https://media.giphy.com/media/mEtSQlxqBtWWA/giphy.gif",
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
        "https://media.giphy.com/media/2M2RtPm8T2kO/giphy.gif"
    ]
    selected_image = random.choice(slap_images)
    embed = discord.Embed(description=f"{ctx.author.mention} slaps {user.mention}!")
    embed.set_image(url=selected_image)
    await ctx.send(embed=embed)
@bot.command()
async def hug(ctx, user: discord.Member):
    """Hug another user with a random image."""
    hug_images = [
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
        "https://media.giphy.com/media/sUIZWMnfd4Mb6/giphy.gif",
        "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif"
    ]
    selected_image = random.choice(hug_images)
    embed = discord.Embed(description=f"{ctx.author.mention} hugs {user.mention}!")
    embed.set_image(url=selected_image)
    await ctx.send(embed=embed)
@bot.command()
async def kiss(ctx, user: discord.Member):
    """Kiss another user with a random image."""
    kiss_images = [
        "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
        "https://media.giphy.com/media/KH1CTZtw1iP3W/giphy.gif",
        "https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif",
        "https://media.giphy.com/media/10zzX8EQZy2u4/giphy.gif",
        "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif"
    ]
    selected_image = random.choice(kiss_images)
    embed = discord.Embed(description=f"{ctx.author.mention} kisses {user.mention}!")
    embed.set_image(url=selected_image)
    await ctx.send(embed=embed)
@bot.command()
async def pat(ctx, user: discord.Member):
    """Pat another user with a random image."""
    pat_images = [
        "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
        "https://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif",
        "https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif",
        "https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif"
    ]
    selected_image = random.choice(pat_images)
    embed = discord.Embed(description=f"{ctx.author.mention} pats {user.mention}!")
    embed.set_image(url=selected_image)
    await ctx.send(embed=embed)
@bot.command()
@is_staff()
async def ban(ctx, user: discord.Member, *, reason=None):
    """Ban a user from the server."""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.")
        return
    try:
        await user.ban(reason=reason)
        await ctx.send(f"✅ {user.mention} has been banned. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Failed to ban {user.mention}. Error: {e}")

bot.run(f"{DISCORD_TOKEN}")
    