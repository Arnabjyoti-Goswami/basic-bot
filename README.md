# Basic Bot

A basic discord bot

# Features

- [x] Mute command with specified durations, unmute command
- [x] Command for Reaction Roles
- [x] Reminder command to remind the user after a specified duration
- [x] Verify and unverify commands
- [ ] Need to implement something such that the bot recognizes its own messages before it came online. If the current script is turned off and restarted, then the bot's previous messages for commands like self_roles doen't work as roles are not added to users upon reacting, this is because the on_reaction_add() is called only if the messages are in the bot's cache