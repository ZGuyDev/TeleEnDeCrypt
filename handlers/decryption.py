from handlers import Dispatcher, types
from handlers import bot
from handlers import State, StatesGroup

from handlers import hash_key, decrypt
from handlers import BytesIO
from handlers import Path
from modules.messages import MESSAGES


class FSM_Decryption(StatesGroup):
    key = State()
    file = State()


async def start_decryption(message: types.Message):
    await FSM_Decryption.key.set()
    await bot.send_message(message.chat.id, MESSAGES["send-dec"])


async def get_decryption_key(message: types.Message, state: FSM_Decryption):
    if message.content_type is types.ContentType.TEXT:
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(message.text)
    elif message.content_type is types.ContentType.DOCUMENT:
        file_unique_id = message.document.file_unique_id
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(file_unique_id)
    elif message.content_type is types.ContentType.STICKER:
        file_unique_id = message.sticker.file_unique_id
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(file_unique_id)
    elif message.content_type is types.ContentType.VOICE:
        file_unique_id = message.voice.file_unique_id
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(file_unique_id)
    elif message.content_type is types.ContentType.LOCATION:
        longtitude = message.location.longitude
        latitude = message.location.latitude
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(str(longtitude + latitude)[:-2])

    await message.delete()
    await FSM_Decryption.next()
    await bot.send_message(message.chat.id, MESSAGES["send-file-dec"])


async def get_file_to_decrypt(message: types.Message, state: FSM_Decryption):
    if message.content_type is types.ContentType.DOCUMENT:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_name = message.document.file_name

        file_base = file_name.split(".")[0]
        file_extensions = Path(file_name).suffixes

        if file_extensions[-1].lower() == ".aes":
            file_extensions.pop(-1)

        if int(file_info.file_size) > 8 * 1024 * 1024 * 20:
            await bot.send_message(message.chat.id, MESSAGES["file-too-large-error"])
            return await state.finish()

        raw_bytes = BytesIO()
        await bot.download_file(file_info.file_path, raw_bytes)

        try:
            if not len(file_extensions):
                async with state.proxy() as proxy:
                    dec_data = decrypt(raw_bytes.read(), proxy["key"])
                    del raw_bytes
                    dec_bytes = BytesIO(dec_data)

                    await bot.send_document(message.chat.id, document=types.InputFile(dec_bytes, filename=f"{file_base}.txt"))
            else:
                file_extension = file_extensions[-1]

                if file_extension == ".TELEGRAM_STICKER":
                    async with state.proxy() as proxy:
                        dec_data = decrypt(
                            raw_bytes.read(), proxy["key"]).decode()
                        del raw_bytes
                        await bot.send_sticker(message.chat.id, sticker=dec_data)
                else:
                    async with state.proxy() as proxy:
                        dec_data = decrypt(raw_bytes.read(), proxy["key"])
                        del raw_bytes
                        dec_bytes = BytesIO(dec_data)

                        await bot.send_document(message.chat.id, document=types.InputFile(dec_bytes, filename=f"{file_base}{file_extension}"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["wrong-key-dec"])

    ########################################################################################
    # doesn't make sense, because telegram deletes "garbage symbols"

    # elif message.content_type is types.ContentType.TEXT:
    #     try:
    #         async with state.proxy() as proxy:
    #             dec_data = decrypt(bytes(message.text, encoding="utf-8"), proxy["key"])
                
    #             await bot.send_message(message.chat.id, dec_data)
    #     except:
    #         await bot.send_message(message.chat.id, MESSAGES["wrong-key-dec"])
    ########################################################################################
    else:
        await bot.send_message(message.chat.id, MESSAGES["wrong-data-type-dec"])
    await state.finish()


def decryption_register(dp: Dispatcher):
    dp.register_message_handler(start_decryption, commands=[
                                "decrypt", "расшифровать", "дешифровать", "дешифрование"], state=None)
    dp.register_message_handler(get_decryption_key, content_types=[
                                types.ContentType.TEXT, types.ContentType.DOCUMENT, types.ContentType.STICKER, types.ContentType.VOICE,
                                types.ContentType.LOCATION], state=FSM_Decryption.key)
    dp.register_message_handler(get_file_to_decrypt, content_types=[
                                types.ContentType.DOCUMENT], state=FSM_Decryption.file)
