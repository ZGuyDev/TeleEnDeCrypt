from handlers import Dispatcher, types
from handlers import bot
from handlers import State, StatesGroup

from handlers import hash_key, encrypt
from handlers import BytesIO
from handlers import Path
from modules.messages import MESSAGES


class FSM_Encryption(StatesGroup):
    key = State()
    file = State()


async def start_encryption(message: types.Message):
    await FSM_Encryption.key.set()
    await bot.send_message(message.chat.id, MESSAGES["send-enc"])


async def get_encryption_key(message: types.Message, state: FSM_Encryption):
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
        file_unique_id = message.sticker.file_unique_id
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(file_unique_id)
    elif message.content_type is types.ContentType.LOCATION:
        longtitude = message.location.longitude
        latitude = message.location.latitude
        async with state.proxy() as proxy:
            proxy["key"] = hash_key(str(longtitude + latitude)[:-1])

    await message.delete()
    await FSM_Encryption.next()
    await bot.send_message(message.chat.id, MESSAGES["send-file-enc"])


async def get_file_to_encrypt(message: types.Message, state: FSM_Encryption):
    if message.content_type is types.ContentType.TEXT:
        async with state.proxy() as proxy:
            enc_data = encrypt(
                bytes(message.text, encoding="utf-8"), proxy["key"])
            enc_bytes = BytesIO(enc_data)
            await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename="encrypted.txt.aes"))

    elif message.content_type is types.ContentType.DOCUMENT:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_name = message.document.file_name

        if int(file_info.file_size) > 8 * 1024 * 1024 * 20:  # telegram limitations
            await bot.send_message(message.chat.id, MESSAGES["file-too-large-error"])
            return await state.finish()

        raw_bytes = BytesIO()
        await bot.download_file(file_info.file_path, raw_bytes)
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"{file_name}.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])
    elif message.content_type is types.ContentType.PHOTO:
        file_id = message.photo[0].file_id
        file_info = await bot.get_file(file_id)
        file_extension = Path(file_info["file_path"]).suffixes[-1]

        file_name = f"photo{file_extension}"

        if int(file_info.file_size) > 8 * 1024 * 1024 * 20:  # telegram limitations
            await bot.send_message(message.chat.id, MESSAGES["file-too-large-error"])

        raw_bytes = BytesIO()
        await bot.download_file(file_info.file_path, raw_bytes)
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"{file_name}.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])

    elif message.content_type is types.ContentType.VIDEO:
        file_id = message.video.file_id
        file_info = await bot.get_file(file_id)
        file_name = message.video.file_name

        if int(file_info.file_size) > 8 * 1024 * 1024 * 20:  # telegram limitations
            await bot.send_message(message.chat.id, MESSAGES["file-too-large-error"])
            return await state.finish()

        raw_bytes = BytesIO()
        await bot.download_file(file_info.file_path, raw_bytes)
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"{file_name}.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])
    elif message.content_type is types.ContentType.AUDIO:
        file_id = message.audio.file_id
        file_info = await bot.get_file(file_id)
        file_name = message.audio.file_name

        if int(file_info.file_size) > 8 * 1024 * 1024 * 20:  # telegram limitations
            await bot.send_message(message.chat.id, MESSAGES["file-too-large-error"])
            return await state.finish()

        raw_bytes = BytesIO()
        await bot.download_file(file_info.file_path, raw_bytes)
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"{file_name}.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])
    elif message.content_type is types.ContentType.LOCATION:
        longtitude = message.location.longitude
        latitude = message.location.latitude
        data = f"https://www.google.com/maps/@{longtitude},{latitude}"

        raw_bytes = BytesIO(bytes(data, encoding="utf-8"))
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"location.url.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])
    elif message.content_type is types.ContentType.STICKER:
        file_id = message.sticker.file_id

        raw_bytes = BytesIO(bytes(file_id, encoding="utf-8"))
        try:
            async with state.proxy() as proxy:
                enc_data = encrypt(raw_bytes.read(), proxy["key"])
                del raw_bytes
                enc_bytes = BytesIO(enc_data)

                await bot.send_document(message.chat.id, document=types.InputFile(enc_bytes, filename=f"sticker.TELEGRAM_STICKER.aes"))
        except:
            await bot.send_message(message.chat.id, MESSAGES["unknown-error"])
    else:
        await bot.send_message(message.chat.id, MESSAGES["wrong-data-type-enc"])
    await state.finish()


def encryption_register(dp: Dispatcher):
    dp.register_message_handler(start_encryption, commands=[
                                "encrypt", "зашифровать", "шифрование"], state=None)
    dp.register_message_handler(get_encryption_key, content_types=[
                                types.ContentType.TEXT, types.ContentType.DOCUMENT, types.ContentType.STICKER, types.ContentType.VOICE,
                                types.ContentType.LOCATION], state=FSM_Encryption.key)
    dp.register_message_handler(get_file_to_encrypt, content_types=[
                                types.ContentType.DOCUMENT, types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO,
                                types.ContentType.AUDIO, types.ContentType.LOCATION, types.ContentType.STICKER], state=FSM_Encryption.file)
