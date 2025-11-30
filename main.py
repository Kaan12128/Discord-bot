import discord
from discord.ext import commands
import os  # Render'dan Token çekmek için gerekli

# --- AYARLAR ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Yetkili Rol Adı
IZINLI_ROL = "Tier Yöneticisi"

# Tier Listesi (Küçükten Büyüğe)
TIER_LIST = ["LT5", "LT4", "LT3", "LT2", "LT1", "HT5", "HT4", "HT3", "HT2", "HT1"]

# Oyun Modları ve Emojileri
OYUN_MODLARI = {
    "nethpot": "⚫🗡️",
    "sword": "💎⚔️",
    "crystal": "🔮💣",
    "uhc": "🍎🏹",
    "axe": "🪓🛡️",
    "smp": "🌲⛏️",
    "genel": "🎮"
}

# Bot Hazır Olduğunda
@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')
    print('Bot şu an aktif ve komut bekliyor.')

# --- KOMUT 1: TIER YÜKSELTME VE İSİM DEĞİŞTİRME ---
@bot.command()
@commands.has_role(IZINLI_ROL)
async def terfi(ctx, member: discord.Member, mod: str = "genel"):
    mod = mod.lower()
    
    if mod not in OYUN_MODLARI:
        await ctx.send(f"⚠️ **{mod}** diye bir mod bulunamadı! Geçerli modlar: {', '.join(OYUN_MODLARI.keys())}")
        return

    current_tier_index = -1
    for role in member.roles:
        if role.name in TIER_LIST:
            current_tier_index = TIER_LIST.index(role.name)
            break
    
    new_role_name = ""
    if current_tier_index == -1:
        new_role_name = TIER_LIST[0]
    elif current_tier_index < len(TIER_LIST) - 1:
        new_role_name = TIER_LIST[current_tier_index + 1]
        old_role = discord.utils.get(ctx.guild.roles, name=TIER_LIST[current_tier_index])
        if old_role:
            await member.remove_roles(old_role)
    else:
        new_role_name = TIER_LIST[-1]

    new_role = discord.utils.get(ctx.guild.roles, name=new_role_name)
    if new_role:
        if new_role not in member.roles:
            await member.add_roles(new_role)
        
        # İsim Değiştirme
        emoji = OYUN_MODLARI[mod]
        try:
            yeni_nick = f"{emoji} [{new_role_name}] {member.name}"
            await member.edit(nick=yeni_nick)
            await ctx.send(f"✅ {member.mention} terfi etti! \n**Rol:** {new_role_name}\n**Yeni İsim:** `{yeni_nick}`")
        except discord.Forbidden:
            await ctx.send(f"✅ Terfi verildi ama yetkim yetmediği için ismini değiştiremedim.")
    else:
        await ctx.send(f"Hata: **{new_role_name}** rolü sunucuda yok!")

# --- KOMUT 2: MAÇ SONUCU VE İSTATİSTİK KARTI ---
@bot.command()
@commands.has_role(IZINLI_ROL)
async def macsonu(ctx, member: discord.Member, mc_name: str, yeni_tier: str, skor: str, kazanan: str):
    
    # Renk Ayarı (Kazanan kontrolü)
    if member.display_name.lower() in kazanan.lower() or member.name.lower() in kazanan.lower():
        embed_color = discord.Color.green()
        durum_ikonu = "🏆 ZAFER"
    else:
        embed_color = discord.Color.red()
        durum_ikonu = "💀 MAĞLUBİYET"

    # Tier İşlemleri
    eski_tier = "Yok"
    for role in member.roles:
        if role.name in TIER_LIST:
            eski_tier = role.name
            await member.remove_roles(role)
            break
            
    yeni_tier = yeni_tier.upper()
    if yeni_tier in TIER_LIST:
        new_role_obj = discord.utils.get(ctx.guild.roles, name=yeni_tier)
        if new_role_obj:
            await member.add_roles(new_role_obj)
    
    # Embed Tasarımı
    embed = discord.Embed(
        title=f"{durum_ikonu} - Tier Maçı Sonucu",
        description=f"**{member.mention}** maç detayları:",
        color=embed_color
    )
    skin_body_url = f"https://minotar.net/armor/body/{mc_name}/150.png"
    skin_head_url = f"https://minotar.net/helm/{mc_name}/100.png"
    
    embed.set_thumbnail(url=skin_body_url)
    embed.set_author(name=mc_name, icon_url=skin_head_url)
    embed.add_field(name="📉 Eski Tier", value=f"`{eski_tier}`", inline=True)
    embed.add_field(name="📈 Yeni Tier", value=f"**{yeni_tier}**", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=False) 
    embed.add_field(name="📊 Skor", value=f"**{skor}**", inline=True)
    embed.add_field(name="🏅 Kazanan", value=f"**{kazanan}**", inline=True)
    embed.set_footer(text=f"Onaylayan: {ctx.author.display_name}")

    await ctx.send(embed=embed)

# Hata Yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("⛔ Bu komutu sadece **Tier Yöneticisi** kullanabilir!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❗ Eksik bilgi girdin.")

# Render için Token Çekme
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("HATA: DISCORD_TOKEN bulunamadı! Render Environment Variables ayarlarını kontrol et.")
