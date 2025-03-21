import math

import numpy as np


# ----------------------------------------------------------------------------------------------------------------------
class VisionAgent:
    id: str
    index: int
    state: np.ndarray
    state_covariance: np.ndarray
    input: np.ndarray
    input_covariance: np.ndarray
    measurements: list['VisionAgentMeasurement']


# ----------------------------------------------------------------------------------------------------------------------
class VisionAgentMeasurement:
    source: str
    source_index: int
    target: str
    target_index: int
    measurement: np.ndarray
    measurement_covariance: np.ndarray


# ----------------------------------------------------------------------------------------------------------------------
class CentralizedLocationAlgorithm:
    agents: dict[str, VisionAgent]

    Ts: float
    state: np.ndarray
    state_covariance: np.ndarray

    def __init__(self, Ts):
        self.Ts = Ts

    # ------------------------------------------------------------------------------------------------------------------
    def update(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def addAgent(self, agent: VisionAgent):
        self.agents[agent.id] = agent

    # ------------------------------------------------------------------------------------------------------------------
    def removeAgent(self, agent: VisionAgent):
        del self.agents[agent.id]

    # ------------------------------------------------------------------------------------------------------------------
    def predictionAgent(self, state: np.ndarray, input: np.ndarray):
        """
        Prediction step of one agent
        Args:
            state: State of the agent
            input: Input to the agent

        Returns:

        """
        state_hat = np.array([
            state[0] + self.Ts * input[0] * math.cos(state[2]),
            state[1] + self.Ts * input[0] * math.sin(state[2]),
            state[2] + self.Ts * input[1]
        ])
        return state_hat

    # ------------------------------------------------------------------------------------------------------------------
    def enumerateAgentArray(self):
        """
        Enumerate the agents in the array
        Returns:

        """
        for i, agent in enumerate(self.agents.values()):
            agent.index = i

    # ------------------------------------------------------------------------------------------------------------------
    def prediction(self):
        """
        Calculate the prediction of the full system
        Returns:

        """
        x_hat = np.zeros(len(self.agents)*3)

        for i in range(len(self.agents)):
            agent = self._getAgentByIndex(i)
            if agent is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            x_hat[i*3:(i+1)*3] = self.predictionAgent(agent.state, agent.input)

    # ------------------------------------------------------------------------------------------------------------------
    def jacobianAgent(self, state: np.ndarray, input: np.ndarray):
        """
        Calculate the Jacobian matrix of the agent's motion model
        Args:
            state:
            input:

        Returns:

        """
        F = np.array([
            [1, 0, -self.Ts * input[0] * math.sin(state[2])],
            [0, 1, self.Ts * input[0] * math.cos(state[2])],
            [0, 0, 1]
        ])
        return F

    # ------------------------------------------------------------------------------------------------------------------
    def jacobian(self):
        """
        Calculate the Jacobian matrix of the full system
        Returns:

        """
        J = np.zeros((len(self.agents)*3, len(self.agents)*3))

        for i in range(len(self.agents)):
            agent = self._getAgentByIndex(i)
            if agent is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            J[i*3:(i+1)*3, i*3:(i+1)*3] = self.jacobianAgent(agent.state, agent.input)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def measurementPredictionAgent(agent_source_state, agent_target_state):
        """
        Prediction for one agent for the measurement model
        Args:
            agent_source_state:
            agent_target_state:

        Returns:

        """
        h_source_target = np.array([
            [math.cos(agent_source_state[2]) * (agent_target_state[0] - agent_source_state[0]) + math.sin(
                agent_source_state[2]) * (agent_target_state[1] - agent_source_state[1])],
            [-math.sin(agent_source_state[2]) * (agent_target_state[0] - agent_source_state[0]) + math.cos(
                agent_source_state[2]) * (agent_target_state[1] - agent_source_state[1])],
            [agent_target_state[2] - agent_source_state[2]]
        ])
        return h_source_target

    # ------------------------------------------------------------------------------------------------------------------
    def calculatePredictionCovariance(self, state_covariance, dynamics_jacobian, dynamics_noise_covariance):
        return dynamics_jacobian @ state_covariance @ dynamics_jacobian.T + dynamics_noise_covariance

    # ------------------------------------------------------------------------------------------------------------------
    def measurementPrediction(self):
        ...

    # ------------------------------------------------------------------------------------------------------------------
    def _getAgentByIndex(self, index: int) -> (VisionAgent, None):
        for agent in self.agents.values():
            if agent.index == index:
                return agent
        return None
