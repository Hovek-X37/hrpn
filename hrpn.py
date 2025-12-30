from pathlib import Path
from settings import HRPNS
import argparse
import json
import os
import math
import readline


class HRPNApp():
    stack = []
    regpath = Path('registry.json')

    def __init__(self, args):
        self.settings = {}
        os.system('cls' if os.name == 'nt' else 'clear')
        self.hsg = HRPNS(args)
        self.settings = self.hsg.get_settings()
        self.registry = self.hsg.get_registry()
        self.header = '\033[95m'
        self.okblue = '\033[94m'
        self.okcyan = '\033[96m'
        self.okgreen = '\033[92m'
        self.warnc = '\033[93m'
        self.fail = '\033[91m'
        self.endc = '\033[0m'
        self.bold = '\033[1m'
        self.underline = '\033[4m'

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_length(self, reqlength):
        if len(self.stack) < reqlength:
            return False
        return True

    def error(self, message):
        self.clear_screen()
        print(self.fail + message + self.endc)

    def result(self, message):
        print(self.okgreen + message + self.endc)

    def warn(self, message):
        self.clear_screen()
        print(self.warnc + message + self.endc)

    def change_sign(self):
        self.clear_screen()
        if len(self.stack) < 1:
            self.warn("Not enough items in stack")
            return
        x = self.stack.pop()
        if x < 0:
            self.stack.append(abs(x))
        else:
            self.stack.append(-abs(x))

    def swap_xy(self):
        self.clear_screen()
        if len(self.stack) < 2:
            self.warn("Not enough items in stack")
            return
        x = self.stack.pop()
        y = self.stack.pop()
        self.stack.append(x)
        self.stack.append(y)

    def drop(self):
        self.clear_screen()
        if len(self.stack) == 0:
            self.warn("Not enough items in stack")
            return
        self.stack.pop()

    def clear(self):
        self.clear_screen()
        self.stack.clear()

    def add(self):
        self.clear_screen()
        if len(self.stack) < 2:
            self.warn("Not enough items in stack")
            return
        y = self.stack.pop()
        x = self.stack.pop()
        self.stack.append(x + y)

    def subtract(self):
        self.clear_screen()
        if len(self.stack) < 2:
            self.warn("Not enough items in stack")
            return
        y = self.stack.pop()
        x = self.stack.pop()
        self.stack.append(x - y)

    def multiply(self):
        self.clear_screen()
        if len(self.stack) < 2:
            self.warn("Not enough items in stack")
            return
        y = self.stack.pop()
        x = self.stack.pop()
        try:
            self.stack.append(x * y)
        except OverflowError:
            self.error("Result too large")

    def divide(self):
        self.clear_screen()
        if len(self.stack) < 2:
            self.warn("Not enough items in stack")
            return
        y = self.stack.pop()
        x = self.stack.pop()
        if y == 0:
            self.error("Cannot divide by zero")
            return
        self.stack.append(x / y)

    def push(self, arg):
        self.clear_screen()
        self.arg = arg
        if len(self.stack) == self.settings['stacksize']:
            self.warn("Stack is full")
        else:
            try:
                self.stack.append(float(arg))
            except ValueError:
                self.warn("Invalid input")

    def pi(self):
        self.clear_screen()
        if len(self.stack) == self.settings['stacksize']:
            self.warn("Stack is full")
            return
        self.stack.append(math.pi)

    def store_number(self, key):
        self.clear_screen()
        if len(self.stack) == 0:
            self.warn("Stack is empty")
            return
        self.registry[key] = self.stack[-1]
        if self.hsg.cmd_line() is False and self.hsg.ret_setting('registry') is True:
            self.regpath.write_text(json.dumps(self.registry))
        self.result(f"Number stored to key {key}")

    def changesettings(self):
        self.clear_screen()
        if self.hsg.cmd_line() is True:
            self.warn("Cannot change settings in command line mode")
            return
        self.hsg.change_app_settings()
        self.settings = self.hsg.get_settings()
        return

    def recall_number(self, key):
        self.clear_screen()
        if key not in self.registry:
            self.warn(f"No number stored in key {key}")
            return
        self.stack.append(self.registry[key])
        self.result(f"Number recalled from key {key}")

    def show_stack(self, bypass=False):
        decs = self.hsg.ret_setting('decimalplaces')
        if self.hsg.ret_setting('hidestack') is False or bypass is True:
            if self.hsg.ret_setting('orientation') == "v":
                print("Stack:")
                for i in range(len(self.stack)):
                    if decs == 0:
                        print(self.stack[i])
                    else:
                        print(f'{self.stack[i]:.{decs}f}')
            else:
                print("Stack: [", end=" ")
                if decs == 0:
                    print(', '.join(str(q) for q in self.stack), end=" ")
                else:
                    print(', '.join(f'{q:.{decs}f}' for q in self.stack), end=" ")
                print("]")
        else:
            return

    def last_number(self, digits=8):
        self.clear_screen()
        if len(self.stack) == 0:
            self.warn("Stack is empty")
            return
        if digits == "f":
            lastnum = self.stack[-1]
        else:
            try:
                digits = int(digits)
            except ValueError:
                self.warn("Invalid input")
                return
            digit = int(digits)
            lastnum = round(self.stack[-1], digit)
        self.result(f"Last number: {lastnum}")

    def show_header(self):
        if self.hsg.ret_setting('hideheader') is False:
            print(self.header + self.bold + self.underline + "HRPN Calculator" + self.endc)
            print("Enter a command or number to push to the stack")
            print("Commands: +, -, *, /, c, d, s, x, n, p, q, sto[key], rcl[key], set")
        else:
            return

    def show_help(self):
        self.clear_screen()
        print(self.header + "HRPN Calculator Help" + self.endc)
        print("Commands:")
        print("+: Add the top two numbers on the stack")
        print("-: Subtract the top two numbers on the stack")
        print("*: Multiply the top two numbers on the stack")
        print("/: Divide the top two numbers on the stack")
        print("c: Clear the stack")
        print("d: Drop the top number from the stack")
        print("s: Swap the top two numbers on the stack")
        print("x: Change the sign of the top number on the stack")
        print("n: Show the stack")
        print("p: Push pi to the stack")
        print("sto[key]: Store the top number on the stack to the registry")
        print("rnd[digits]: Show the last number on the stack with the specified number of digits")
        print("rcl[key]: Recall a number from the registry")
        print("set: Change the settings")
        print("q: Quit the calculator")

    def show_about(self):
        self.clear_screen()
        print(self.header + "HRPN Calculator" + self.endc)
        print("Version 0.1")
        print("Written by: Hovek")
        print("Type help for a list of commands")

    def run(self):
        while True:
            self.show_header()
            self.show_stack()
            command = input(self.settings['prompt'])
            if command == "+":
                self.add()
            elif command == "-":
                self.subtract()
            elif command == "*":
                self.multiply()
            elif command == "/":
                self.divide()
                command = command[1:9]
            elif command == "c":
                self.clear()
            elif command == "d":
                self.drop()
            elif command == "s":
                self.swap_xy()
            elif command == "p":
                self.pi()
            elif command == "x":
                self.change_sign()
            elif command == "n":
                self.show_stack(True)
            elif command == "q":
                break
            elif command.startswith('sto'):
                self.store_number(command[3:4])
            elif command.startswith('rnd'):
                self.last_number(command[3:6])
            elif command.startswith('rcl'):
                self.recall_number(command[3:4])
            elif command == "set":
                self.changesettings()
            elif command == "help":
                self.show_help()
            elif command == "about":
                self.show_about()
            else:
                self.push(command)


parser = argparse.ArgumentParser(description="HRPN Calculator")
parser.add_argument("-p", "--prompt", type=str, help="Set the prompt")
parser.add_argument("-s", "--stacksize", type=int, help="Set the stack size")
parser.add_argument("-d", "--decimalplaces", type=int, help="Set the number of decimal places")
parser.add_argument("-hh", "--hideheader", action="store_true", help="Hide the header")
parser.add_argument("-sh", "--hidestack", action="store_true", help="Hide the stack")
parser.add_argument("-o", "--orientation", type=str, help="Set the stack orientation", choices=["v", "h"])
parser.add_argument("-c", "--commandline", action="store_true", help="use command line arguments instead of settings file", default=False)
parser.add_argument("-f", "--file", type=str, help="Settings file", default="settings.json")
parser.add_argument("-nr", "--noregistry", action="store_true", help="Don't use Registry file", default=False)
args = parser.parse_args()
HRPN = HRPNApp(args)
HRPN.run()
