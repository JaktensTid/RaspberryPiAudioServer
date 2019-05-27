import socket
import subprocess


class Executor:
    def __init__(self, func, parameter=None):
        self.func = func
        self.parameter = parameter

    def execute(self):
        try:
            self.func(self.parameter)
        except TypeError:
            self.func()


class Command:
    _last_process = None
    SHUTDOWN = 'SD' # shutdown
    CV = 'CV' # change visualization mode
    RV = 'RV' # restart visualization
    CB = 'CB' # change brightness
    CP = 'CP' # change number of pixels
    #_script_dir = './visualization.py'
    _script_dir = '/home/pi/audio-reactive-led-strip/python/visualization.py'

    @staticmethod
    def kill_visualization():
        if Command._last_process:
            subprocess.Popen.terminate(Command._last_process)

    @staticmethod
    def restart_visualization():
        Command.kill_visualization()
        Command._last_process = subprocess.Popen(['python', Command._script_dir])

    @staticmethod
    def shutdown():
        Command.kill_visualization()
        Command._last_process = subprocess.Popen(['shutdown', '-P', 'now'])

    @staticmethod
    def change_visualization(visualization_name):
        Command.kill_visualization()
        Command._last_process = subprocess.Popen(['python', Command._script_dir, '-cv=' + visualization_name])

    @staticmethod
    def change_brightness(brightness):
        Command.kill_visualization()
        Command._last_process = subprocess.Popen(['python', Command._script_dir, '-cb=' + str(brightness)])

    @staticmethod
    def change_number_of_pixels(number_of_pixels):
        Command.kill_visualization()
        Command._last_process = subprocess.Popen(['python', Command._script_dir, '-cp=' + str(number_of_pixels)])


def command_handler(s):
    arguments = s.decode('utf-8')
    if not arguments:
        return
    arguments = arguments.split('-')
    if len(arguments) == 1:
        command = arguments[0]
        parameter = None
    else:
        command, parameter = arguments
    method = None
    if command == Command.SHUTDOWN:
        method = Command.shutdown
    if command == Command.CV:
        method = Command.change_visualization
    if command == Command.RV:
        method = Command.restart_visualization
    if command == Command.CB:
        method = Command.change_brightness
    if command == Command.CP:
        method = Command.change_number_of_pixels
    return Executor(method, parameter)


def start_listening():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET,
                        socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    Command.restart_visualization()

    while True:
        data, _ = sock.recvfrom(16) # buffer size is 16 bytes
        executor = command_handler(data)
        executor.execute()

def main():
    start_listening()


if __name__ == '__main__':
    main()


    
