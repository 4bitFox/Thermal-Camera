# ***************************************************************************
 # *  Copyright(C) 2020 Michal Charvát
 # *
 # *  This program is free software: you can redistribute it and/or modify
 # *  it under the terms of the GNU General Public License as published by
 # *  the Free Software Foundation, either version 3 of the License, or
 # *  (at your option) any later version.
 # *
 # *  This program is distributed in the hope that it will be useful,
 # *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 # *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # *  GNU General Public License for more details.
 # *
 # *  You should have received a copy of the GNU General Public License
 # *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 # *  ***************************************************************************

from time import sleep
from enum import IntEnum, Enum
from smbus2 import SMBus, i2c_msg
from typing import List, Dict, Union, Tuple


class Lepton3Command(object):
    SUPPORTED_METHODS = set()

    class Module(IntEnum):
        AGC = 0x01
        SYS = 0x02
        VID = 0x03
        OEM = 0x48
        RAD = 0x4E

    class Method(IntEnum):
        GET = 0x00
        SET = 0x01
        RUN = 0x02

    def __init__(self, command_module: Union[int, Enum], command_id: int):
        assert type(command_id) == int and 0 <= command_id < 256, 'The command ID must fit into 8 bits: {}'.format(command_id)
        assert command_module in set(module.value for module in self.Module), 'Module must be set to one of: {}'.format(list(self.Module))
        self.command_module = self.Module(command_module)
        self.command_id = command_id
        self.parameters = dict()
        self.command_length = 0


class Lepton3GetCommand(Lepton3Command):
    SUPPORTED_METHODS = {Lepton3Command.Method.GET}

    def __init__(self, command_module: Union[int, Enum], command_id: int, parameters: Union[int, Dict[str, List[int]]] = None):
        super(Lepton3GetCommand, self).__init__(command_module, command_id)
        assert (type(parameters) == dict and len(parameters) > 0) or type(parameters) == int, 'Command parameters must be a nonempty dict or a command length in bytes.'

        if type(parameters) == dict:
            assert all(type(command_name) == str for command_name in parameters.keys()), 'Command parameter dict\'s keys must be string.'
            assert all(type(command_byte_list) == list
                       and len(command_byte_list) % 2 == 0
                       and len(command_byte_list) > 0
                       and all(type(value) == int and 0 <= value <= 255 for value in command_byte_list)
                       for command_byte_list in parameters.values()), 'All command paramter dict\'s values must be lists/tuples with even and positive number of 8bit integers'

            command_parameter_lengths = set(len(command_byte_list) for command_byte_list in parameters.values())
            assert len(command_parameter_lengths) == 1, 'Command parameter dict\'s values must have the same length'
            self.command_length = next(iter(command_parameter_lengths))
            self.parameters = parameters

        else:
            self.command_length = parameters

        assert type(
            self.command_length) == int and self.command_length > 0 and self.command_length % 2 == 0, 'Command length in bytes must be a positive even integer, got: {}'.format(
            self.command_length)


class Lepton3GetSetCommand(Lepton3GetCommand):
    SUPPORTED_METHODS = {Lepton3Command.Method.GET, Lepton3Command.Method.SET}

    def __init__(self, command_module: Union[int, Enum], command_id: int, parameters: Dict[str, List[int]]):
        assert type(parameters) == dict and len(parameters) > 0, 'Command parameters must be a nonempty dict.'
        super(Lepton3GetSetCommand, self).__init__(command_module, command_id, parameters)


class Lepton3RunCommand(Lepton3Command):
    SUPPORTED_METHODS = {Lepton3Command.Method.RUN}


class Lepton3EnableDisableCommand(Lepton3GetSetCommand):
    def __init__(self, command_module: Union[int, Enum], command_id: int):
        super(Lepton3EnableDisableCommand, self).__init__(command_module, command_id, {'on': [0x00, 0x01], 'off': [0x00, 0x00]})


