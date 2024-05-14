#Установка библиотек
!pip install pytelegrambotapi -q
!pip install diffusers -q
!pip install deep-translator -q

!pip install -U g4f --quiet
!pip install browser-cookie3 --quiet
!pip install aiohttp_socks --quiet

#GPT-4 и Создание картинки
import telebot;
from telebot import types
from deep_translator import GoogleTranslator
bot = telebot.TeleBot('7119246996:AAF1Z2U4pZhVhHPJJiLrwC-gzwFyproWJow');


import g4f
from g4f.Provider import (
    GeekGpt,
    Liaobots,
    Phind,
    Raycast,
    RetryProvider,
    Bing,
    ChatgptAi,
    You)
from g4f.client import Client
import nest_asyncio
nest_asyncio.apply()

client = Client(
    provider = RetryProvider([
            g4f.Provider.Liaobots,
            g4f.Provider.GeekGpt,
            g4f.Provider.Phind,
            g4f.Provider.Raycast,
            g4f.Provider.Bing,
            g4f.Provider.ChatgptAi,
            g4f.Provider.You
    ])
  )
chat_history = [{"role": "user", "content": 'Отвечай на русском языке'}]


def send_request(message):
    global chat_history
    chat_history[0]["content"] += message + " "

    try:
        response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=chat_history
    )
    except Exception as err:
        print("Все провайдеры не отвечают, попробуйте пойзже")
    print(response)
    chat_history[0]["content"] += response + " "
    return response

from diffusers import DiffusionPipeline
import torch

def send_photo(message):
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True)

    base.to("cuda")
    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16", )
    refiner.to("cuda")


    n_steps = 40
    high_noise_frac = 0.8

    prompt = message

    image = base(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_end=high_noise_frac,
        output_type="latent", ).images
    image = refiner(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_start=high_noise_frac,
        image=image, ).images[0]
    return image
#Запуск бота
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("❓ О боте")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Привет! Можешь спрашивать меня! Что тебя интересует?', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "👋 Поздороваться"):
        bot.send_message(message.chat.id, text=f"Привет, {message.from_user.first_name}, надеюсь я смогу тебе помочь)")
    elif (message.text == "❓ О боте"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Как меня зовут?")
        btn2 = types.KeyboardButton("Что я могу?")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)

    elif (message.text == "Как меня зовут?"):
        bot.send_message(message.chat.id, "Cooking bOt🤖")

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id,
                         text="🍴Рассказать пользователю о рецепте любого блюда, а также изобрзить готовый результат")

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("👋 Поздороваться")
        button2 = types.KeyboardButton("❓ О боте")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
    else:
        inp = GoogleTranslator(source='auto', target='en').translate(message.text)
        inp1 = "tell me the recipe for " + inp
        out = GoogleTranslator(source='auto', target='ru').translate(send_request(inp1))

        bot.send_message(message.chat.id, out)
        bot.send_photo(message.chat.id, send_photo(inp))


bot.polling(none_stop=True, interval=0)