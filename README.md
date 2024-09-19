# NMD Hashira Competitions bot

Welcome to the Tournament Bot! This Telegram bot allows you to create and manage tournaments using the McMahon pairing
system.
The bot also recalculates ratings based on the Elo formula and dynamic deviation, which is calculated before and after
each rating recalculation.

The bot is only to manage tournaments privately for Hashira clan in "Ninja must die" game.

## Features

* Create and manage tournaments
* McMahon pairing system for optimal pairings
* Elo rating system with dynamic deviation
* Store all data in Google Sheets as a database
* Designed to run cheaply on a serverless resource

## Bot initial setup

1. Fork the bot
2. Setup the config/config.ini file with all required id's
3. Add gapi_service_file.json with google service account token from https://console.cloud.google.com/
4. Setup 2 required google sheets: admins (with 2 worksheets: admins and global settings) and ratings (with 1 worksheet)
   You can have some issues here, but read logs carefully and everything will be fine
5. Start the bot: `export MODE=Release && python3 main.py`
    * use `MODE=Debug` or `MODE=Test` to use appropriate id's from config file

## Usage

* Only admins in the admin google sheet can use the bot menu
  So add yourself to the admin worksheet. Tg username in the first column, tg id in the second column.
* As you are an admin you can use the command /start to see the menu:
    * Administrators - add, delete or show admins
    * Ratings - update or delete rating
    * Global settings - these settings will be used when autostart enabled. Autostart can be enabled here :)
    * Tournament - create, schedule or manage current tournament
    * Service - development functions such as: upload log, fetch admins, fetch ratings, download configs
    * User - here you can interact with the bot as a common user
* A common user will see a permission error message if the user doesn't exist in the rating sheet
* Add the bot to the required group with admin rights (it requires to pin self messages)
* Use command /mark_as_tournament_thread to ... mark as a tournament thread... :)
  All tournament messages will be published here
* Start a tournament

## Disclaimer

This bot is designed to be cost-effective and does not use internal memory.
All data is stored in Google Sheets. This will allow you to safe a lot of money if you use a serverless resource.
But some stuff such as time has to be still modified. I got a free server so stopped the idea.

## Feedback

If you have any feedback, suggestions, or issues with the bot, please feel free to open an issue on GitHub or contact me
directly.

Thank you for using the Tournament Bot! Let the games begin! 🏆🤖
