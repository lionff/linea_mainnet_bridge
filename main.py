import json
import time
from web3 import Web3
import random

w3 = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))  # ETH mainnet RPC
linea_w3 = Web3(Web3.HTTPProvider('https://rpc.linea.build/'))

bridge_abi = json.load(open('bridge_abi.json'))
bridge_address = w3.to_checksum_address('0xd19d4B5d358258f05D7B411E21A1460D11B0876F')
bridge_contract = w3.eth.contract(address=bridge_address, abi=bridge_abi)

with open("private_keys.txt", "r") as f:
    keys_list = [row.strip() for row in f if row.strip()]
    numbered_keys = list(enumerate(keys_list, start=1))
    # random.shuffle(numbered_keys)  # Можно расскомментировать если хотите перемешать кошельки

your_choice = int(input(
    "1 - фиксированное кол-во токенов, 2 - рандом в диапазоне, 3 - некий процент: \n"))

for wallet_number, PRIVATE_KEY in numbered_keys:

    account = w3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    print(time.strftime("%H:%M:%S", time.localtime()))
    print(f'[{wallet_number}] - {address}', flush=True)

    _to = address
    _fee = linea_w3.eth.gas_price * 100000
    calldata = b''

    if your_choice == 1:
        AMOUNT = 0.1  # на все акки полетит по 0.1 эфиру
        amnt = w3.to_wei(AMOUNT, 'ether')

    if your_choice == 2:
        AMOUNT = random.uniform(0.1, 1)  # рандомное количество эфира для бриджа в диапазоне от 0.1 до 1
        amnt = w3.to_wei(AMOUNT, 'ether')

    if your_choice == 3:
        amnt = int(w3.eth.get_balance(
            address) * 0.5)  # Выводим 50% баланса - меняем 0.5 для смены процента. 100% не отправить - комса

    value = amnt + _fee


    # Чек газа в основной сети - можно выпилить этот блок
    while True:
        if w3.eth.gas_price > 20000000000: # Если газ больше 20 гвей - то ждет. Можно расскоментить ниже строки, чтоб не смотреть пустоту
             #print('Ждем газа')
             #print(w3.from_wei(w3.eth.gas_price, 'gwei'))
             time.sleep(random.randint(120, 150))
        else:
            break

    # Если газ в поряде - начинаем работать

    tx = bridge_contract.functions.sendMessage(
        _to,
        _fee,
        calldata,
    ).build_transaction({
        'from': address,
        'maxFeePerGas': int(w3.eth.gas_price + (w3.eth.gas_price * 0.15)),
        'maxPriorityFeePerGas': 1500000000,
        'value': value,
        'nonce': w3.eth.get_transaction_count(address),
    })

    signed_transaction = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    txn = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f"Transaction: https://etherscan.io/tx/{txn.hex()}")
    time.sleep(random.randint(60, 90))
