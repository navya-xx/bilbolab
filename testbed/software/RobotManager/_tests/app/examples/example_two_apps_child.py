import time

from _tests.app.control_app import ControlApp, WidgetGroup, Button, SliderWidget, RootGroup


def example_two_apps_child():
    # app = ControlApp(app_id='child', port=9002, mdns_name='app2', parent_address='192.168.8.115', parent_port=9001)
    app = ControlApp('child', port=9002, mdns_name='app2', parent_address='example.local', parent_port=80)

    root_group = RootGroup(group_id="rootz", pages=2)
    btn1 = root_group.addWidget(Button("btn1", "BX ", [0.5, 0.2, 0.34], textcolor=[0, 0, 0]))
    slider1 = SliderWidget(widget_id='slider1',
                           title='Slider',
                           precision=0,
                           min_value=0,
                           max_value=100,
                           current_value=50,
                           color=[0.5,0,0.1])

    root_group.addWidget(slider1)
    index = 0

    def change_button_1():
        nonlocal index, btn1
        btn1.set_text(f"{index}")
        index += 1

    btn1.callbacks.clicked.register(change_button_1)

    app.init(root_group)
    app.run_in_thread()

    sub_group = WidgetGroup("subz", pages=2)
    btn2 = sub_group.addWidget(Button('btn2', "B2"))

    root_group.addGroup(sub_group)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    example_two_apps_child()
