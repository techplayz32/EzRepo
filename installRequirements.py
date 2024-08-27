# DO NOT TOUCH THIS CODE PLEASE. THIS CODE IS ONLY FOR INSTALL MODULES FOR ANY OF MY SOFTWARE!
# DO NOT TOUCH THIS CODE PLEASE. THIS CODE IS ONLY FOR INSTALL MODULES FOR ANY OF MY SOFTWARE!
# DO NOT TOUCH THIS CODE PLEASE. THIS CODE IS ONLY FOR INSTALL MODULES FOR ANY OF MY SOFTWARE!
# DO NOT TOUCH THIS CODE PLEASE. THIS CODE IS ONLY FOR INSTALL MODULES FOR ANY OF MY SOFTWARE!
# DO NOT TOUCH THIS CODE PLEASE. THIS CODE IS ONLY FOR INSTALL MODULES FOR ANY OF MY SOFTWARE!

import importlib.util
import os
import importlib
import subprocess
import asyncio

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

async def check_requirements(file_name):
    with open(file_name, 'r') as file:
        for line in file:
            module_name = line.strip().split('==')[0]
            if importlib.util.find_spec(module_name) is not None:
                print(f'{GREEN}[V] "{module_name}" is installed.{RESET}')
            else:
                print(f'{RED}[X] "{module_name}" is not installed.{RESET}')
                result = subprocess.run(f"pip install {line}", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f'{GREEN}[V] "{module_name}" installed successfully.{RESET}')
                else:
                    print(f'{RED}[X] Error installing {module_name}:')
                    print(f"{result.stderr}{RESET}")
                    print("Exiting program...")
                    input("Press Enter to continue...")
                    os._exit(0)
                    
            await asyncio.sleep(0.75)
                    
async def main():
    os_name = os.name
    if os_name == 'nt':  # windows
        await check_requirements(os.path.join(os.path.dirname(__file__), 'requirementsWIN.txt'))
    elif os_name == 'posix':  # linux or mac or etc which not windows. 
        await check_requirements(os.path.join(os.path.dirname(__file__), 'requirementsLINUX.txt'))
        
    print(f"{GREEN}[V] Done installing! Please lanuch 'ANY OF MY SOFTWARE.py' now.{RESET}")
    print("Exiting program...")
    input("Press Enter to continue...")
    os._exit(0)
        
if __name__ == '__main__':
    asyncio.run(main())
