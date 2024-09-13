import discord
from discord import app_commands

id_do_servidor = 1250949730041856060  # Coloque aqui o ID do seu servidor
canal_beneficios = 1251014963615502359  # ID do canal onde estão os benefícios


class Client(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False  # Para evitar sincronizar os comandos múltiplas vezes
        self.casamentos = {}  # Armazenar os casamentos aqui
        self.pedidos_casamento = {}  # Armazenar pedidos de casamento pendentes

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Entramos como {self.user}.")

    async def on_member_update(self, before: discord.Member,
                               after: discord.Member):
        if before.premium_since is None and after.premium_since is not None:
            try:
                await after.send(
                    f'Obrigado por impulsionar o servidor Draconic Hunters! Veja os benefícios em <#{canal_beneficios}>'
                )
            except discord.Forbidden:
                pass  # Ignorar falhas ao enviar mensagens

    async def on_message(self, message: discord.Message):
        if message.author.id in self.pedidos_casamento:
            pedido = self.pedidos_casamento[message.author.id]
            if message.content == '2':
                usuario1 = message.author
                usuario2 = pedido['usuario']
                self.casamentos[usuario1.id] = usuario2.id
                self.casamentos[usuario2.id] = usuario1.id
                self.pedidos_casamento.pop(usuario1.id, None)

                await usuario2.send(
                    f'{usuario1.mention} aceitou o pedido de casamento!')
                await usuario1.send(
                    f'Você e {usuario2.mention} agora estão casados para sempre!'
                )
            else:
                self.pedidos_casamento.pop(message.author.id, None)
                await message.author.send(
                    'Seu pedido de casamento foi recusado.')

            await message.delete()


aclient = Client()
tree = app_commands.CommandTree(aclient)


# Comando de teste
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='teste',
              description='Testando')
async def slash2(interaction: discord.Interaction):
    await interaction.response.send_message("Estou funcionando!",
                                            ephemeral=True)


# Comando de kick
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='kick',
              description='Expulsar um usuário do servidor')
async def kick(interaction: discord.Interaction,
               membro: discord.Member,
               motivo: str = 'Nenhum motivo fornecido'):
    if interaction.user.guild_permissions.kick_members:
        await membro.kick(reason=motivo)
        try:
            await membro.send(
                f'Você foi expulso do servidor {interaction.guild.name}. Motivo: {motivo}'
            )
        except discord.Forbidden:
            pass
        await interaction.response.send_message(
            f'{membro} foi expulso por: {motivo}.', ephemeral=True)
    else:
        await interaction.response.send_message(
            'Você não tem permissão para usar este comando.', ephemeral=True)


# Comando de ban
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='ban',
              description='Banir um usuário do servidor')
async def ban(interaction: discord.Interaction,
              membro: discord.Member,
              motivo: str = 'Nenhum motivo fornecido'):
    if interaction.user.guild_permissions.ban_members:
        await membro.ban(reason=motivo)
        try:
            await membro.send(
                f'Você foi banido do servidor {interaction.guild.name}. Motivo: {motivo}'
            )
        except discord.Forbidden:
            pass
        await interaction.response.send_message(
            f'{membro} foi banido por: {motivo}.', ephemeral=True)
    else:
        await interaction.response.send_message(
            'Você não tem permissão para usar este comando.', ephemeral=True)


# Comando de unban
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='unban',
              description='Desbanir um usuário do servidor')
async def unban(interaction: discord.Interaction, usuario: str):
    if interaction.user.guild_permissions.ban_members:
        nome, discriminador = usuario.split('#')
        ban_list = await interaction.guild.bans()
        for ban in ban_list:
            if ban.user.name == nome and ban.user.discriminator == discriminador:
                await interaction.guild.unban(ban.user)
                await interaction.response.send_message(
                    f'{usuario} foi desbanido.', ephemeral=True)
                return
        await interaction.response.send_message(
            f'{usuario} não foi encontrado na lista de banidos.',
            ephemeral=True)
    else:
        await interaction.response.send_message(
            'Você não tem permissão para usar este comando.', ephemeral=True)


# Comando de advertência
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='warn',
              description='Advertir um usuário')
async def warn(interaction: discord.Interaction,
               membro: discord.Member,
               *,
               motivo: str = 'Nenhum motivo fornecido'):
    if interaction.user.guild_permissions.manage_messages:
        try:
            await membro.send(
                f'Você recebeu uma advertência no servidor {interaction.guild.name}. Motivo: {motivo}'
            )
        except discord.Forbidden:
            pass
        await interaction.response.send_message(
            f'{membro} recebeu uma advertência. Motivo: {motivo}',
            ephemeral=True)
    else:
        await interaction.response.send_message(
            'Você não tem permissão para usar este comando.', ephemeral=True)


