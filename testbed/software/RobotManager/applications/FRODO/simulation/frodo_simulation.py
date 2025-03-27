import dataclasses
import enum
import math
import time

import numpy as np
import qmt
from paramiko import agent

import extensions.simulation.src.core as core
from applications.FRODO.simulation.frodo_simulation_utils import frodo_virtual_agent_colors, is_in_fov
from applications.FRODO.utilities.web_gui.FRODO_Web_Interface import FRODO_Web_Interface, Group, VisionAgent
from extensions.simulation.src.core.environment import BASE_ENVIRONMENT_ACTIONS
from extensions.simulation.src.objects.base_environment import BaseEnvironment
from extensions.simulation.src.objects.frodo import FRODO_DynamicAgent
from utils.logging_utils import Logger


# ======================================================================================================================
class FRODO_ENVIRONMENT_ACTIONS(enum.StrEnum):
    MEASUREMENT = 'frodo_measurement'
    COMMUNICATION = 'frodo_communication'
    ESTIMATION = 'frodo_estimation'


# ======================================================================================================================
class FrodoEnvironment(BaseEnvironment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = Logger('FRODO ENV')
        self.logger.setLevel('INFO')

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.MEASUREMENT,
                               object=self,
                               function=self.action_measurement,
                               priority=31,
                               parent=self.scheduling.actions['objects'])

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.COMMUNICATION,
                               object=self,
                               function=self.action_frodo_communication,
                               priority=32,
                               parent=self.scheduling.actions['objects'])

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.ESTIMATION,
                               object=self,
                               function=self.action_estimation,
                               priority=33,
                               parent=self.scheduling.actions['objects'])

    def start(self, *args, **kwargs):
        self.logger.info("Starting FRODO Simulation Environment")
        super().start(*args, **kwargs)

    def action_measurement(self):
        self.logger.debug(f"{self.scheduling.tick}: Action Frodo Measurement")

    def action_frodo_communication(self):
        self.logger.debug(f"{self.scheduling.tick}: Action Frodo Communication")

    def action_estimation(self):
        self.logger.debug(f"{self.scheduling.tick}: Action Frodo Estimation")


# ======================================================================================================================

@dataclasses.dataclass
class FRODO_Agent_Measurement:
    agent_id: str
    vec: np.ndarray
    psi: float


class FRODO_VisionAgent(FRODO_DynamicAgent):
    fov: float
    view_range: float
    measurements: dict[str, FRODO_Agent_Measurement]

    def __init__(self, fov_deg=120, view_range=1.5, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fov = math.radians(fov_deg)
        self.view_range = view_range

        self.logger = Logger(self.agent_id)
        self.logger.setLevel('INFO')

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.MEASUREMENT,
                               object=self,
                               function=self.action_measurement,
                               priority=1)

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.COMMUNICATION,
                               object=self,
                               function=self.action_frodo_communication,
                               priority=2)

        core.scheduling.Action(action_id=FRODO_ENVIRONMENT_ACTIONS.ESTIMATION,
                               object=self,
                               function=self.action_estimation,
                               priority=3)

        # self.scheduling.actions[BASE_ENVIRONMENT_ACTIONS.OUTPUT].addAction(self.print_state)

        self.input = [0, 0]

    def action_measurement(self):
        self.logger.debug(f"{self.scheduling.tick}: ({self.agent_id}) Action Frodo Measurement")

        # Loop over other agents in environment
        other_agents = {
            agent_id: other_agent
            for agent_id, other_agent in self.env.agents.items()
            if self.agent_id != other_agent.agent_id
        }

        self.measurements = {}

        for agent_id, other_agent in other_agents.items():
            ...
            in_fov = is_in_fov(pos=self.configuration['pos'].value,
                               psi=self.configuration['psi'].value,
                               fov=self.fov,
                               radius=self.view_range,
                               other_agent_pos=other_agent.configuration['pos'].value)

            if in_fov:

                vec = other_agent.configuration['pos'].value - self.configuration['pos'].value
                psi = qmt.wrapToPi(other_agent.configuration['psi'].value - self.configuration['psi'].value)

                # Transform vec into agent's coordinate system
                own_psi = self.configuration['psi'].value

                R = np.array([
                    [math.cos(own_psi), math.sin(own_psi)],
                    [-math.sin(own_psi), math.cos(own_psi)]
                ])

                vec_transformed = R @ vec

                measurement = FRODO_Agent_Measurement(
                    agent_id=other_agent.agent_id,
                    vec=vec_transformed,
                    psi=psi
                )

                self.measurements[other_agent.agent_id] = measurement

    def action_frodo_communication(self):
        self.logger.debug(f"{self.scheduling.tick}: ({self.agent_id}) Action Frodo Communication")

    def action_estimation(self):
        self.logger.debug(f"{self.scheduling.tick}: ({self.agent_id}) Action Frodo Estimation")

    def _onAdd_callback(self):
        self.logger.info(f"{self.agent_id} added to Environment")
        super()._onAdd_callback()

    def print_state(self):
        self.logger.info(f"state: {self.configuration}")