class Lepton3Control(object):
    _ADDRESS = 0x2A
    _BUSY_WAIT_S = 0.1  # seconds

    class Register(IntEnum):
        POWER = 0x0000
        STATUS = 0x0002
        COMMAND_ID = 0x0004
        DATA_LENGTH = 0x0006
        DATA_0 = 0x0008

    @staticmethod
    def _16bit_to_bytes(number: int) -> List[int]:
        return [((number >> 8) & 0xFF), (number & 0xFF)]

    COMMANDS: Dict[str, Lepton3Command] = {
        'agc_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.AGC, 0x00),
        'agc_policy': Lepton3GetSetCommand(Lepton3Command.Module.AGC, 0x04, {'linear': [0x00, 0x00], 'heq': [0x00, 0x01]}),
        'agc_calc_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.AGC, 0x00),

        'sys_ping': Lepton3RunCommand(Lepton3Command.Module.SYS, 0x00),
        'sys_flir_serial_number': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x08, 8),
        'sys_camera_up_time': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x0C, 4),
        'sys_aux_temp_k': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x10, 2),
        'sys_fpa_temp_k': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x14, 2),
        'sys_telemetry_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.SYS, 0x18),
        'sys_telemetry_location': Lepton3GetSetCommand(Lepton3Command.Module.SYS, 0x1C, {'header': [0x00, 0x00], 'footer': [0x00, 0x01]}),
        'sys_frames_to_average_run': Lepton3RunCommand(Lepton3Command.Module.SYS, 0x20),
        'sys_frames_to_average': Lepton3GetSetCommand(Lepton3Command.Module.SYS, 0x24, {'div1': [0x00, 0x00], 'div2': [0x00, 0x01], 'div4': [0x00, 0x02], 'div8': [0x00, 0x03],
                                                                                        'div16': [0x00, 0x04], 'div32': [0x00, 0x05], 'div64': [0x00, 0x06],
                                                                                        'div128': [0x00, 0x07]}),
        'sys_customer_serial_number': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x28, 32),
        'sys_scene_statistics': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x2C, 8),
        'sys_shutter_position': Lepton3GetSetCommand(Lepton3Command.Module.SYS, 0x38, {'unknown': [0xFF, 0xFF], 'idle': [0x00, 0x00], 'open': [0x00, 0x01], 'closed': [0x00, 0x02],
                                                                                       'breakon': [0x00, 0x03]}),
        'sys_ffc_run': Lepton3RunCommand(Lepton3Command.Module.SYS, 0x40),
        'sys_ffc_status': Lepton3GetCommand(Lepton3Command.Module.SYS, 0x44, 2),
        'sys_gain_mode': Lepton3GetSetCommand(Lepton3Command.Module.SYS, 0x48, {'high': [0x00, 0x00], 'low': [0x00, 0x01], 'auto': [0x00, 0x02]}),
        #'sys_gain_mode': Lepton3GetSetCommand(Lepton3Command.Module.SYS, 0x1C, {'high': [0x00, 0x00], 'low': [0x00, 0x01], 'auto': [0x00, 0x02]}),

        'vid_pcolor_lut': Lepton3GetSetCommand(Lepton3Command.Module.VID, 0x04, {'wheel6': [0x00, 0x00], 'fusion': [0x00, 0x01], 'rainbow': [0x00, 0x02], 'glowbow': [0x00, 0x03],
                                                                                 'sepia': [0x00, 0x04], 'color': [0x00, 0x05], 'icefire': [0x00, 0x06], 'rain': [0x00, 0x07],
                                                                                 'user': [0x00, 0x08]}),
        'vid_focus_calc_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.VID, 0x0C),
        'vid_freeze_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.VID, 0x24),
        'vid_output_format': Lepton3GetSetCommand(Lepton3Command.Module.VID, 0x30, {'raw14': [0x00, 0x07]}),
        'vid_low_gain_pcolor_lut': Lepton3GetSetCommand(Lepton3Command.Module.VID, 0x34,
                                                        {'wheel6': [0x00, 0x00], 'fusion': [0x00, 0x01], 'rainbow': [0x00, 0x02], 'glowbow': [0x00, 0x03],
                                                         'sepia': [0x00, 0x04], 'color': [0x00, 0x05], 'icefire': [0x00, 0x06], 'rain': [0x00, 0x07],
                                                         'user': [0x00, 0x08]}),

        'oem_flir_part_number': Lepton3GetCommand(Lepton3Command.Module.OEM, 0x1C, 32),
        'oem_sw_revision': Lepton3GetCommand(Lepton3Command.Module.OEM, 0x20, 8),
        'oem_video_out_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.OEM, 0x24),
        'oem_output_format': Lepton3GetSetCommand(Lepton3Command.Module.OEM, 0x28, {'rgb888': [0x00, 0x03], 'raw14': [0x00, 0x07]}),
        'oem_customer_part_number': Lepton3GetCommand(Lepton3Command.Module.OEM, 0x38, 32),
        'oem_reboot': Lepton3RunCommand(Lepton3Command.Module.OEM, 0x40),
        'oem_calc_status': Lepton3GetCommand(Lepton3Command.Module.OEM, 0x48, 2),
        'oem_thermal_shutdown_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.OEM, 0x68),
        'oem_bad_pixel_replacement_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.OEM, 0x6C),
        'oem_temporal_filter_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.OEM, 0x70),

        'rad_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.RAD, 0x10),
        'rad_tshutter_mode': Lepton3GetSetCommand(Lepton3Command.Module.RAD, 0x24, {'user': [0x00, 0x00], 'calculated': [0x00, 0x01], 'fixed': [0x00, 0x02]}),
        'rad_ffc_run': Lepton3RunCommand(Lepton3Command.Module.SYS, 0x2C),
        'rad_tlinear_enable': Lepton3EnableDisableCommand(Lepton3Command.Module.RAD, 0xC0),
        'rad_tlinear_scale': Lepton3GetSetCommand(Lepton3Command.Module.RAD, 0xC4, {'10': [0x00, 0x00], '100': [0x00, 0x01]}),
        'rad_tlinear_auto_scale': Lepton3EnableDisableCommand(Lepton3Command.Module.RAD, 0xC8),
    }

    def __init__(self, i2c_number: int):
        self._i2c = SMBus(i2c_number)

    def __del__(self):
        self._i2c.close()
        self._i2c = None

    def read_register(self, register: int, number_of_bytes: int = 2) -> List[int]:
        assert 0 <= register <= 65535 and register in set(reg.value for reg in self.Register), 'Register must fit into 16 bits and be one of: {}'.format(list(self.Register))
        assert (number_of_bytes >= 2 and number_of_bytes % 2 == 0)

        # write operation from where we want to read
        write_register_operation = i2c_msg.write(Lepton3Control._ADDRESS, self._16bit_to_bytes(register))

        # read operation - number of bytes to read
        read_operation = i2c_msg.read(Lepton3Control._ADDRESS, number_of_bytes)

        # transceive at once
        self._i2c.i2c_rdwr(write_register_operation, read_operation)
        return list(read_operation)

    def write_register(self, register: int, data: Union[int, List[int]]) -> None:
        assert 0 <= register <= 65535 and register in set(reg.value for reg in self.Register), 'Register must fit into 16 bits and be one of: {}'.format(list(self.Register))

        # form list of bytes
        if type(data) == int:
            # 16bit - split to two bytes
            data = self._16bit_to_bytes(data)

        assert (type(data) == list and len(data) >= 2 and len(data) % 2 == 0 and all(type(value) == int and 0 <= value <= 255 for value in data)), \
            'Data must form list of even bytes, got: {}'.format(data)

        # merge into a single message
        message = self._16bit_to_bytes(register) + data

        # transceive at once
        write_register_data_operation = i2c_msg.write(Lepton3Control._ADDRESS, message)
        self._i2c.i2c_rdwr(write_register_data_operation)

    def execute_command(self, command_name: str, method_name: str, parameter_name: Union[str, None] = None) -> Tuple[Union[None, List[int], str], int]:
        assert command_name in self.COMMANDS, 'Command not found: {}'.format(command_name)
        command = self.COMMANDS[command_name]

        try:
            method = Lepton3Command.Method[method_name.upper()]
            assert method in command.SUPPORTED_METHODS, 'Command `{}` doesnt support method `{}`. Use one of: {}'.format(command_name, method_name,
                                                                                                                         [m.name for m in command.SUPPORTED_METHODS])
        except KeyError:
            raise ValueError('Unknown method: {}. Use one of: {}'.format(method_name, [m.name for m in Lepton3Command.Method])) from None

        # wait till the camera is ready
        booted, ready, error_code = self.get_status()
        if not booted and command_name != 'oem_reboot':
            print('Camera is not booted and cannot accept commands.')
            return None, error_code

        while not ready and booted:
            sleep(Lepton3Control._BUSY_WAIT_S)
            booted, ready, error_code = self.get_status()

        words_written = 0  # default

        if method == Lepton3Command.Method.SET:
            assert (parameter_name in command.parameters), \
                'For SET method for command: {} you must specify one of this parameters: {}'.format(command_name, command.parameters)

            parameter = command.parameters[parameter_name]
            words_written = len(parameter) // 2  # number of 16bit words

            #  write data
            self.write_register(Lepton3Control.Register.DATA_0, parameter)

        elif method == Lepton3Command.Method.GET:
            words_written = command.command_length // 2

        # write data_length
        self.write_register(Lepton3Control.Register.DATA_LENGTH, words_written)

        # run command
        self.write_register(Lepton3Control.Register.COMMAND_ID, [command.command_module.value, (command.command_id & 0b11111100) | (method & 0b11)])

        # wait for completed
        booted, ready, error_code = self.get_status()
        while not ready:
            sleep(Lepton3Control._BUSY_WAIT_S)
            booted, ready, error_code = self.get_status()

        # GET: read data from DATA_N registers
        output = None
        if method == Lepton3Command.Method.GET:
            output = self.read_register(Lepton3Control.Register.DATA_0, command.command_length)
            for name, value in command.parameters.items():
                if value == output:
                    output = name
                    break

        return output, error_code

    def get_status(self) -> Tuple[bool, bool, int]:
        status = self.read_register(Lepton3Control.Register.STATUS)
        booted, ready, error = bool(status[1] & 0b100), not bool(status[1] & 0b1), status[0]
        return booted, ready, error

    @classmethod
    def get_commands(cls):
        return '\n'.join(sorted(['\t{} -- {}'.format(command_name, [m.name for m in command.SUPPORTED_METHODS])
                                 for command_name, command in Lepton3Control.COMMANDS.items()]))


