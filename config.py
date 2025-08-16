from environs import Env

env = Env()
env.read_env()

bot_token = env.str("TOKEN")
open_ai_token = env.str("OPEN_AI_TOKEN")
hour = env.int("HOUR")
minute = env.int("MINUTE")
