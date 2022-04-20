from http.client import HTTPException
from discord.ext.commands import command, Cog, check
from discord import Embed
from ..db import db

CURRENCY_DICT = {
    'Copper': 'CopperAmt',
    'Silver': 'SilverAmt',
    'Brass': 'BrassAmt',
    'Gold': 'GoldAmt',
    'Platinum': 'PlatinumAmt',
    'Electrum': 'ElectrumAmt'
}


def isDm():
    def predicate(ctx):
        dm_record = db.record('SELECT CharacterName FROM bank WHERE IsDm = 1')
        return int(dm_record[0]) == int(ctx.message.author.id)
    return check(predicate)

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='dm')
    async def add_dm(self, ctx, *, message):
        if ctx.message.author.guild_permissions.administrator:
            stripped_user_name = self.strip_user_name(message)
            if self.can_this_happen(stripped_user_name):
                db.execute('UPDATE bank SET IsDm = 1 WHERE CharacterName = ?', stripped_user_name)
                await ctx.send(f'{message} has been made the DM')
        else:
            await ctx.send('Nice try bud')
    
    @command(name='enroll')
    @isDm()
    async def add_user(self, ctx, *, message):
        nick_name = message.split()[1]
        stripped_message = self.strip_user_name(message.split()[0])
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_message))
        if user_exists:
            success_message = "{} already has an account".format(message)
            await ctx.send(success_message)
        else:
            db.execute("INSERT INTO bank VALUES (?,?,?,?,?,?,?,?,?)", 0,stripped_message,nick_name,0,0,0,0,0,0)
            success_message = "{} has opened an account".format(message)
            await ctx.send(success_message)
    
    @command(name='balance')
    async def view_balance(self, ctx, *, message):
        stripped_user_name = self.strip_user_name(message)
        if self.can_this_happen(stripped_user_name):
            user_account = db.record('SELECT * FROM bank WHERE CharacterName = {}'.format(stripped_user_name))
            embed = self.format_balance_embed(user_account)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Please enroll this user first')

    @command(name='deposit')
    @isDm()
    async def deposit_currency(self, ctx, *, message):
        user_name, amount, currency_db, currency = self.currency_formatting(message)
        stripped_user_name = self.strip_user_name(user_name)
        if self.can_this_happen(stripped_user_name):
            self.update_user_bank(currency_db, amount, stripped_user_name, '+')
            success_message = f'Sent {amount} {currency}'
            await ctx.send(success_message)
        else:
            await ctx.send('Please enroll this user first')

    @command(name='loot')
    @isDm()
    async def loot_currency(self, ctx, *, message):
        new_message = "all " + message
        user_name, amount, currency_db, currency = self.currency_formatting(new_message)
        db.execute("UPDATE bank SET {} = {} + ?".format(currency_db, currency_db), amount)
        success_message = f'Sent {amount} {currency} to everyone!'
        await ctx.send(success_message)

    @command(name='withdraw')
    @isDm()
    async def withdraw_currency(self, ctx, *, message):
        user_name, amount, currency_db, currency = self.currency_formatting(message)
        stripped_user_name = self.strip_user_name(user_name)
        if self.can_this_happen(stripped_user_name, currency_db, sub_amount=amount):
            self.update_user_bank(currency_db, amount, stripped_user_name, '-')
            success_message = f'Withdrew {amount} {currency}'
            await ctx.send(success_message)
        else:
            await ctx.send('Either user doesn\'t exist or you\'ll overdraw')

    @command(name='transfer')
    @isDm()
    async def transfer_currency(self, ctx, *, message):
        user_name_1 = message.split()[0]
        user_name_2 = message.split()[1]
        amount = message.split()[2]
        currency = message.split()[3]

        #string compare maybe toLower and select from dict
        currency, currency_db = self.get_database_currency(currency)
        stripped_user_name_1 = self.strip_user_name(user_name_1)
        user_1_names = self.get_user_and_nick_name(stripped_user_name_1)
        stripped_user_name_2 = self.strip_user_name(user_name_2)
        user_2_names = self.get_user_and_nick_name(stripped_user_name_2)

        if user_1_names and user_2_names and self.can_this_happen(stripped_user_name_1, currency_db, sub_amount=amount) and self.can_this_happen(stripped_user_name_2, currency_db):
            self.update_user_bank(currency_db, amount, stripped_user_name_1, '-')
            self.update_user_bank(currency_db, amount, stripped_user_name_2, '+')
            success_message = f'Withdrew {amount} {currency} from {user_1_names[1]} and given to {user_2_names[1]}'
            await ctx.send(success_message)
        else:
            await ctx.send('Either user doesn\'t exist or you\'ll overdraw')

    @command(name='dontdothisunlessyoureabsolutelysure')
    @isDm()
    async def reset_all(self, ctx):
        db.execute('DELETE FROM bank')
        await ctx.send('Man hope you were sure, you just nuked everything')

    #Helper functions and shit
    def can_this_happen(self, stripped_user_name, currency_db='GoldAmt', sub_amount=0):
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_user_name))
        if user_exists:
            current_amount = db.record("SELECT {} FROM bank WHERE CharacterName = {}".format(currency_db, stripped_user_name))
            final_value = int(current_amount[0]) - int(sub_amount)
            return final_value >= 0
        else:
            return False
    
    def format_balance_embed(self, user_account):
        embed = Embed(title=f"{user_account[1]}'s Bank Balance", description="How much you got?")
        just_the_money_values = user_account[2:]
        currency_strings = []
        for key in CURRENCY_DICT.keys():
            currency_strings.append(key)

        balance_fields = [("Total monies", "\n".join([f"{currency_strings[index]}: {just_the_money}" for index, just_the_money in enumerate(just_the_money_values)]), False)]
        for name, value, inline in balance_fields:
            embed.add_field(name=name, value=value, inline=inline)  
        
        return embed

    def update_user_bank(self, currency_db, amount, stripped_user_name, addOrSubtract):
        db.execute("UPDATE bank SET {} = {}{}? WHERE CharacterName = ?".format(currency_db, currency_db, addOrSubtract), amount, stripped_user_name)

    def get_user_and_nick_name(self, stripped_user_name):
        user_names = db.record("SELECT CharacterName, NickName FROM bank WHERE CharacterName = {}".format(stripped_user_name))
        return user_names[0], user_names[1]

    def get_database_currency(self, currency):
        for key, value in CURRENCY_DICT.items():
            if currency.lower().startswith(key.lower()[0]):
                currency_db = value
                currency = key
                continue
            
        return currency, currency_db

    def strip_user_name(self, user_name):
        return user_name.replace(">","").replace("<","").replace("@","")
    
    def construct_user_name(self, user_name):
        constructed_user_name =  "@<" + user_name + ">"
        return constructed_user_name

    def currency_formatting(self, message):
        user_name = message.split()[0]
        amount = message.split()[1]
        currency = message.split()[2]

        try:
            int(amount)
        except Exception as e:
            return HTTPException

        currency, currency_db = self.get_database_currency(currency)
        return user_name, amount, currency_db, currency

def setup(bot):
    bot.add_cog(Bank(bot))