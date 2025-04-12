from intelhex import IntelHex

# Set the allowed flash region for STM32H745
FLASH_START = 0x08000000
FLASH_END   = 0x08200000  # Exclusive upper bound

def crop_hex(input_file, output_file, start=FLASH_START, end=FLASH_END):
    ih = IntelHex(input_file)
    all_addresses = list(ih.addresses())

    print("Scanning all addresses...")

    removed = 0
    for addr in all_addresses:
        if addr < start or addr >= end:
            del ih[addr]
            removed += 1

    print(f"✅ Removed {removed} bytes outside of 0x{start:08X} - 0x{end - 1:08X}")
    print(f"💾 Saving trimmed HEX to: {output_file}")
    ih.write_hex_file(output_file)

if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description="Crop out-of-range sections from Intel HEX")
    # parser.add_argument("input_hex", help="Original .hex file")
    # parser.add_argument("output_hex", help="Cropped .hex file")
    # args = parser.parse_args()

    # crop_hex(args.input_hex, args.output_hex)

    crop_hex('/home/admin/robot/software/bilbo.hex', '/home/admin/robot/software/bilbo_cropped.hex')
