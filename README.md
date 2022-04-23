# What is this

D-DBank is a discord.py bot that can keep track of your players wallets in D&D
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install discord.py

```bash
pip install discord.py
```
Invite the bot to your server

Run by executing the `launcher.py` file in the repo.

## Usage

First you will need to have Administrator permissions on your discord.

Then you will be able to use the following commands,

- `+enroll` - Adds the player to the bank
```
+enroll @playersDiscordName {players in game name}
```
- `+dm` - Makes a player the DM, so has permissions to use most things (must be server admin)
```
+dm @playersDiscordName
```
- `+balance` - Shows a player their balance
```
+balance @playersDiscordName
```
- `+withdraw` - Removes currency from the player (DM only function)
```
+withdraw @playersDiscordName {amount to remove} {type of currency}
```
- `+deposit` - Adds currency to the player (DM only function)
```
+deposit @playersDiscordName {amount to give} {type of currency}
```
- `+loot` - Adds currency to all players (DM only function)
```
+loot @playersDiscordName {amount to give} {type of currency}
```
- `+transfer` - Moves currency from one player to another (DM only function)
```
+transfer @playerGivingCurrencyDiscordName @playerReceivingCurrencyDiscordName {amount to remove from player 1 and give to player 2} {type of currency}
```
- `+dontdothisunlessyoureabsolutelysure` - Deletes all rows in the bank DB (DM only function)


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
