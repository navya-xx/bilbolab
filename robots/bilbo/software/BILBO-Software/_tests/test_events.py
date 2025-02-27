from robot.logging.bilbo_sample import BILBO_Sample
from robot.lowlevel.stm32_sample import bilbo_ll_sample_struct
from utils.python_utils import is_immutable
from utils.dataclass_utils import freeze_dataclass_instance

def main():
    # sample = TWIPR_Sample()
    # sample_freeze = freeze_dataclass_instance(sample)
    # print(is_immutable(sample))
    # print(is_immutable(sample_freeze))
    sample_ll = bilbo_ll_sample_struct()

    print(is_immutable(sample_ll))
    ...

if __name__ == '__main__':
    main()