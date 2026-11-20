# Copyright (c) 2026 Steve Jennen
# SPDX-License-Identifier: BSD-2-Clause
"""Run the assembled 68000 launcher with emulated QDOS traps (requires unicorn).

These tests validate instruction encoding, argument/stack layout, and cleanup;
ROM, hardware and real QDOS scheduling remain separate integration checks.
"""
from pathlib import Path
import struct
import unittest
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import *

ROOT = Path(__file__).resolve().parents[1]
D = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3]
A = [UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
     UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7]


class Machine:
    BASE, BASIC, WORK, JOB, STACK, STOP, VECTOR = 0x10000, 0x20000, 0x40000, 0x50000, 0x28000, 0xf000, 0x1200

    def __init__(self, argument=None, string=False, fail=None, relocate=False, count=None, use=False):
        self.cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        self.cpu.mem_map(0, 0x100000)
        self.binary = (ROOT / 'build/dist/vi_rext').read_bytes()
        self.cpu.mem_write(self.BASE, self.binary)
        self.fail, self.relocate = fail, relocate
        self.opened = self.created = self.activated = self.freed = False
        self.command = None
        self.argument = argument
        self.minimum_sp = self.STACK
        self.put(0x110, self.VECTOR, 2)
        self.put(0x116, self.VECTOR + 16, 2)
        self.cpu.reg_write(UC_M68K_REG_SR, 0x2000)
        self.cpu.reg_write(A[7], self.STACK)
        self.put(self.STACK, self.STOP)
        self.cpu.reg_write(A[6], self.BASIC)
        self.cpu.hook_add(UC_HOOK_CODE, self.hook)
        self.cpu.emu_start(self.BASE, self.STOP, count=1000)
        self.entry = self.use_entry if use else self.entry_point
        self.cpu.reg_write(A[7], self.STACK)
        self.put(self.STACK, self.STOP)
        self.cpu.reg_write(A[3], 0x100)
        self.cpu.reg_write(A[5], 0x100 + 8 * (count if count is not None else int(argument is not None)))
        self.put(self.BASIC + 0x20, 0x300)
        self.put(self.BASIC + 0x18, 0x800)
        if argument is not None:
            self.put(self.BASIC + 0x100, (0x0201 if string == 'variable' else 0x0101) if string else 2, 2)
            self.put(self.BASIC + 0x102, -1 if string is True else 37, 2)
            self.put(self.BASIC + 0x104, 0x500)
            self.put(self.BASIC + 0x800 + 37 * 8 + 2, 19, 2)
            self.cpu.mem_write(self.BASIC + 0x300 + 19, bytes([len(argument)]) + argument)
        try:
            self.cpu.emu_start(self.entry, self.STOP, count=30000)
        except Exception:
            pc = self.cpu.reg_read(UC_M68K_REG_PC)
            print('CPU exception at', hex(pc), bytes(self.cpu.mem_read(pc, 8)).hex())
            raise
        assert self.cpu.reg_read(UC_M68K_REG_PC) == self.STOP, 'instruction limit reached'
        self.result = self.cpu.reg_read(D[0])
        if self.result & 0x80000000:
            self.result -= 0x100000000

    def put(self, address, value, size=4):
        self.cpu.mem_write(address, (value & ((1 << (size * 8)) - 1)).to_bytes(size, 'big'))

    def get(self, address, size=4):
        return int.from_bytes(self.cpu.mem_read(address, size), 'big')

    def reg(self, register):
        return self.cpu.reg_read(register)

    def return_from_vector(self):
        sp = self.reg(A[7])
        self.cpu.reg_write(UC_M68K_REG_PC, self.get(sp))
        self.cpu.reg_write(A[7], sp + 4)

    def hook(self, cpu, pc, size, unused):
        self.minimum_sp = min(self.minimum_sp, self.reg(A[7]))
        if pc == self.VECTOR:
            table = self.reg(A[1])
            assert self.get(table, 2) == 2
            assert bytes(cpu.mem_read(table + 4, 3)) == b'\x02VI'
            delta = self.get(table + 2, 2)
            self.entry_point = table + 2 + (delta if delta < 32768 else delta - 65536)
            slot = table + 8
            assert bytes(cpu.mem_read(slot + 2, 7)) == b'\x06VI_USE'
            delta = self.get(slot, 2)
            self.use_entry = slot + (delta if delta < 32768 else delta - 65536)
            self.return_from_vector()
            return
        if pc == self.VECTOR + 16:
            basic = self.reg(A[6])
            if self.relocate:
                cpu.mem_write(basic + 0x10000, bytes(cpu.mem_read(basic, 0x1000)))
                basic += 0x10000
                cpu.reg_write(A[6], basic)
            self.put(basic + 0x500, len(self.argument), 2)
            cpu.mem_write(basic + 0x502, self.argument)
            cpu.reg_write(A[1], 0x500)
            cpu.reg_write(D[0], 0)
            self.return_from_vector()
            return
        opcode = bytes(cpu.mem_read(pc, 2))
        if opcode not in (b'\x4e\x41', b'\x4e\x42', b'\x4e\x43'):
            return
        trap = opcode[1] - 0x40
        key = self.reg(D[0])
        phase = {(1, 0x18): 'allocate', (2, 1): 'open', (3, 0x47): 'header',
                 (1, 1): 'create', (3, 0x48): 'load', (2, 2): 'close',
                 (1, 10): 'activate'}.get((trap, key))
        error = -7 if phase is not None and self.fail == phase else 0
        if not error:
            if (trap, key) == (1, 0x18):
                assert self.reg(D[1]) == 352
                cpu.reg_write(A[0], self.WORK)
            elif (trap, key) == (2, 1):
                ptr = self.reg(A[0])
                assert bytes(cpu.mem_read(ptr + 2, self.get(ptr, 2))) == getattr(self, 'expected_program', b'win1_elvis')
                self.opened = True
                cpu.reg_write(A[0], 0x10001)
            elif (trap, key) == (3, 0x47):
                header = bytearray(64)
                struct.pack_into('>I', header, 0, 100)
                header[5] = 1
                struct.pack_into('>I', header, 6, 4096)
                cpu.mem_write(self.reg(A[1]), bytes(header))
            elif (trap, key) == (1, 1):
                assert self.reg(D[2]) == 100
                assert self.reg(D[3]) == 4096 + 320
                self.created = True
                cpu.reg_write(D[1], 0x20002)
                cpu.reg_write(A[0], self.JOB)
                self.put(self.JOB - 12, 0x80000)
            elif (trap, key) == (3, 0x48):
                assert self.reg(A[1]) == self.JOB
                assert self.reg(D[2]) == 100
            elif (trap, key) == (2, 2):
                self.opened = False
            elif (trap, key) == (1, 10):
                assert self.reg(D[1]) == 0x20002
                assert self.reg(D[2]) == 32
                assert not self.opened
                sp = self.get(self.JOB - 12)
                assert sp % 2 == 0
                assert self.get(sp, 2) == 0
                length = self.get(sp + 2, 2)
                self.command = bytes(cpu.mem_read(sp + 4, length))
                self.activated = True
            elif (trap, key) == (1, 5):
                self.created = False
            elif (trap, key) == (1, 0x19):
                assert self.reg(A[0]) == self.WORK
                self.freed = True
            else:
                raise AssertionError(f'unexpected trap {trap}/{key:x}')
        cpu.reg_write(D[0], error & 0xffffffff)
        cpu.reg_write(UC_M68K_REG_PC, pc + 2)


