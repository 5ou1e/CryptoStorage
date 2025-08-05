import json
from datetime import datetime, timedelta

from solana.rpc.api import Client
from solders.pubkey import Pubkey
import time
from typing import Optional, Set, List, Dict

# Alchemy RPC endpoint
client = Client("https://solana-mainnet.g.alchemy.com/v2/WaQc10bHsmpRrYrEMM9Ah")


def get_signatures_for_time_period(
    program_address: Pubkey,
    hours_ago: int = 24,
    max_signatures: int = 1000
) -> List:
    """
    Получает подписи за определенный период времени

    Args:
        program_address: Адрес программы
        hours_ago: Количество часов назад от текущего момента
        max_signatures: Максимальное количество подписей для получения
    """
    all_signatures = []
    before_signature = None
    target_time = datetime.now() - timedelta(hours=hours_ago)
    target_timestamp = int(target_time.timestamp())

    print(f"🕐 Fetching transactions from the last {hours_ago} hours")
    print(f"📅 Target time: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ Fetching signatures...")

    while len(all_signatures) < max_signatures:
        try:
            # Получаем порцию подписей
            if before_signature:
                signatures = client.get_signatures_for_address(
                    program_address,
                    before=before_signature,
                    limit=100  # Получаем по 100 за раз
                )
            else:
                signatures = client.get_signatures_for_address(
                    program_address,
                    limit=100
                )

            if not signatures.value:
                break

            # Проверяем временные метки
            for sig_info in signatures.value:
                # block_time может быть None
                if sig_info.block_time and sig_info.block_time >= target_timestamp:
                    all_signatures.append(sig_info)
                elif sig_info.block_time and sig_info.block_time < target_timestamp:
                    # Если дошли до транзакций старше целевого времени, останавливаемся
                    print(f"✅ Reached target time period. Found {len(all_signatures)} signatures")
                    return all_signatures

            # Устанавливаем before для следующей итерации
            if signatures.value:
                before_signature = signatures.value[-1].signature

            print(f"📊 Fetched {len(all_signatures)} signatures so far...")

            # Небольшая задержка для избежания rate limit
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ Error fetching signatures: {e}")
            if "429" in str(e):
                print("⏳ Rate limit hit, waiting 2 seconds...")
                time.sleep(2)
            else:
                break

    return all_signatures


def find_swap_authority(tx_data) -> Optional[Dict[str, any]]:
    """
    Находит authority (подписанта) из SPL Token инструкций
    """
    try:
        if not tx_data or not tx_data.value:
            return None

        meta = tx_data.value.transaction.meta
        if not meta or meta.err:
            return None

        authorities = set()
        transfers = []

        # Проверяем внутренние инструкции
        if meta.inner_instructions:
            for inner_group in meta.inner_instructions:
                for inst in inner_group.instructions:
                    try:
                        # Проверяем различные форматы инструкций
                        program = None
                        parsed = None

                        # Проверяем атрибуты
                        if hasattr(inst, 'program'):
                            program = inst.program
                        elif isinstance(inst, dict) and 'program' in inst:
                            program = inst['program']

                        if hasattr(inst, 'parsed'):
                            parsed = inst.parsed
                        elif isinstance(inst, dict) and 'parsed' in inst:
                            parsed = inst['parsed']

                        # Если это SPL Token инструкция
                        if program == "spl-token" and parsed:
                            # Получаем тип инструкции
                            inst_type = None
                            if hasattr(parsed, 'type'):
                                inst_type = parsed.type
                            elif isinstance(parsed, dict) and 'type' in parsed:
                                inst_type = parsed['type']

                            # Для transferChecked и transfer
                            if inst_type in ["transferChecked", "transfer"]:
                                # Получаем info
                                info = None
                                if hasattr(parsed, 'info'):
                                    info = parsed.info
                                elif isinstance(parsed, dict) and 'info' in parsed:
                                    info = parsed['info']

                                if info:
                                    # Извлекаем authority
                                    authority = None
                                    if hasattr(info, 'authority'):
                                        authority = info.authority
                                    elif isinstance(info, dict) and 'authority' in info:
                                        authority = info['authority']

                                    if authority:
                                        authorities.add(authority)

                                        # Сохраняем информацию о переводе
                                        transfer_info = {
                                            "authority": authority,
                                            "type": inst_type,
                                            "source": info.get("source") if isinstance(info,
                                                                                       dict) else getattr(
                                                info, 'source', None),
                                            "destination": info.get("destination") if isinstance(
                                                info, dict) else getattr(info, 'destination', None),
                                            "mint": info.get("mint", "Unknown") if isinstance(info,
                                                                                              dict) else getattr(
                                                info, 'mint', "Unknown")
                                        }

                                        # Добавляем информацию о количестве
                                        if isinstance(info, dict):
                                            if "tokenAmount" in info:
                                                transfer_info["amount"] = info["tokenAmount"].get(
                                                    "uiAmountString", "Unknown")
                                                transfer_info["decimals"] = info["tokenAmount"].get(
                                                    "decimals", 0)
                                            elif "amount" in info:
                                                transfer_info["amount"] = info["amount"]
                                        else:
                                            token_amount = getattr(info, 'tokenAmount', None)
                                            if token_amount:
                                                transfer_info["amount"] = getattr(token_amount,
                                                                                  'uiAmountString',
                                                                                  "Unknown")
                                                transfer_info["decimals"] = getattr(token_amount,
                                                                                    'decimals', 0)
                                            elif hasattr(info, 'amount'):
                                                transfer_info["amount"] = info.amount

                                        transfers.append(transfer_info)
                    except Exception as e:
                        # Пропускаем проблемные инструкции
                        continue

        if authorities:
            # Обычно все переводы в свапе имеют одного authority
            return {
                "authority": list(authorities)[0] if len(authorities) == 1 else list(authorities),
                "transfers": transfers,
                "unique_authorities": len(authorities)
            }

        return None

    except Exception as e:
        print(f"Error parsing authority: {e}")
        return None


