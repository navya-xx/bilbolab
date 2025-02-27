import time

from extensions.cli.cli_gui import CLI_GUI_Client

if __name__ == "__main__":
    gui = CLI_GUI_Client(address='localhost', port=8090)
    gui.init()
    gui.start()

    while True:
        # gui.app.addLog("HELLO")
        time.sleep(1)