# ======================================================================================================================
class FRODO_Simulation:
    env: FrodoEnvironment
    agents: dict[str, FRODO_VisionAgent]
    web_interface: FRODO_Web_Interface

    virtual_agents_plotting_group: Group

    def __init__(self, Ts=0.05):
        self.env = FrodoEnvironment(Ts, run_mode='rt')
        self.agents = {}
        self.web_interface = FRODO_Web_Interface()

        self.logger = Logger('FRODO SIM')
        self.logger.setLevel('INFO')

        self.virtual_agents_plotting_group = None

        self.env.scheduling.actions[BASE_ENVIRONMENT_ACTIONS.OUTPUT].addAction(self._update_webinterface)

    # === METHODS ======================================================================================================
    def init(self):
        self.env.init()
        self._init_webinterface()

    def start(self, steps=None):
        self.web_interface.start()
        self.env.start(steps, thread=True)

    def addVirtualAgent(self, id: str, fov_deg=120, view_range=1.5):
        self.logger.info(f"Add Virtual Agent: {id}")

        # Add the agent to the simulation
        self.agents[id] = FRODO_VisionAgent(agent_id=id, Ts=self.env.Ts, fov_deg=fov_deg, view_range=view_range)
        self.env.addObject(self.agents[id])

        # Add the agent to the plotter
        group = self.virtual_agents_plotting_group.add_group(id)
        group.add_vision_agent(
            id=id,
            position=[0, 0],
            psi=0,
            vision_radius=self.agents[id].view_range,
            vision_fov=self.agents[id].fov,
            color=frodo_virtual_agent_colors[id] if id in frodo_virtual_agent_colors else [0.5, 0.5, 0.5]
        )
        return self.agents[id]

    def removeVirtualAgent(self, id: str):
        self.logger.info(f"Remove Virtual Agent: {id}")
        self.env.removeObject(self.agents[id])
        del self.agents[id]

    def _init_webinterface(self):
        self.virtual_agents_plotting_group = self.web_interface.add_group('Virtual Agents')
        self.web_interface.add_rectangle(
            id='env',
            mid=[0, 0],
            x=3,
            y=3,
            fill=[0.9, 0.9, 0.9],
        )

    def _update_webinterface(self):

        for id, agent in self.agents.items():
            group = self.virtual_agents_plotting_group.get_element_by_id(id)
            if group is None:
                continue

            plotting_agent = group.get_element_by_id(id)

            if plotting_agent is not None:
                # Update the agent position
                plotting_agent.position[0] = agent.configuration['pos'][0]
                plotting_agent.position[1] = agent.configuration['pos'][1]
                plotting_agent.psi = agent.configuration['psi'].value

                # # Add measurement line
                valid_lines_ids = []
                for other_agent_id, measurement in agent.measurements.items():
                    line_id = f"{agent.agent_id}_{other_agent_id}"
                    valid_lines_ids.append(line_id)

                # Remove non-valid lines
                remove_lines = []
                for line_id in group.lines:
                    if line_id not in valid_lines_ids:
                        remove_lines.append(line_id)

                for line_id in remove_lines:
                    group.lines.pop(line_id)

                for other_agent_id, measurement in agent.measurements.items():
                    line_id = f"{agent.agent_id}_{other_agent_id}"
                    if line_id not in group.lines:
                        other_agent_group = self.virtual_agents_plotting_group.get_element_by_id(other_agent_id)
                        other_agent_plot_element = other_agent_group.get_element_by_id(other_agent_id)
                        group.add_line(id=line_id,
                                       start=plotting_agent,
                                       end=other_agent_plot_element,
                                       color=[0.5, 0.5, 0.5])


def main():
    app = FRODO_Simulation()
    app.init()
    app.start()

    ag1 = app.addVirtualAgent("frodo1_v")
    ag2 = app.addVirtualAgent("frodo2_v")
    ag3 = app.addVirtualAgent("frodo3_v", view_range=4)
    ag1.input = [0.5, 0.5]
    ag2.setPosition([0, 1])

    ag3.setPosition([0, -1])
    ag3.setConfiguration(dimension='psi', value=math.pi / 2)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