def main():
    # Адрес вашей программы
    program_address = Pubkey.from_string("Gy4r2wzguhhqqRRhcQV2wU6maxCLEtAR9zNSQt3iBPQP")
    raydium_launchpad_address = "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh"

    all_finded_authorities = set()
    all_signatures_with_authorities = []
    try:
        # Получаем подписи
        # signatures = client.get_signatures_for_address(program_address, limit=10).value

        signatures = get_signatures_for_time_period(
            program_address,
            hours_ago=336,
            max_signatures=100_000
        )

        print(f"Found {len(signatures)} signatures\n")

        swap_count = 0

        for i, sig_info in enumerate(signatures):
            signature = sig_info.signature

            try:
                # Получаем транзакцию
                tx = client.get_transaction(
                    signature,
                    encoding="jsonParsed",
                    max_supported_transaction_version=0
                )

                # Находим authority
                result = find_swap_authority(tx)

                if result:
                    swap_count += 1
                    print(f"\n✅ SWAP #{swap_count} - Signature: {signature}")

                    # Выводим authority
                    if isinstance(result["authority"], list):
                        print(f"🔑 Multiple Authorities Found:")
                        all_signatures_with_authorities.append(
                            {"signature": signature, "authorities": [auth for auth in
                                                                     result["authority"] if not
                            auth == raydium_launchpad_address]}
                        )
                        for auth in result["authority"]:
                            print(f"   - {auth}")
                            all_finded_authorities.add(auth)

                    else:
                        print(f"🔑 Authority: {result['authority']}")

                    # Выводим информацию о переводах
                    if result["transfers"]:
                        print(f"\n📊 Token Transfers ({len(result['transfers'])} found):")
                        for idx, transfer in enumerate(result["transfers"], 1):
                            print(f"\n   Transfer #{idx}:")
                            print(f"   - Type: {transfer['type']}")
                            print(f"   - Amount: {transfer.get('amount', 'Unknown')}")
                            print(f"   - Mint: {transfer['mint']}")
                            print(
                                f"   - From: {transfer['source']}")
                            print(
                                f"   - To: {transfer['destination']}")

                    print("-" * 80)

                # Задержка между запросами
                time.sleep(0.1)

            except Exception as e:
                print(f"\nError fetching transaction {signature}: {e}")
                if "429" in str(e):
                    print("Rate limit hit, waiting 1 second...")
                    time.sleep(1)
                continue

        print(
            f"\n📈 Summary: Found {swap_count} swaps with authority out of {len(signatures)} transactions")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

    print(all_finded_authorities)
    with open(f"authorities.txt", "a+") as file:
        for auth in all_finded_authorities:
            file.write(auth)
            file.write(f"\n")
    with open(f"signatures.txt", "a+") as file:
        for entry in all_signatures_with_authorities:
            line = f"{entry['signature']} | {entry['authorities']}"
            file.write(line)
            file.write(f"\n")



if __name__ == "__main__":
    main()