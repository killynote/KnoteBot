import shlex

from amiyabot import Chain, log
from amiyabot import Message

from ai.gpt.chatgpt import ChatGPT
from configs import normal_order_level, image_dir, bot, system_order
from ai.image.create import ImageGeneration
from utils.argument_parser import ArgumentParser


class Meta:
    command = "#画图"
    description = "通过自然语言绘制图片"

# 画图(先暂时固定生成1024，1张)
async def draw_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=draw_verify, level=normal_order_level, check_prefix=False)
async def draw(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 添加选项和参数
    parser.add_argument('-n', '--generated-number', type=int, default=1, help="生成图片数量，一般为1-10之间的整数，不建议一次生成超过3张，数量过高出现问题的概率会增大，默认为1")
    parser.add_argument('-p', '--prompt', type=str, default=None, help="对需要生成的图片的描述，使用自然语言，越详细越好，虽然中文也可以，但是英文的准确度更高，此项必填")
    parser.add_argument('-s', '--size', type=str, default="512x512", help="生成图片的分辨率，只能为128x128、512x512、1024x1024其中之一，默认为512x512")

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    number = args.generated_number
    prompt = args.prompt
    size = args.size

    # 判断参数是否正确
    if size not in ['128x128', '512x512', '1024x1024']:
        return Chain(data).text(f"指定的图像尺寸不正确，支持的尺寸为: 128x128、512x512、1024x1024，指定的尺寸为: {size}")
    if not prompt:
        return Chain(data).text(f"需要使用-p/--prompt参数指定prompt(对图片的描述)，使用\"{Meta.command} -h\"查看详细帮助")
    if number > 10 or number < 1:
        return Chain(data).text(f"指定的数量不正确，数量只能为1-10之间的整数，指定的数量为: {number}")

    await bot.send_message(Chain().at(data.user_id).text("正在准备生成，请稍等..."), channel_id=data.channel_id)

    # 通过GPT将prompt处理为英文
    prompt_en = await ChatGPT(temperature=0, system_order=system_order['翻译助手']).call(content=prompt)

    image_generation = ImageGeneration(prompt=prompt_en, gen_number=number, size=size)
    urls = await image_generation.call()
    if type(urls) == str:
        return Chain(data).text(urls)

    files = await image_generation.download_images()
    if not files:
        return Chain(data).text("图像生成错误，请稍后重试！")

    image_count = 0
    for file in files:
        with open(f'{image_dir}/{file}', 'rb') as f:
            image = f.read()
        image_count +=1
        await bot.send_message(Chain().text(f'prompt: {prompt_en}, size: {size}, number: {image_count}/{len(files)}').image(image), channel_id=data.channel_id)
    return

