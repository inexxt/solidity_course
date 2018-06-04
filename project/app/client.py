import sys
from frontend.Client import Client
from frontend.Connector import Connector
from utils.utils import W3cls, STATUS_DICT
import IPython

def sep():
    print("-----------------------------\n")

def create_channel():
    sep()
    cap = input("Select cap for your new channel: (in eth) ")
    cap = W3cls.ethToWei(int(cap))
    client.st.createNewChannel(cap)
    print(f"Channel {len(client.st.channels)} created")

def list_channels():
    sep()
    SEP = "\t\t\t"

    print("Your channels:")
    print(SEP.join(["Number", "Status", "Cap", "Used", "Left", "Closing at"]))
    channels = {}

    for e, _ in enumerate(client.st.channels):
        cap = W3cls.weiToEth(client.st.cap(None, e))
        status = STATUS_DICT[client.st.status(None, e)]

        used = W3cls.weiToEth(client.st.curr_used_funds[e])

        closing = client.st.closed_at(None, e) - W3cls.w3.eth.blockNumber
        if status == "open":
            closing_text = "None: channel still open"
        elif closing <= 0 and status == "closing":
            closing_text = "ready"
        elif status == "closing":
            closing_text = f"Not ready: {closing} blocks left"
        else:
            closing_text = "None: channel closed"

        left = cap - used
        print(SEP.join(map(str, [e, status, cap, used, left, closing_text])))
        channels[e] = {"cap": cap, "status": status, "used": used, "closing": closing}

    return channels

def delete_channel():
    channels = list_channels()
    c = input("Select channel to remove or 'c' to cancel: ")

    if c == 'c':
        return

    c = int(c)

    if c not in channels:
        print("Error: No such channel")
        return

    if channels[c]["status"] == "closed":
        print("Channel already closed")

    if channels[c]["status"] == "open":
        client.st.startClosingChannel(c, None)

    if channels[c]["status"] == "closing":
        if channels[c]["closing"] <= 0:
            client.st.closeChannel(c)

    print("Action finished")
    return

def list_catalog():
    sep()
    catalog = connector.downloadCatalog()
    print("Catalog: (id -> price)")
    print(catalog)

def buy():
    list_catalog()
    balances = client.getBalances()
    print(f"Funds available on your accounts: {balances}")
    channel_number = input("Select one of the accounts or 'c' to cancel: ")
    channel_number = int(channel_number) if channel_number != "c" else None

    if channel_number is None:
        return

    wid = input("Select one position from the catalog: ")
    print(f"Choosing {wid}")
    if wid in codes:
        print("Error: You've already bought this item")
        return

    if balances[channel_number] < catalog[wid]:
        print("Error: You do not have enough money for that")
        return

    receipt = client.buy(catalog[wid], int(channel_number))
    codes[wid] = connector.sendReceipt(receipt, wid)

    print(f"Succesfully bought {wid}")

def watch():
    sep()
    print(f"You have access to: {list(codes.keys())}")
    wid = input("Select your item: ")
    if wid not in codes:
        print("Error: You do not have this item")
        return

    print(connector.watch(wid, codes[wid]))

def dbg():
    IPython.embed()
    return

def main():
    sep()
    print("Actions: ")
    actions = {
        "b": ("buy", buy),
        "c": ("create channel", create_channel),
        "s": ("show your channels", list_channels),
        "d": ("delete channel", delete_channel),
        "l": ("list catalog", list_catalog),
        "w": ("watch an item", watch),
        "g": ("debug", dbg)
    }

    for k, v in actions.items():
        print(f" * {k} - {v[0]}")
    print()

    option = input("Select your action: ")

    if option in actions:
        actions[option][1]()
    else:
        print("Error: Invalid character")


if __name__ == "__main__":
    addresss = sys.argv[1]

    client = Client(addresss)
    connector = Connector()

    catalog = connector.downloadCatalog()
    codes = {}

    while True:
        try:
            main()
        except Exception as e:
            print(f"Error {e}")
