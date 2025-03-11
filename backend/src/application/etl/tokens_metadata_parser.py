import asyncio
import base64
import json
import logging
import struct

import aiohttp
from solders.pubkey import Pubkey
from tortoise import Tortoise

from src.infra.db.models.tortoise import Token
from src.infra.db.setup_tortoise import (
    init_db_async,
)

logger = logging.getLogger("tasks.parse_tokens_metadata")


async def parse_tokens_metadata_async():
    try:
        await init_db_async()
        while True:
            tokens = await get_tokens_to_process()
            if not tokens:
                logger.debug("Нету токенов для сбора метаданных.")
                return
            await process_tokens(tokens)
            await asyncio.sleep(1)
    finally:
        await Tortoise.close_connections()


async def get_tokens_to_process():
    tokens = await Token.filter(is_metadata_parsed=False).limit(100)  # Получаем токены, которые не были обработаны
    return tokens


async def process_tokens(tokens):
    await asyncio.gather(*[fetch_and_update_token_metadata(token) for token in tokens])


async def fetch_and_update_token_metadata(token):
    try:
        metadata = await fetch_token_metadata(token.address)  # Функция для получения метаданных для токена
    except Exception as e:
        logger.debug(f"Ошибка парсинга метаданных токена: {token} - {e}")
        # traceback.print_exc()
        return
    uri = metadata.get("uri")
    json_metadata = {}
    if uri:
        try:
            json_metadata = await fetch_json_metadata_from_uri(uri)
        except Exception as e:
            logger.debug(f"Не удалось получить JSON-метаданные по URI токена {token} - {e}")
    await update_token(token, metadata, json_metadata)
    logger.debug(f"Метаданные токена {token.address} успешно обновлены!")


async def update_token(token, metadata, json_metadata):
    token.metadata = metadata  # Сохраняем метаданные
    token.name = metadata.get("name")
    token.symbol = metadata.get("symbol")
    token.uri = metadata.get("uri")
    logo = str(json_metadata.get("image", "")).replace("\u0000", "")
    created_on = str(json_metadata.get("createdOn", "")).replace("\u0000", "")
    token.logo = logo if len(logo) <= 255 else None
    token.created_on = created_on if len(created_on) <= 255 else None

    token.is_metadata_parsed = True
    await token.save()


async def fetch_token_metadata(token_address):
    metadata_pubkey = await get_token_metadata_pubkey(token_address)
    account_info = await get_token_account_info(str(metadata_pubkey))
    if not account_info["result"]["value"]:
        return {}
    data = account_info["result"]["value"]["data"][0]
    decoded_metadata = decode_metadata(data)
    return decoded_metadata


async def get_token_metadata_pubkey(mint_address):
    metadata_program_id = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
    mint_pubkey = Pubkey.from_string(mint_address)
    metadata_pubkey = Pubkey.find_program_address(
        [
            b"metadata",
            bytes(metadata_program_id),
            bytes(mint_pubkey),
        ],
        metadata_program_id,
    )[0]
    return metadata_pubkey


async def fetch_json_metadata_from_uri(url):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        async with session.get(url) as resp:
            return await resp.json()


async def get_token_account_info(pubkey):
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            pubkey,
            {"encoding": "base64"},
        ],
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        async with session.post(
            "http://ny.rpc.onyxnodes.com:8899/",
            json=payload,
            headers=headers,
        ) as resp:
            data = await resp.text()
            result = json.loads(data)
            if result.get("error"):
                raise ValueError(result.get("error"))
            return result


def decode_metadata(data):
    decoded_data = base64.b64decode(data)
    try:
        offset = 1 + 32 + 32  # Ключ + два публичных ключа
        name_len = struct.unpack_from("<B", decoded_data, offset)[0]
        offset += 4  # Длина имени занимает 1 байт
        name = (
            struct.unpack_from(
                f"<{name_len}s",
                decoded_data,
                offset,
            )[0]
            .decode("utf-8")
            .rstrip("\x00")
        )
        offset += name_len
        symbol_len = struct.unpack_from("<B", decoded_data, offset)[0]
        offset += 4  # Длина символа занимает 1 байт
        symbol = (
            struct.unpack_from(
                f"<{symbol_len}s",
                decoded_data,
                offset,
            )[0]
            .decode("utf-8")
            .rstrip("\x00")
        )
        offset += symbol_len
        uri_len = struct.unpack_from("<B", decoded_data, offset)[0]
        offset += 4  # Длина URI занимает 1 байт
        uri = (
            struct.unpack_from(
                f"<{uri_len}s",
                decoded_data,
                offset,
            )[0]
            .decode("utf-8")
            .rstrip("\x00")
        )
        return {
            "name": name,
            "symbol": symbol,
            "uri": uri,
        }
    except (
        struct.error,
        UnicodeDecodeError,
    ) as e:
        logger.debug(f"Error decoding metadata: {e}")
        raise e
