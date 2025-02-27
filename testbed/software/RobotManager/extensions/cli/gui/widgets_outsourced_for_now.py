# ======================================================================================================================
class RobotsWidget(Widget):

    def __init__(self, *args, **kwargs):
        self.log_function = None
        self.overview_table = None  # Store a reference to the table
        self.robot_rows = {}  # Store references to each row for easy updating
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield TabbedContent(id="robots-tabs")

    def update_robots(self, robots: dict):
        """Dynamically update the table rows without redrawing everything."""
        tabs = self.query_one("#robots-tabs", TabbedContent)

        # If table doesn't exist, create it and add a single overview tab
        if not self.overview_table:
            overview_pane = TabPane("Overview", id="overview")
            tabs.add_pane(overview_pane)

            overview_content = Vertical()
            overview_pane.mount(overview_content)

            # Create table only once
            self.overview_table = DataTable()
            self.overview_table.add_column("Robot ID")
            self.overview_table.add_column("Status", key='status')
            self.overview_table.add_column("Position [x]", key='x')
            self.overview_table.add_column("Position [y]", key='y')
            self.overview_table.add_column("Orientation [psi]", key='psi')
            overview_content.mount(self.overview_table)

        # Dynamically update or add rows
        for robot_id, robot_data in robots.items():
            status = str(robot_data.get("status", "unknown"))
            x = str(robot_data.get("x", 0))
            y = str(robot_data.get("y", 0))
            orientation = str(robot_data.get("psi", 0))

            if robot_id in self.overview_table.rows:
                # Update existing row
                self.overview_table.update_cell(robot_id, 'status', status)
                self.overview_table.update_cell(robot_id, 'x', x)
                self.overview_table.update_cell(robot_id, 'y', y)
                self.overview_table.update_cell(robot_id, 'psi', orientation)
            else:
                # Add new row and store index
                self.overview_table.add_row(*[robot_id, status, x, y, orientation], key=robot_id)

        # If robots are removed from the data, delete rows accordingly
        # existing_robot_ids = set(self.robot_rows.keys())
        # new_rbot_ids = set(robots.keys())
        #
        # for robot_id in existing_robot_ids - new_robot_ids:
        #     row_index = self.robot_rows.pop(robot_id)
        #     self.overview_table.rows.pop(row_index)

        self.refresh()  # Trigger a UI update


class OverviewWidget2(Widget):
    log_output = None

    def compose(self) -> ComposeResult:
        with Vertical():
            with Collapsible(title="Buttons"):
                yield VerticalScroll(
                    Static("Standard Buttons", classes="header"),
                    Button("Default"),
                    Button("Primary!", variant="primary"),
                    Button.success("Success!", id="button123456"),
                    Button.warning("Warning!"),
                    Button.error("Error!"),
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.log_output:
            self.log_output(str(event.button))
