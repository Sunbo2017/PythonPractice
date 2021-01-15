# pip install websocket_client
import websocket
import threading
import time

file = True
num = 0


def on_message(ws, message):
    print(message)
    print('**********************')


def on_error(ws, error):
    print(error)


def on_close(ws):
    print('关闭')
    "### closed ###"


def on_open(ws):
    def run(*args):
        global num
        while num < 5:
            time.sleep(1)
            num += 1
            print("{'message': 'num_%s'}" % num)
            ws.send('{"message": "num_%s"}')
        # ws.send('{"message": "num_%s"}')
        time.sleep(1)
        ws.close()
        print("thread close...")

    th = threading.Thread(target=run, args=())
    th.start()


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:8131/",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)
