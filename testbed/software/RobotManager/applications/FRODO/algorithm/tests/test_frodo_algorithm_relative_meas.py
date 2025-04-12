import math
import time

import numpy as np

from applications.FRODO.algorithm.centralized_ekf_old import CentralizedLocationAlgorithm, VisionAgent, \
    VisionAgentMeasurement
from applications.FRODO.simulation.frodo_simulation import FRODO_Simulation, FRODO_ENVIRONMENT_ACTIONS


class FRODO_Algorithm_Simulated:
    simulation: FRODO_Simulation
    algorithm: CentralizedLocationAlgorithm

    def __init__(self, ):

        self.simulation = FRODO_Simulation()
        self.simulation.env.scheduling.actions[FRODO_ENVIRONMENT_ACTIONS.ESTIMATION].addAction(self.estimation)
        self.algorithm = CentralizedLocationAlgorithm(Ts=self.simulation.env.scheduling.Ts)

    def init(self, agents: dict[str, dict]):
        self.simulation.init()

        vision_agents_algorithm = {}
        index = 0
        for name, agent_data in agents.items():
            agent = self.simulation.addVirtualAgent(id=name, fov_deg=agent_data["fov_deg"],
                                                    view_range=agent_data["view_range"])
            agent.setPosition(agent_data["position"])
            agent.setConfiguration(dimension='psi', value=agent_data["psi"])

            vision_agents_algorithm[name] = VisionAgent(
                id=name,
                index=index,
                state=np.array([agent.state['pos']['x'], agent.state['pos']['y'],
                                agent.state['psi'].value]) if agent_data['leader'] else np.array(
                    agent_data['initial_guess']),
                state_covariance=np.diag(np.asarray(agent_data['uncertainty'])),
                input=np.array([0, 0]),
                input_covariance=np.eye(2) * 0,
                measurements=[],
            )
            index += 1

        self.algorithm.init(vision_agents_algorithm)

    def start(self, *args, **kwargs):
        self.simulation.start(*args, **kwargs)

    def estimation(self):
        # Collect the data from the agents for the estimation
        for name, agent in self.simulation.agents.items():
            self.algorithm.agents[name].measurements = []
            for _, data in agent.measurements.items():
                algorithm_measurement = VisionAgentMeasurement(
                    source=name,
                    source_index=self.algorithm.getAgentIndex(name),
                    target=data.agent_id,
                    target_index=self.algorithm.getAgentIndex(data.agent_id),
                    measurement=np.array([data.vec[0], data.vec[1], data.psi]),
                    measurement_covariance=np.eye(3) * 1e-8
                )
                # print(f"{name}->{data.agent_id}: {algorithm_measurement}")
                self.algorithm.agents[name].measurements.append(algorithm_measurement)

        # Update the algorithm
        self.algorithm.update()


# source: str
# source_index: int
# target: str
# target_index: int
# measurement: np.ndarray
# measurement_covariance: np.ndarray

def test_frodo_algorithm():
    agents = {
        'frodo1_v': {
            'fov_deg': 120,
            'view_range': 2,
            'position': [0, 0],
            'initial_guess': [0, 0, 0],
            'psi': 0,
            'uncertainty': [1e-6, 1e-6, 1e-6],
            'leader': True
        },
        'frodo2_v': {
            'fov_deg': 30,
            'view_range': 1.5,
            'position': [0.5, 0.5],
            'initial_guess': [0, 0, 0],
            'psi': math.radians(135),
            'uncertainty': [1e2, 1e2, 1e3],
            'leader': False
        },
        'frodo3_v': {
            'fov_deg': 40,
            'view_range': 1.5,
            'position': [0, 1],
            'initial_guess': [0, 0, 0],
            'psi': math.radians(-90),
            'uncertainty': [1e2, 1e2, 1e3],
            'leader': False
        },
    }

    app = FRODO_Algorithm_Simulated()
    app.init(agents)
    app.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    test_frodo_algorithm()
