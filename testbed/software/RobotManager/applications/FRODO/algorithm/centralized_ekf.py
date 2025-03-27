import dataclasses
import math
import numpy as np
import qmt

from utils.logging_utils import Logger,setLoggerLevel
import pandas as pd

logger = Logger('EKF')
logger.setLevel("INFO")
# ----------------------------------------------------------------------------------------------------------------------
@dataclasses.dataclass
class VisionAgent:
    id: str
    index: int
    state: np.ndarray
    state_covariance: np.ndarray
    input: np.ndarray
    input_covariance: np.ndarray
    measurements: list['VisionAgentMeasurement']


# ----------------------------------------------------------------------------------------------------------------------
@dataclasses.dataclass
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

    step: int = 0

    def __init__(self, Ts):
        self.Ts = Ts

    def init(self, agents: dict[str, VisionAgent]):
        self.agents = agents

        # Build the state:
        self.state = np.zeros(len(agents)*3)
        for i, agent in enumerate(agents.values()):
            self.state[i*3:(i+1)*3] = agent.state

        logger.info(f"State: {self.state}")

        # Build the state covariance
        self.state_covariance = np.zeros((len(agents)*3, len(agents)*3))
        for i, agent in enumerate(agents.values()):
            self.state_covariance[i*3:(i+1)*3, i*3:(i+1)*3] = agent.state_covariance

        logger.info(f"State covariance: {self.state_covariance}")
    # ------------------------------------------------------------------------------------------------------------------
    def update(self):

        # STEP 1: PREDICTION
        x_hat_pre, P_hat_pre = self.prediction()

        # STEP 2: Calculate measurement jacobian
        H = self.measurementJacobian()

        # STEP 3: Calculate the kalman gain
        W = self.buildMeasurementCovariance()
        K = P_hat_pre @ H.T @ np.linalg.inv(H @ P_hat_pre @ H.T + W)

        # STEP 4: Correction
        y = self.buildMeasurementVector()
        y_est = self.measurementPrediction()

        # Calculate the difference between y and y_est
        diff = y - y_est

        # Update the state
        correction_term = K@diff
        new_state = x_hat_pre + K @ diff

        # Update the covariance
        pp = K @ W @ K.T
        min_norm = np.linalg.norm(pp, 'fro')
        new_covariance = (np.eye(len(self.agents)*3) - K @ H) @ P_hat_pre @ (np.eye(len(self.agents)*3) - K @ H).T + K @ W @ K.T

        self.state = new_state
        self.state_covariance = new_covariance

        # Write the state back to the agents
        for i in range(len(self.agents)):
            agent = self.getAgentByIndex(i)
            if agent is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            agent.state = self.state[i*3:(i+1)*3]


        self.step += 1

        if (self.step % 10) == 0 or self.step==1:
            state_str = np.array2string(self.state, precision=2, suppress_small=True)
            print(f"Step: {self.step}, State: {state_str}, State covariance: {np.linalg.norm(self.state_covariance, 'fro'):.2f}")


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

        # Predict the states
        x_hat = np.zeros(len(self.agents)*3)
        for i in range(len(self.agents)):
            agent = self.getAgentByIndex(i)
            if agent is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            x_hat[i*3:(i+1)*3] = self.predictionAgent(agent.state, agent.input)


        # Predict the covariance

        # Calculate the dynamics jacobian
        F = self.dynamicsJacobian()

        # dynamics_noise = np.zeros_like(self.state_covariance)  # TODO
        dynamics_noise = np.eye(3*len(self.agents)) * 0
        P_hat = F @ self.state_covariance @ F.T + dynamics_noise

        return x_hat, P_hat

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
    def dynamicsJacobian(self):
        """
        Calculate the Jacobian matrix of the full system
        Returns:

        """
        J = np.zeros((len(self.agents)*3, len(self.agents)*3))

        for i in range(len(self.agents)):
            agent = self.getAgentByIndex(i)
            if agent is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            J[i*3:(i+1)*3, i*3:(i+1)*3] = self.jacobianAgent(agent.state, agent.input)

        return J
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
            [qmt.wrapToPi(agent_target_state[2] - agent_source_state[2])]
        ]) # TODO: Do i need some wrapping here?
        return h_source_target

    # ------------------------------------------------------------------------------------------------------------------
    def calculatePredictionCovariance(self, state_covariance, dynamics_jacobian, dynamics_noise_covariance):
        return dynamics_jacobian @ state_covariance @ dynamics_jacobian.T + dynamics_noise_covariance

    # ------------------------------------------------------------------------------------------------------------------
    def measurementJacobian(self):

        H = np.zeros((3*(len(self.agents)**2), 3*len(self.agents)))

        for i in range(len(self.agents)):
            sub_H = np.zeros((3*len(self.agents), 3*len(self.agents)))

            for ii in range(len(self.agents)):
                for jj in range(len(self.agents)):
                    if i ==  ii:
                        continue

                    if jj == i:
                        H_agent = self.measurementJacobianAgents(self.getAgentByIndex(i), self.getAgentByIndex(ii), 1)
                        pass
                    elif ii == jj:
                        H_agent = self.measurementJacobianAgents(self.getAgentByIndex(i), self.getAgentByIndex(jj), 2)
                        pass
                    else:
                        continue

                    sub_H[3*ii:3*(ii+1), 3*jj:3*(jj+1)] = H_agent
                    pass


            pass
            H[3*len(self.agents)*i:3*len(self.agents)*(i+1), :] = sub_H
            pass
        return H



    # ------------------------------------------------------------------------------------------------------------------
    def measurementJacobianAgents(self, agent1, agent2, reference_agent):
        assert(reference_agent in [1, 2])

        if reference_agent == 1:
            psi_1 = agent1.state[2]
            x_1 = agent1.state[0]
            y_1 = agent1.state[1]
            x_2 = agent2.state[0]
            y_2 = agent2.state[1]
            H = np.array([
                [-np.cos(psi_1), -np.sin(psi_1), -np.sin(psi_1) * (x_2 - x_1) + np.cos(psi_1) * (y_2 - y_1)],
                [np.sin(psi_1), -np.cos(psi_1), -np.cos(psi_1) * (x_2 - x_1) - np.sin(psi_1) * (y_2 - y_1)],
                [0, 0, -1]
            ])

            pass

        elif reference_agent == 2:
            psi_1 = agent1.state[2]
            H = np.array([
                [np.cos(psi_1) , np.sin(psi_1) , 0,],
                [-np.sin(psi_1), np.cos(psi_1) , 0,],
                [0, 0, 1]
            ])
        else:
            return None
        return H

    # ------------------------------------------------------------------------------------------------------------------
    def measurementPrediction(self):

        prediction_vector = np.zeros(3*len(self.agents)**2)

        for i in range(len(self.agents)):
            agent_from = self.getAgentByIndex(i)
            if agent_from is None:
                raise ValueError(f"Agent with index {i} does not exist.")
            for j in range(len(self.agents)):
                agent_to = self.getAgentByIndex(j)
                if agent_to is None:
                    raise ValueError(f"Agent with index {j} does not exist.")

                if i == j:
                    continue

                predicted_measurement = self.measurementPredictionAgent(agent_from.state, agent_to.state)
                prediction_vector[i*len(self.agents)*3 + 3*j:i*len(self.agents)*3 + 3*(j+1)] = predicted_measurement.flatten()
                pass
            
        return prediction_vector
    # ------------------------------------------------------------------------------------------------------------------
    def buildMeasurementVector(self):

        y = np.zeros(3*len(self.agents)**2)
        for i in range(len(self.agents)):
            agent_from = self.getAgentByIndex(i)
            if agent_from is None:
                raise ValueError(f"Agent with index {i} does not exist.")

            for j in range(len(self.agents)):
                agent_to = self.getAgentByIndex(j)
                if agent_to is None:
                    raise ValueError(f"Agent with index {j} does not exist.")

                if i == j:
                    continue

                # Check if agent from has a measurement to agent_to in its measurements
                measurement_found = False
                measurement: VisionAgentMeasurement = None
                for m in agent_from.measurements:
                    if m.target_index == j:
                        measurement_found = True
                        measurement = m
                        break

                if measurement_found:

                    y[i*len(self.agents)*3 + 3*j:i*len(self.agents)*3 + 3*(j+1)] = measurement.measurement
                else:
                    continue

        return y

    def buildMeasurementCovariance(self):

        value_measurement_exists = 1e-5
        value_measurement_not_exists = 1e9

        W = np.zeros((3*len(self.agents)**2, 3*len(self.agents)**2))


        for i in range(len(self.agents)):
            agent_from = self.getAgentByIndex(i)
            if agent_from is None:
                raise ValueError(f"Agent with index {i} does not exist.")

            for j in range(len(self.agents)):
                agent_to = self.getAgentByIndex(j)
                if agent_to is None:
                    raise ValueError(f"Agent with index {j} does not exist.")

                offset = len(self.agents) * 3 * i

                if i == j:
                    W[offset+3*j:offset+3*(j+1), offset+3*j:offset+3*(j+1)] = np.eye(3)*value_measurement_not_exists
                    continue

                measurement_found = False
                measurement: VisionAgentMeasurement = None
                for m in agent_from.measurements:
                    if m.target_index == j:
                        measurement_found = True
                        measurement = m
                        break


                if measurement_found:
                    W[offset+3*j:offset+3*(j+1), offset+3*j:offset+3*(j+1)] = np.eye(3)*value_measurement_exists
                else:
                    W[offset+3*j:offset+3*(j+1), offset+3*j:offset+3*(j+1)] = np.eye(3)*value_measurement_not_exists

        return W
    # ------------------------------------------------------------------------------------------------------------------
    def getAgentByIndex(self, index: int) -> (VisionAgent, None):
        for agent in self.agents.values():
            if agent.index == index:
                return agent
        return None

    # ------------------------------------------------------------------------------------------------------------------
    def getAgentIndex(self, id: str) -> (int, None):
        for i, agent in enumerate(self.agents.values()):
            if agent.id == id:
                return i
