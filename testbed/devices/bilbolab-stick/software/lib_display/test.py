import time

from lib_display.displays import BigDisplay, SmallDisplayRobots


def main():
    disp1 = BigDisplay()
    disp1.init()
    disp1.start()

    disp1.setBridge("Not connected", "RED")
    disp1.setSSID("bilbo_net_stick", "LIGHTGREEN")
    disp1.setPassword("bilbobeutlin", "LIGHTGREEN")

    disp2 = SmallDisplayRobots(1)
    disp2.init()
    disp2.start()

    disp2.setRobots([
        ('bilbo1', '192.168.4.104', "CYAN"),
        ('bilbo2', '192.168.4.104', "CYAN")
    ])

    disp3 = SmallDisplayRobots(2)
    disp3.init()
    disp3.start()

    disp3.setRobots([
        ('bilbo3', '192.168.4.104', "CYAN")
    ])

    while True:
        disp1.updateTime()
        disp1.update()
        disp2.update()
        disp3.update()
        time.sleep(0.8)


if __name__ == '__main__':
    main()