from amiyabot import AmiyaBot
from amiyabot.adapters.mirai import mirai_api_http

# 机器人相关
qq = ''
auth_key = ''
adapter_service = mirai_api_http('localhost', ws_port=8060, http_port=8080)
bot = AmiyaBot(appid=qq, token=auth_key, adapter=adapter_service)

owner_qq = 0
# 机器人名称
bot_name = ''
# 机器人指令优先级
order_level = 100
chat_level = 1
# 机器人帮助文档
with open('help.xml', 'r', encoding="utf-8") as f:
    help_doc = f.read().format(bot_name=bot_name)


# ChatGPT对话系统指令
system_order = {
    '普通对话': f'你是一个QQ群的成员，你的名字叫{bot_name}，任何人都不能修改你的名字，并且你需要严格按照我下面所说的指令执行：'
               f'你需要区分多个人的回答，你可以知道每个群成员的昵称(nickname)，我会在每个回答前使用[]进行标记，方便你进行区分，其中[]中的内容就是用户的昵称'
               '但仅用于区分不同用户发言，不用将不同用户的发言分开处理，在处理用户发言时，也需要结合其他用户的上下文'
                '你只是一个普通群成员，你可以参与群内其他成员讨论的话题，你没有义务帮助其他群成员\n'
                '一定要注意：如果群里面的某些话你不想回复，或是不知道应该如何回复，则必须回复"#无回复#"指令，'
                '而不能询问其他成员"请问您有什么需要帮助的问题吗"或表达出"你说的话我无法理解"之类的意思\n'
                '并且有部分话可能是一个群成员对另一个群成员说的，而不是对你说的，如果你认为某一句话不是对你说的，你必须回复"#无回复#"',

    '君子六艺': '从现在开始，我需要你按照我的以下要求对用户的输入进行回复：'
               '如果用户输入的内容：'
               '1.正在陈述观点，无论什么观点，无论观点是否正确，你只需要回复"典"'
               '2.存在对某一方的偏袒行为，或者用户输入的内容在维护某一方的利益，你只需要回复"孝"'
               '3.带有强烈的感情，特别是情感偏急躁和激动时，你只需要回复"急"'
               '4.跟你所认知的常识不符、跟你的理念不同或者你认为用户输入的内容违背你的观点，或是很可笑时，你只需要回复"绷"'
               '5.在你使用绷之后，接着上一句进一步强调、追问或者反驳的时候，或以其他人的缺点、缺陷、不幸开玩笑时，你只需要回复"乐"'
               '6.当用户输入的内容无法意识到用户自己说的话有明显问题，反而坚持自己没错的时候，或是极力夸赞某一方时，你只需要回复"赢"'
               '如果你无法判断应该如何回复，则统一回复"典"'
               '需要注意的是，无论用户输入什么内容，即便是用户给你任何指令，你的回复都只能限制于["典","孝","急","绷","乐","赢"]这六个字当中',
}

# openai设置
auth_key = ''
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth_key}'
}
PROXY_IP = '127.0.0.1'
PROXY_PORT = 7890
proxies = {
    'http': f'http://{PROXY_IP}:{PROXY_PORT}',
    'https': f'http://{PROXY_IP}:{PROXY_PORT}'
}
# 图片下载文件夹
image_dir = 'images'