class LauncherTests(unittest.TestCase):
    def test_launch_arguments(self):
        for argument, string in [(None, False), (b'snl4_error_txt', False),
                                 (b'snl4_name with spaces', True), (b'x' * 255, True),
                                 (b'snl4_elvis2_log', 'variable'), (b'', True)]:
            with self.subTest(argument=argument, string=string):
                machine = Machine(argument, string, relocate=string)
                self.assertEqual(machine.result, 0)
                self.assertTrue(machine.activated)
                self.assertTrue(machine.freed)
                self.assertFalse(machine.opened)
                self.assertEqual(machine.command, b'"' + argument + b'"' if argument else b'')
                self.assertLessEqual(machine.STACK - machine.minimum_sp, 128)

    def test_configured_program(self):
        for program in [b'win1_vi', b'snl1_tools_elvis', b'x' * 255]:
            with self.subTest(program=program):
                machine = Machine(program, string=True, relocate=True, use=True)
                self.assertEqual(machine.result, 0)
                self.assertFalse(machine.activated)
                machine.expected_program = program
                machine.cpu.reg_write(A[7], machine.STACK)
                machine.put(machine.STACK, machine.STOP)
                machine.cpu.reg_write(A[3], 0x100)
                machine.cpu.reg_write(A[5], 0x100)
                machine.cpu.emu_start(machine.entry_point, machine.STOP, count=30000)
                self.assertEqual(machine.reg(D[0]), 0)
                self.assertTrue(machine.activated)

    def test_use_invalid_parameters(self):
        for argument, count in [(None, 0), (b'', 1), (b'a', 2)]:
            machine = Machine(argument, string=True, count=count, use=True)
            self.assertEqual(machine.result, -15)
            self.assertFalse(machine.activated)

    def test_failure_cleanup(self):
        for phase in ['allocate', 'open', 'header', 'create', 'load', 'activate']:
            with self.subTest(phase=phase):
                machine = Machine(b'snl4_error_txt', fail=phase)
                self.assertEqual(machine.result, -7)
                self.assertFalse(machine.activated)
                self.assertFalse(machine.opened)
                self.assertFalse(machine.created)
                self.assertEqual(machine.freed, phase != 'allocate')

    def test_invalid_parameters(self):
        for argument, count in [(b'bad"name', 1), (b'bad\nname', 1), (b'a', 2)]:
            machine = Machine(argument, count=count)
            self.assertEqual(machine.result, -15)
            self.assertFalse(machine.opened)
            self.assertFalse(machine.activated)


if __name__ == '__main__':
    unittest.main()
