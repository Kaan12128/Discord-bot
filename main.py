import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- 1. KISIM: SAHTE WEB SİTESİ (HİLE KISMI) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Calisiyor! Ben buradayim."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KISIM: SENİN BOT KODLARIN ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

IZINLI_ROL = "Tier Yöneticisi"
TIER_LIST = ["LT5", "LT4", "LT3", "LT2", "LT1", "HT5", "HT4", "HT3", "HT2", "HT1"]
OYUN_MODLARI = {
    "nethpot": "⚫🗡️", "sword": "💎⚔️", "crystal": "🔮💣",
    "uhc": "🍎🏹", "axe": "🪓🛡️", "smp": "🌲⛏️", "genel": "🎮"
}

@bot.event
async def on_ready():
    print(f'{bot.user} aktif!')

@bot.command()
@commands.has_role(IZINLI_ROL)
async def terfi(ctx, member: discord.Member, mod: str = "genel"):
    mod = mod.lower()
    if mod not in OYUN_MODLARI:
        await ctx.send(f"⚠️ Mod bulunamadı. Geçerli: {', '.join(OYUN_MODLARI.keys())}")
        return
    current_tier_index = -1
    for role in member.roles:
        if role.name in TIER_LIST:
            current_tier_index = TIER_LIST.index(role.name)
            break
    new_role_name = ""
    if current_tier_index == -1: new_role_name = TIER_LIST[0]
    elif current_tier_index < len(TIER_LIST) - 1:
        new_role_name = TIER_LIST[current_tier_index + 1]
        old_role = discord.utils.get(ctx.guild.roles, name=TIER_LIST[current_tier_index])
        if old_role: await member.remove_roles(old_role)
    else: new_role_name = TIER_LIST[-1]

    new_role = discord.utils.get(ctx.guild.roles, name=new_role_name)
    if new_role:
        if new_role not in member.roles: await member.add_roles(new_role)
        emoji = OYUN_MODLARI[mod]
        try:
            yeni_nick = f"{emoji} [{new_role_name}] {member.name}"
            await member.edit(nick=yeni_nick)
            await ctx.send(f"✅ {member.mention} terfi etti! Rol: **{new_role_name}**")
        except: await ctx.send(f"✅ Terfi verildi (İsim değiştirilemedi).")
    else: await ctx.send(f"Hata: **{new_role_name}** rolü yok!")

@bot.command()
@commands.has_role(IZINLI_ROL)
async def macsonu(ctx, member: discord.Member, mc_name: str, yeni_tier: str, skor: str, kazanan: str):
    if member.display_name.lower() in kazanan.lower() or member.name.lower() in kazanan.lower():
        color = discord.Color.green(); durum = "🏆 ZAFER"
    else: color = discord.Color.red(); durum = "💀 MAĞLUBİYET"

    eski_tier = "Yok"
    for role in member.roles:
        if role.name in TIER_LIST:
            eski_tier = role.name
            await member.remove_roles(role)
            break
    yeni_tier = yeni_tier.upper()
    if yeni_tier in TIER_LIST:
        nr = discord.utils.get(ctx.guild.roles, name=yeni_tier)
        if nr: await member.add_roles(nr)

    embed = discord.Embed(title=f"{durum} - Tier Maçı", description=f"**{member.mention}**", color=color)
    embed.set_thumbnail(url=f"https://minotar.net/armor/body/{mc_name}/150.png")
    embed.set_author(name=mc_name, icon_url=f"https://minotar.net/helm/{mc_name}/100.png")
    embed.add_field(name="📉 Eski", value=eski_tier, inline=True)
    embed.add_field(name="📈 Yeni", value=yeni_tier, inline=True)
    embed.add_field(name="📊 Skor", value=skor, inline=True)
    embed.add_field(name="🏅 Kazanan", value=kazanan, inline=True)
    await ctx.send(embed=embed)

# --- 3. KISIM: BAŞLATMA ---
keep_alive() # Önce web sitesini başlat
token = os.environ.get("DISCORD_TOKEN")
if token: bot.run(token)
