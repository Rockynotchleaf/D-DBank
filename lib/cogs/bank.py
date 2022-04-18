from email.policy import HTTP
from http.client import HTTPException
from discord.ext.commands import command, Cog
from discord import Embed
from ..db import db
from itertools import islice

CURRENCY_DICT = {
    'Copper': 'CopperAmt',
    'Silver': 'SilverAmt',
    'Brass': 'BrassAmt',
    'Gold': 'GoldAmt',
    'Platinum': 'PlatinumAmt',
    'Electrum': 'ElectrumAmt'
}

class Bank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='enroll')
    async def add_user(self, ctx, *, message):
        #+add_user @user
        nick_name = message.split()[1]
        stripped_message = self.strip_user_name(message.split()[0])
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_message))
        if user_exists:
            success_message = "{} already has an account".format(message)
            await ctx.send(success_message)
        else:
            db.execute("INSERT INTO bank VALUES (?,?,?,?,?,?,?,?)", stripped_message,nick_name,0,0,0,0,0,0)
            success_message = "{} has opened an account".format(message)
            await ctx.send(success_message)
            return
    
    @command(name='balance')
    async def view_balance(self, ctx, *, message):
        stripped_user_name = self.strip_user_name(message)
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_user_name))
        if user_exists:
            user_account = db.record('SELECT * FROM bank WHERE CharacterName = {}'.format(stripped_user_name))
            #gives a list (something, something) need to show individual and total

            embed = Embed(title=f"{user_account[1]}'s Bank Balance", description="How much you got?")
            just_the_money_values = user_account[2:]
            currency_strings = []
            for key in CURRENCY_DICT.keys():
                currency_strings.append(key)

            balance_fields = [("Total monies", "\n".join([f"{currency_strings[index]}: {just_the_money}" for index, just_the_money in enumerate(just_the_money_values)]), False)]
            for name, value, inline in balance_fields:
                embed.add_field(name=name, value=value, inline=inline)            

            await ctx.send(embed=embed)
        else:
            await ctx.send('Please enroll this user first')

    @command(name='deposit')
    async def deposit_currency(self, ctx, *, message):
        user_name, amount, currency_db, currency = self.currency_formatting(message)
        stripped_user_name = self.strip_user_name(user_name)
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_user_name))
        if user_exists:
            db.execute("UPDATE bank SET {} = {} + ? WHERE CharacterName = ?".format(currency_db, currency_db), amount, stripped_user_name)
            success_message = f'Sent {amount} {currency}'
            await ctx.send(success_message)
        else:
            await ctx.send('Please enroll this user first')

    @command(name='loot')
    async def loot_currency(self, ctx, *, message):
        new_message = "all " + message
        user_name, amount, currency_db, currency = self.currency_formatting(new_message)

        db.execute("UPDATE bank SET {} = {} + ?".format(currency_db, currency_db), amount)
        success_message = f'Sent {amount} {currency}'
        await ctx.send(success_message)

    @command(name='withdraw')
    async def withdraw_currency(self, ctx, *, message):
        user_name, amount, currency_db, currency = self.currency_formatting(message)
        stripped_user_name = self.strip_user_name(user_name)
        user_exists = db.record("SELECT CharacterName FROM bank WHERE CharacterName = {}".format(stripped_user_name))
        if user_exists and self.can_this_happen(stripped_user_name, currency_db, sub_amount=amount):
            db.execute("UPDATE bank SET {} = {}-? WHERE CharacterName = ?".format(currency_db, currency_db), amount, stripped_user_name)
            success_message = f'Withdrew {amount} {currency}'
            await ctx.send(success_message)
        else:
            await ctx.send('Either user doesn\'t exist or you\'ll overdraw')

    @command(name='transfer')
    async def transfer_currency(self, ctx, *, message):
        user_name_1 = message.split()[0]
        user_name_2 = message.split()[1]
        amount = message.split()[2]
        currency = message.split()[3]

        #string compare maybe toLower and select from dict
        for key, value in CURRENCY_DICT.items():
            if currency.lower().startswith(key.lower()[0]):
                currency_db = value
                currency = key
                continue
        stripped_user_name_1 = self.strip_user_name(user_name_1)
        user_1_names = db.record("SELECT CharacterName, NickName FROM bank WHERE CharacterName = {}".format(stripped_user_name_1))
        stripped_user_name_2 = self.strip_user_name(user_name_2)
        user_2_names = db.record("SELECT CharacterName, NickName FROM bank WHERE CharacterName = {}".format(stripped_user_name_2))

        if user_1_names and user_2_names and self.can_this_happen(stripped_user_name_1, currency_db, sub_amount=amount) and self.can_this_happen(stripped_user_name_2, currency_db):
            db.execute("UPDATE bank SET {} = {}-? WHERE CharacterName = ?".format(currency_db, currency_db), amount, stripped_user_name_1)
            db.execute("UPDATE bank SET {} = {}+? WHERE CharacterName = ?".format(currency_db, currency_db), amount, stripped_user_name_2)
            success_message = f'Withdrew {amount} {currency} from {user_1_names[1]} and given to {user_2_names[1]}'
            await ctx.send(success_message)
        else:
            await ctx.send('Either user doesn\'t exist or you\'ll overdraw')

    #Helper functions and shit
    def can_this_happen(self, stripped_user_name, currency_db, sub_amount=0):
        current_amount = db.record("SELECT {} FROM bank WHERE CharacterName = {}".format(currency_db, stripped_user_name))
        final_value = int(current_amount[0]) - int(sub_amount)
        print(final_value)
        return final_value > 0

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

        #string compare maybe toLower and select from dict
        for key, value in CURRENCY_DICT.items():
            if currency.lower().startswith(key.lower()[0]):
                currency_db = value
                currency = key
                continue
        return user_name, amount, currency_db, currency


def setup(bot):
    bot.add_cog(Bank(bot))