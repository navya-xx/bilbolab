import json


def main():
    int_type = int
    dict_type = dict

    data = {
        "int": int_type,
        "dict": dict_type
    }

    data_serialized = json.dumps(data)
    data_deserialized = json.loads(data_serialized)

    print(data_deserialized)

if __name__ == '__main__':
    main()