# Comando de limpar mensagens
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='clear',
              description='Limpar mensagens de um canal')
async def clear(interaction: discord.Interaction, quantidade: int):
    if interaction.user.guild_permissions.manage_messages:
        await interaction.channel.purge(limit=quantidade)
        await interaction.response.send_message(
            f'{quantidade} mensagens foram limpas.', ephemeral=True)
    else:
        await interaction.response.send_message(
            'Você não tem permissão para usar este comando.', ephemeral=True)


# Comando de informações do servidor
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='info',
              description='Informações do servidor')
async def info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name,
                          description="Informações do servidor",
                          color=discord.Color.blue())
    embed.add_field(name="ID do Servidor", value=guild.id)
    embed.add_field(name="Membros", value=guild.member_count)
    embed.add_field(name="Canais", value=len(guild.channels))
    embed.add_field(name="Criado em",
                    value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"))
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Comando de perfil de usuário
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='perfil',
              description='Informações sobre um usuário')
async def perfil(interaction: discord.Interaction,
                 membro: discord.Member = None):
    membro = membro or interaction.user
    embed = discord.Embed(title=f'Perfil de {membro.name}',
                          description=f'Informações sobre {membro.mention}',
                          color=discord.Color.green())
    embed.add_field(name="ID do Usuário", value=membro.id)
    embed.add_field(name="Data de Criação",
                    value=membro.created_at.strftime("%d/%m/%Y %H:%M:%S"))
    embed.add_field(name="Data de Entrada no Servidor",
                    value=membro.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
    embed.set_thumbnail(url=membro.avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Comando de ajuda
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='ajuda',
              description='Exibe todos os comandos disponíveis')
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Comandos Disponíveis",
        description="Aqui estão os comandos que você pode usar:",
        color=discord.Color.orange())
    embed.add_field(name="/teste", value="Testa o bot", inline=False)
    embed.add_field(name="/kick <membro> [motivo]",
                    value="Expulsa um usuário do servidor",
                    inline=False)
    embed.add_field(name="/ban <membro> [motivo]",
                    value="Bane um usuário do servidor",
                    inline=False)
    embed.add_field(name="/unban <usuário#discriminador>",
                    value="Desbana um usuário do servidor",
                    inline=False)
    embed.add_field(name="/warn <membro> [motivo]",
                    value="Adverte um usuário",
                    inline=False)
    embed.add_field(name="/clear <quantidade>",
                    value="Limpa mensagens de um canal",
                    inline=False)
    embed.add_field(name="/info",
                    value="Mostra informações sobre o servidor",
                    inline=False)
    embed.add_field(name="/perfil [membro]",
                    value="Mostra informações sobre um usuário",
                    inline=False)
    embed.add_field(name="/casar <membro>",
                    value="Envia um pedido de casamento",
                    inline=False)
    embed.add_field(name="/termino",
                    value="Termina um casamento",
                    inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# Comando de casar
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='casar',
              description='Casar com um usuário')
async def casar(interaction: discord.Interaction, usuario: discord.Member):
    if usuario.id == interaction.user.id:
        await interaction.response.send_message(
            'Você não pode casar consigo mesmo.', ephemeral=True)
        return

    if interaction.user.id in aclient.casamentos:
        await interaction.response.send_message(
            'Você já está casado com alguém.', ephemeral=True)
        return

    if usuario.id in aclient.casamentos:
        await interaction.response.send_message(
            f'{usuario.mention} já está casado com alguém.', ephemeral=True)
        return

    try:
        pedido = await usuario.send(
            f'{interaction.user.mention} te convidou para um casamento! Responda com `2` para aceitar ou qualquer outra coisa para recusar.'
        )
        aclient.pedidos_casamento[usuario.id] = {'usuario': interaction.user}
        await interaction.response.send_message(
            f'O pedido de casamento foi enviado para {usuario.mention}.',
            ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            'Não consegui enviar a mensagem para o usuário mencionado. Eles podem ter bloqueado o bot.',
            ephemeral=True)


# Comando de término de casamento
@tree.command(guild=discord.Object(id=id_do_servidor),
              name='termino',
              description='Terminar um casamento')
async def termino(interaction: discord.Interaction):
    if interaction.user.id not in aclient.casamentos:
        await interaction.response.send_message(
            'Você não está casado com ninguém.', ephemeral=True)
        return

    parceiro_id = aclient.casamentos.pop(interaction.user.id)
    aclient.casamentos.pop(parceiro_id, None)
    parceiro = interaction.guild.get_member(parceiro_id)

    if parceiro:
        await parceiro.send(
            f'O seu casamento com {interaction.user.mention} foi terminado.')

    await interaction.response.send_message(
        f'Você e {parceiro.mention} terminaram o casamento.', ephemeral=True)


aclient.run(
    '')

