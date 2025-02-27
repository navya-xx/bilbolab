from robot.lowlevel.stm32_sample import bilbo_ll_sample_struct, BILBO_LL_Sample
from utils.ctypes_utils import struct_to_dataclass
from utils.time import performance_analyzer

@performance_analyzer
def convert(instance, dataclass_type):

    return struct_to_dataclass(instance, dataclass_type)

def main():
    struct_instance = bilbo_ll_sample_struct()
    dataclass_instance = convert(struct_instance, BILBO_LL_Sample)
    print(dataclass_instance)

    pass
if __name__ == '__main__':
    main()