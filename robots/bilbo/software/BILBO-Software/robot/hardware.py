from utils.files import fileExists, deleteFile, relativeToFullPath
from utils.json_utils import readJSON, writeJSON
from paths import config_path

# hardware_definition = {
#     'electronics': {
#         'board_revision': 'v4',
#         'shield': 'bilbo_shield_rev2',
#         'display': 'oled_bw_128x64',
#         'sound': {
#             'active': True,
#             'gain': 1.0,
#         },
#         'buttons': {
#             'primary': {
#                 'exists': True,
#                 'type': 'internal',
#                 'pin': 4,
#                 'led': {
#                     'exists': True,
#                     'type': 'sx1508',
#                     'pin': 1,
#                 }
#             },
#             'secondary': {
#                 'exists': True,
#                 'type': 'internal',
#                 'pin': 5,
#                 'led': {
#                     'exists': True,
#                     'type': 'sx1508',
#                     'pin': 7,
#                 }
#             },
#         },
#         'leds': {},
#         'sensors': {},
#         }
#     }

hardware_definition_big_bilbo = {
    'model': {
        'type': 'big'
    },
    'settings': {
      'theta_offset': math.radians(2.0),
    },
    'electronics': {
        'board_revision': 'v4.1',
        'shield': None,
        'display': 'oled_bw_128x64',
        'sound': {
            'active': False,
            'gain': 0.5,
        },
        'buttons': {
            'primary': {
                'exists': True,
                'type': 'internal',
                'pin': 5,
                'led': {
                    'exists': True,
                    'type': 'internal',
                    'pin': 4,
                }
            },
            'secondary': {
                'exists': False,
            },
        },
        'leds': {},
        'sensors': {},
    }
}

hardware_definition_small_bilbo = {
    'model': {
        'type': 'small'
    },
    'settings': {
        'theta_offset': math.radians(2.0),
    },
    'electronics': {
        'board_revision': 'v4',
        'shield': None,
        'display': 'oled_bw_128x64',
        'sound': {
            'active': False,
            'gain': 0.5,
        },
        'buttons': {
            'primary': {
                'exists': True,
                'type': 'internal',
                'pin': 5,
                'led': {
                    'exists': True,
                    'type': 'internal',
                    'pin': 4,
                }
            },
            'secondary': {
                'exists': False,
            },
        },
        'leds': {},
        'sensors': {},
    }
}


def generate_hardware_definition():
    file = relativeToFullPath(f"{config_path}hardware.json")
    if fileExists(file):
        deleteFile(file)

    writeJSON(file, hardware_definition_big_bilbo)


def get_hardware_definition():
    file = relativeToFullPath(f"{config_path}hardware.json")
    # First check if the files exist
    if fileExists(file):
        return readJSON(file)
    else:
        return None


if __name__ == '__main__':
    generate_hardware_definition()
