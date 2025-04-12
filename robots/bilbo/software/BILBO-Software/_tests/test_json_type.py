import orjson as json

import numpy


def main():
    int_type = int
    dict_type = dict

    data = {
      'a': numpy.float64(15)
    }

    data_serialized = json.dumps(data)
    data_deserialized = json.loads(data_serialized)

    print(data_deserialized)


if __name__ == '__main__':
    main()
