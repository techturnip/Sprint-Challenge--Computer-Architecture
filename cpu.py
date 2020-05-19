"""CPU functionality."""

import sys

# OP CODES
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111  # compare
JEQ = 0b01010101  # jump if true
JNE = 0b01010110  # jump if false
JMP = 0b01010100  # jump to address


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.SP = 7
        self.equal = None
        self.reg[self.SP] = len(self.ram) - 1
        self.running = False
        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push_to_stack
        self.branchtable[POP] = self.pop_from_stack
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        self.branchtable[CMP] = self.cmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne
        self.branchtable[JMP] = self.jmp

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("Need proper file name passed")
            sys.exit(1)

        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                if line == '':
                    continue
                comment_split = line.split('#')

                if comment_split[0] == '' or comment_split[0] == '\n':
                    continue
                else:
                    num = comment_split[0].strip()

                    self.ram[address] = int(num, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            print(f'\nADD: {self.reg[reg_a]} + {self.reg[reg_a]}')

            self.reg[reg_a] += self.reg[reg_b]

            print(f'= {self.reg[reg_a]}')

        elif op == 'MUL':
            print(f'\nMUL: {self.reg[reg_a]} * {self.reg[reg_b]}')

            self.reg[reg_a] *= self.reg[reg_b]

            print(f'= {self.reg[reg_a]}')

        elif op == 'CMP':
            print(f'\nCMP: {self.reg[reg_a]} == {self.reg[reg_b]}')
            # compare values store True or False in self.equal
            self.equal = (self.reg[reg_a] == self.reg[reg_b])
            print(self.equal)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return(self.ram[MAR])

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    # OP CODE DEFINITIONS
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # define methods for the opcodes to clean
    # up the run fn and utilize ram methods
    # ____________________________

    # LDI - Load Immediate
    def ldi(self):
        print("\nLDI:")
        reg = self.ram[self.pc + 1]
        val = self.ram[self.pc + 2]
        print(f'Reg: {reg}')
        print(f'Val: {val}')

        self.reg[reg] = val
        self.pc += 3

        print(self.reg)

    # PRN - Print Value
    def prn(self):
        print("\nPRN:")
        reg = self.ram_read(self.pc + 1)

        print(self.reg[reg])

        self.pc += 2

    def mul(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)

        self.alu('MUL', op_a, op_b)
        self.pc += 3

    def add(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)

        self.alu('ADD', op_a, op_b)
        self.pc += 3

    def push_to_stack(self):
        # push to stack
        reg = self.ram_read(self.pc + 1)
        self.reg[self.SP] -= 1
        val = self.reg[reg]
        self.ram_write(val, self.reg[self.SP])
        self.pc += 2

    def pop_from_stack(self):
        # pop from stack
        val = self.ram_read(self.reg[self.SP])
        reg = self.ram_read(self.pc + 1)
        self.reg[reg] = val
        self.reg[self.SP] += 1
        self.pc += 2

    def call(self):
        # call a fn

        # decrement sp
        self.reg[self.SP] -= 1
        # write to loc in ram
        self.ram_write((self.pc + 2), self.reg[self.SP])
        # read from loc in ram
        reg = self.ram_read(self.pc + 1)
        # grab reg value
        reg_value = self.reg[reg]
        # set the addr
        self.pc = reg_value

    def ret(self):
        # get return value
        return_value = self.ram_read(self.reg[self.SP])
        # increment stack pointer
        self.reg[self.SP] += 1
        # set the return address
        self.pc = return_value

    def hlt(self):
        self.running = False
        self.pc += 1

    def cmp(self):
        """Compares values in given registers"""

        # locations
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)

        self.alu('CMP', op_a, op_b)
        self.pc += 3

    def jeq(self):
        print("\nJEQ:")
        # check if cmp equal is true
        if self.equal == True:
            # jump
            self.jmp()
        else:
            print("No jump, equal is False")
            self.pc += 2

    def jne(self):
        print("\nJNE:")
        # check if cmp equal is false
        if self.equal == False:
            # jump
            self.jmp()
        else:
            print("No jump, equal is True")
            self.pc += 2

    def jmp(self):
        print('JMP')
        reg = self.ram_read(self.pc + 1)
        jump = self.reg[reg]
        self.pc = jump  # set jump addr
        print(f'Jump: {jump}')

    def run(self):
        """Run the CPU."""
        IR = None
        self.running = True

        while self.running:
            IR = self.ram[self.pc]
            COMMAND = IR

            if COMMAND in self.branchtable:
                self.branchtable[COMMAND]()
            else:
                # Error
                print(f'Unknown instruction, {COMMAND}')
                sys.exit(1)
