#!/usr/bin/env python3

from yolo_evm.runner import run

import sys
import json
import os


def main():
    if len(sys.argv) != 2:
        print("Usage: {} <hexdata>".format(sys.argv[0]))
        sys.exit(1)

    data = sys.argv[1]
    run(bytes.fromhex(data))


# def test():
#     script_dirname = os.path.dirname(os.path.abspath(__file__))
#     json_file = os.path.join(script_dirname, "..", "evm.json")
#     with open(json_file) as f:
#         data = json.load(f)
#         total = len(data)

#         for i, test in enumerate(data):
#             # Note: as the test cases get more complex, you'll need to modify this
#             # to pass down more arguments to the evm function
#             code = bytes.fromhex(test['code']['bin'])
#             (success, stack) = evm(code)

#             expected_stack = [int(x, 16) for x in test['expect']['stack']]
            
#             if stack != expected_stack or success != test['expect']['success']:
#                 print(f"❌ Test #{i + 1}/{total} {test['name']}")
#                 if stack != expected_stack:
#                     print("Stack doesn't match")
#                     print(" expected:", expected_stack)
#                     print("   actual:", stack)
#                 else:
#                     print("Success doesn't match")
#                     print(" expected:", test['expect']['success'])
#                     print("   actual:", success)
#                 print("")
#                 print("Test code:")
#                 print(test['code']['asm'])
#                 print("")
#                 print("Hint:", test['hint'])
#                 print("")
#                 print(f"Progress: {i}/{len(data)}")
#                 print("")
#                 break
#             else:
#                 print(f"✓  Test #{i + 1}/{total} {test['name']}")


if __name__ == "__main__":
    main()