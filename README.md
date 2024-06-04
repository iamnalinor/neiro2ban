# neiro2ban
Ban annoying "Нейросети для творчества и заработка" reaction spammers

Bot bans users that set any reaction meeting all of this criterias:
1. Obviously, the reaction should be added from user profile
2. This is the first and only reaction from this user
3. The reaction should be added no later than 10 seconds from the time the message was sent
4. The user should have "@creaitors_bot" keyword in bio

## Setup
1. Create your bot in @BotFather, add it to target group and give admin rights with "Ban users" privilege
2. `pip install -r requirements.txt`
3. Either create file `.env` and fill it with your token (i.e. `BOT_TOKEN=123456:abcdef`) or pass BOT_TOKEN to environment variables
4. Run main.py
