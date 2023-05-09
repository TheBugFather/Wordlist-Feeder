""" Built-in modules """
import argparse
import os
import logging
import sys
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
# Custom modules #
from Modules.utils import error_query, print_err


# Set a time limit per wordlist if desired (None=blocking) #
EXEC_TIMEOUT = None


def system_cmd(conf_obj: object, command: str, exec_time: int):
    """
    Executes passed in system command and returns outs/errs data to write to file.

    :param conf_obj:  The program configuration instance.
    :param command:  The command to be executed.
    :param exec_time:   The execution time of the command (None=blocking).
    :return:  Command data as bytes on success, boolean False on failure.
    """
    try:
        # Set up child process in context manager, piping output & errors to return variable #
        with Popen(command, executable=conf_obj.shell, stdout=PIPE, stderr=STDOUT) as cmd_proc:
            # Execute child process for passed in timeout (None=blocking) #
            out = cmd_proc.communicate(timeout=exec_time)[0]

    # If the process times out #
    except TimeoutExpired:
        out = b'* [TIMEOUT] Command execution timed out *'
        # Print error and log #
        print_err(f'Process for {command} timed out before finishing execution')
        logging.error('Process for %s timed out before finishing execution', command)

    # If the input command has improper data type #
    except TypeError:
        # Print error, log, and return False #
        print_err(f'Input command {command} contains data type other than string')
        logging.error('Input command %s contains data type other than string', command)
        return False

    return out.strip()


def command_parser(arg_cmd: str, cmd_name: str, wordlist_path: str):
    """
    Parses in executable name and wordlist path into command and returns it.

    :param arg_cmd:  The passed in command to have wordlist parsed in it.
    :param cmd_name:  The name of command to be executed parsed from exec_path in config class.
    :param wordlist_path:  The wordlist path to parse in the arg_cmd.
    :return:  The command with the wordlist path parsed in it.
    """
    tmp_parse = arg_cmd.replace('<exec_name>', cmd_name)
    return tmp_parse.replace('<wordlist>', wordlist_path)


def main(conf_obj: object):
    """
    Iterates through wordlists in WordlistDock, parses each wordlist path into command, executes
    the command, and writes returned result to output file.

    :param conf_obj:  The program configuration instance.
    :return:  Nothing
    """
    print(r'''
 __       __)                          ________)                 
(, )  |  /          /) /) ,           (, /              /)       
   | /| /  _____  _(/ //    _  _/_      /___,  _   _  _(/  _  __ 
   |/ |/  (_)/ (_(_(_(/__(_/_)_(__   ) /     _(/__(/_(_(__(/_/ (_
   /  |                             (_/    
    ''')
    # Change directory to the location of executable to prevent dependency issues #
    os.chdir(str(conf_obj.exec_path.parent))

    # Iterate through stored wordlist file paths #
    for file in conf_obj.in_files:
        # Format output file for results #
        out_file = config_obj.output_folder / f'{file.name}_results.txt'

        print(f'[+] Running {conf_obj.exec_path.name} on {file.name}')
        # Replace <exec_name> with executable & <wordlist> with wordlist path #
        cmd = command_parser(conf_obj.cmd_arg, conf_obj.exec_path.name, str(file))
        # Execute system command with parsed wordlist #
        output = system_cmd(conf_obj, cmd, EXEC_TIMEOUT)

        try:
            # Open the output file and write results #
            with out_file.open('wb') as out_file:
                out_file.write(output)

        # If error occurs during file operation #
        except OSError as file_err:
            # Print & log error based on errno descriptor #
            error_query(str(out_file), 'wb', file_err)


class ProgramConfig:
    """
    Program configuration class for storing program components.
    """
    def __init__(self):
        # Program variables #
        self.cwd = Path.cwd()
        self.wordlist_folder = self.cwd / 'WordlistDock'
        self.output_folder = self.cwd / 'Results'
        self.in_files = []
        self.exec_path = None
        self.cmd_arg = None
        self.shell = os.environ.get('SHELL')

    def parse_in_files(self):
        """
        Iterate through contents of WordlistDock and append wordlist paths to input file list.

        :return:  Nothing
        """
        # Iterate through contents of wordlist directory #
        for file in os.scandir(self.wordlist_folder):
            # If the file is not a text wordlist, skip it #
            if not file.name.endswith('.txt'):
                continue

            # Append current iteration file path to input wordlist file list #
            self.in_files.append(self.wordlist_folder / file.name)

    def parse_exec_path(self, parsed_path: str):
        """
        Ensures passed in executable path exists before storing it in program configuration class.

        :param parsed_path:  The executable path parsed from command line args.
        :return:  Nothing
        """
        path_obj = Path(parsed_path)
        # If the parsed executable path does not exist #
        if not path_obj.exists():
            # Print error and exit with error exit code #
            print_err(f'Passed in executable path {parsed_path} does not exist, try again with '
                      'path to existing executable')
            sys.exit(2)

        self.exec_path = path_obj

    def parse_cmd_arg(self, parsed_cmd: str):
        """
        Ensures passed in command arg contains proper <exec_path> and <wordlist> delimiters before
        storing in configuration class.

        :param parsed_cmd:  The arg command to have wordlist parsed in it.
        :return:  Nothing
        """
        # If the wordlist delimiter is not in arg command #
        if '<exec_name>' not in parsed_cmd or '<wordlist>' not in parsed_cmd:
            # Print error and exit with error exit code #
            print_err('Wordlist delimiter missing from passed in command arg, make sure it is in '
                      'the command arg and try again')
            sys.exit(2)

        self.cmd_arg = parsed_cmd


if __name__ == '__main__':
    RET = 0
    # Initial the program configuration instance #
    config_obj = ProgramConfig()
    # Add any wordlist text files into config class list #
    config_obj.parse_in_files()

    # Parse command line arguments #
    arg_parser = argparse.ArgumentParser(description='A tool for automating bruting/fuzzing '
                                                     'wordlists with tools of choice')
    arg_parser.add_argument('exec_path', help='Path to the executable tool performing '
                                              'bruting/fuzzing')
    arg_parser.add_argument('cmd', help='Command to execute with <exec_name> & <wordlist> delimiter'
                                        ' to dynamically parse contents of WordlistDock')
    parsed_args = arg_parser.parse_args()

    # Ensure the executable path arg into config class #
    config_obj.parse_exec_path(parsed_args.exec_path)
    # Validate and store parsed arg into config class #
    config_obj.parse_cmd_arg(parsed_args.cmd)

    # If the WordlistDock directory is missing #
    if not config_obj.wordlist_folder.exists():
        # Create the missing dir #
        config_obj.wordlist_folder.mkdir(parents=True)
        # Print error telling user to put wordlists in the dock #
        print_err('WordlistDock folder missing .. now created so add wordlists in it and try again')
        sys.exit(2)

    # If the Output directory is missing #
    if not config_obj.output_folder.exists():
        # Create the missing dir #
        config_obj.output_folder.mkdir(parents=True)

    # Setup the log file and logging facilities #
    logging.basicConfig(filename='Wordlist-Feeder.log',
                        format='%(asctime)s %(lineno)4d@%(filename)-19s[%(levelname)s]>>  '
                               ' %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        main(config_obj)

    # If unknown exception occurs #
    except Exception as err:
        # Print error, log, and set error exit code #
        print_err(f'Unknown exception occurred: {err}')
        logging.exception('Unknown exception occurred: %s', err)
        RET = 1

    sys.exit(RET)
