import csv
import dataclasses
import json
import time

from robot.logging.bilbo_sample import BILBO_Sample
from utils.time import performance_analyzer
from utils.csv_utils import CSVLogger, read_csv_file
from utils.dataclass_utils import from_dict
def main():
    logger = CSVLogger("log1.csv", custom_text_header=["hello", "World"])

    samples = []
    for i in range(100):
        sample = BILBO_Sample()
        sample.general.tick = i
        sample.control.configuration = "default"
        samples.append(dataclasses.asdict(sample))

    print(len(samples))
    logger.append_data(samples)

    # time.sleep(1)
    data = read_csv_file("log1.csv", meta_lines=2)

    sample1 = data['data'][0]
    # print(sample1)

    x = from_dict(data_class=BILBO_Sample, data=sample1)
    print(BILBO_Sample())
    print(x)
    pass
if __name__ == '__main__':
    main()
