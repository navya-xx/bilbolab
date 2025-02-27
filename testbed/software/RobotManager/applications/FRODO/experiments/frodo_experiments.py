import datetime
import json
import os
import qmt
import time


from applications.FRODO.tracker.assets import TrackedAsset, TrackedVisionRobot, vision_robot_application_assets, \
    TrackedOrigin
from applications.FRODO.tracker.tracker import Tracker
from extensions.cli.src.cli import Command, CommandSet, CommandArgument
from robots.frodo.frodo_manager import FrodoManager
from utils.logging_utils import Logger

INPUT_FILE_PATH = "./applications/FRODO/experiments/input/"
OUTPUT_FILE_PATH = "./applications/FRODO/experiments/output/"

POSITION_TOLERANCE = 0.10   #[m]
PSI_TOLERANCE = 0.17    #[rad]; ~10°


logger = Logger('EXPERIMENT_HANDLER')
logger.setLevel('INFO')


class FRODO_ExperimentHandler:
    manager                 : FrodoManager
    tracker                 : Tracker

    config                  : json
    agents                  : list
    movements               : list

    experiment_name         : str
    output_directory_path   : str

    def __init__(self, manager : FrodoManager, tracker : Tracker):
        self.manager = manager
        self.tracker = tracker
        self.agents = []
        self.output_directory_path = None
        self.experiment_name = None

    def checkConsistency(self):
        check_passed = True

        tracked_assets = self.config['requirements']['tracked_assets']
        required_agents = self.config['requirements']['agents'].keys()
        required_statics = self.config['requirements']['statics'].keys()
        algorithm_agents = self.config['algorithm']['agents'].keys()
        algorithm_statics = self.config['algorithm']['statics'].keys()
        movement_agents = self.config['movement'].keys()
        
        for agent in required_agents:
            '''Check if required agents appear in all config parts'''
            if not agent in tracked_assets:
                logger.info(f"Found required agent {agent} that is not \
                                part of requirements::tracked_assets!")
                check_passed = False
            if not agent in algorithm_agents:
                logger.info(f"Found required agent {agent} that is not \
                                part of algorithm::agents!")
                check_passed = False
            if not agent in movement_agents:
                logger.info(f"Found required agent {agent} that is not \
                                part of movement!")
                check_passed = False
                    
            if check_passed:
                self.agents.append(agent)
        
        for static in required_statics:
            '''Check if required agents appear in all config parts'''
            if not static in tracked_assets:
                logger.info(f"Found required static {static} that is not \
                                part of requirements::tracked_assets!")
                check_passed = False
            if not static in algorithm_statics:
                logger.info(f"Found required static {static} that is not \
                                part of algorithm::statics!")
                check_passed = False

        return check_passed



    def checkRequiredPositions(self):

        if not self.tracker:
            return True

        check_passed = True
        required_assets = self.config['requirements']['tracked_assets']
        required_statics = self.config['requirements']['statics'].keys()

        for asset_str in required_assets:
            try:
                asset_type = "agents"
                if asset_str in required_statics:
                    asset_type = "statics"

                if asset_str not in self.tracker.assets:
                    logger.warning(f"Required asset {asset_str} not part of OptiTrack Data!")
                    check_passed = False
                    continue
                
                asset = self.tracker.assets[asset_str]

                if not asset.tracking_valid:
                    logger.warning(f"Required asset {asset_str} not visible to OptiTrack!")
                    check_passed = False
                    continue

                asset_pos = asset.position.tolist()

                required_pos = self.config['requirements'][asset_type][asset_str]['position']
                for i in range(2):
                    delta_pos = abs(required_pos[i] - asset_pos[i])
                    if delta_pos > POSITION_TOLERANCE:
                        logger.warning(f"Required asset {asset_str} not in the right position!\n \
                                       Required: {required_pos}, found: {asset_pos}")
                        check_passed = False
                        break
                    
                if isinstance(asset, TrackedVisionRobot) and asset_type == "agents":
                    asset_psi = asset.psi

                    required_psi = self.config['requirements'][asset_type][asset_str]['psi']

                    delta_psi = abs(required_psi - asset_psi)
                    delta_psi = float(qmt.wrapToPi(delta_psi))
                    if delta_psi > PSI_TOLERANCE:
                        logger.warning(f"Required agent {asset_str} not correctly turned!\n \
                                       Required: {required_psi}, found: {asset_psi}")
                        check_passed = False
            except Exception as e:
                logger.info(f"Asset {asset_str} not correctly defined: Problem with {e}")

        return check_passed
            

    def loadMovements(self):
        '''Write movement lists to robots'''
        for agent in self.agents:
            if agent not in self.manager.robots:
                logger.warning(f"Agent {agent} not known to Frodo Manager, skipping {agent} in experiment.")
                continue

            movements_since_last_repeat = []
            if self.config['movement'][agent]['mode'] == 'managed':
                self.manager.robots[agent].setControlMode(3)
                for idx in range(len(self.config['movement'][agent]['movements'])):
                    time.sleep(0.1)
                    movement = self.config['movement'][agent]['movements'][str(idx)]
                    try:
                        if movement['description'] == 'wait':
                            movements_since_last_repeat.append([0,0,movement['time_s']])
                            self.manager.robots[agent].addMovement(dphi=0, radius=0, time=movement['time_s'])
                        elif movement['description'] == 'move':
                            movements_since_last_repeat.append([movement['psi'],movement['radius_mm'],movement['time_s']])
                            self.manager.robots[agent].addMovement(dphi=movement['psi'], radius=movement['radius_mm'],  time=movement['time_s'])
                        elif movement['description'] == 'repeat':
                            for i in range(movement['count']):
                                for move in movements_since_last_repeat:
                                    self.manager.robots[agent].addMovement(dphi=move[0], radius=move[1], time=move[2])
                        else:
                            logger.info(f"Unknown movement description, skipping {movement['description']} of {agent}")
                    except Exception as e:
                        logger.info(f"Problem trying to load movement {idx} of agent {agent}: {e}\nSkipping!")
                        continue

            elif self.config['movement'][agent]['mode'] == "external":
                self.manager.robots[agent].setControlMode(2)
            else:
                self.manager.robots[agent].setControlMode(1)

    def createOutputFolder(self):
        '''Create output folder for experiment.\n
        If already exists: add -index'''
        if not os.path.exists(OUTPUT_FILE_PATH):
            logger.warning(f"Experiment output folder does not exist. \n \
                            Please check if {OUTPUT_FILE_PATH} is at the right location!")
        experiment_name = self.config['id']
        if not os.path.exists(OUTPUT_FILE_PATH + experiment_name):
            self.experiment_name = experiment_name
            self.output_directory_path = OUTPUT_FILE_PATH + experiment_name
            os.mkdir(self.output_directory_path)
            logger.info(f"Created output directory: {OUTPUT_FILE_PATH + experiment_name}")
        else:
            i = 1
            while True:
                if not os.path.exists(OUTPUT_FILE_PATH + experiment_name + "-" + str(i)):
                    break
                i += 1
            self.experiment_name = experiment_name + "-" + str(i)
            self.output_directory_path = OUTPUT_FILE_PATH + self.experiment_name
            os.mkdir(self.output_directory_path)
            logger.info(f"Repition of Experiment {experiment_name}\n \
                        Created output directory: {OUTPUT_FILE_PATH + self.experiment_name}")
        with open(self.output_directory_path + "/" + self.experiment_name + ".json", "w") as file:
            self.config['date'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            json.dump(self.config, file, indent=4)

    def startMovements(self):
        for agent in self.agents:
            if agent in self.manager.robots:
                self.manager.robots[agent].startNavigationMovement()

    def pauseMovements(self):
        for agent in self.agents:
            if agent in self.manager.robots:
                self.manager.robots[agent].pauseNavigationMovement()

    def continueMovements(self):
        for agent in self.agents:
            if agent in self.manager.robots:
                self.manager.robots[agent].continueNavigationMovement()

    def stopExperiment(self):
        for agent in self.agents:
            if agent in self.manager.robots:
                self.manager.robots[agent].stopNavigationMovement()
                self.manager.robots[agent].clearNavigationMovementQueue()


    def startExperiment(self, file_name : str):
        self.agents = []
        with open(INPUT_FILE_PATH + file_name, 'r') as file:
            self.config = json.load(file)
        if self.checkConsistency() and self.checkRequiredPositions():
            self.loadMovements()
            self.createOutputFolder()
            self.startMovements()
        logger.info("Finished Experiment Setup, starting!")


class FRODO_Experiments_CLI(CommandSet):

    def __init__(self, experiment_handler: FRODO_ExperimentHandler):
        self.experiment_handler = experiment_handler
        start_experiment_command = Command(name='start', description='Start a new experiment',
                                           callback=self.startExperiment,
                                           arguments=[CommandArgument(name='file',
                                                                      short_name='f',
                                                                      type=str)],
                                                                      allow_positionals=True)

        pause_experiment_command = Command(name='pause', description='Pause the running experiment',
                                           callback=self.pauseExperiment,
                                           arguments=[]
                                           )

        continue_experiment_command = Command(name='continue', description='Continue the paused experiment',
                                           callback=self.continueExperiment,
                                           arguments=[]
                                           )


        stop_experiment_command = Command(name='stop', description='Stop the running experiment',
                                           callback=self.stopExperiment,
                                           arguments=[]
                                           )


        super().__init__(name='experiments', commands=[start_experiment_command,
                                                       pause_experiment_command,
                                                       continue_experiment_command,
                                                       stop_experiment_command])

    def startExperiment(self, file):
        self.experiment_handler.startExperiment(file)
        return f"Start Experiment {file}"

    def pauseExperiment(self):
        self.experiment_handler.pauseMovements()

    def continueExperiment(self):
        self.experiment_handler.continueMovements()

    def stopExperiment(self):
        self.experiment_handler.stopExperiment()

