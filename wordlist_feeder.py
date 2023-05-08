""" Built-in modules """
import argparse
import os
import logging
import sys
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
# Custom modules #
from Modules.utils import error_query, print_err


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


def command_parser(arg_cmd: str, wordlist_path: str):
    """
    Parses in wordlist path into command and returns it.

    :param arg_cmd:  The passed in command to have wordlist parsed in it.
    :param wordlist_path:  The wordlist path to parse in the arg_cmd.
    :return:  The command with the wordlist path parsed in it.
    """
    return arg_cmd.replace('<wordlist>', wordlist_path)


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

    def parse_cmd_arg(self, parsed_arg: str):
        """
        Make sure wordlist delimiter is passed in arg command for wordlists to be dynamically
        parsed in.

        :param parsed_arg:  The arg command to have wordlist parsed in it.
        :return:  Nothing
        """
        # If the wordlist delimiter is not in arg command #
        if '<wordlist>' not in parsed_arg:
            # Print error and exit with error exit code #
            print_err('Wordlist delimiter missing from arg command, make sure it is in arg '
                      'command and try again')
            sys.exit(2)

        self.cmd_arg = parsed_arg


def main(conf_obj: object):
    """
    Iterates through wordlists in WordlistDock, parses each wordlist path into command, executes
    the command, and writes returned result to output file.

    :param conf_obj:  The program configuration instance.
    :return:  Nothing
    """
    # Iterate through stored wordlist file paths #
    for file in conf_obj.in_files:
        # Format output file for results #
        out_file = conf_obj.cwd / config_obj.output_folder / f'{file.name}_results.txt'

        # Replace <wordlist> delimiter with wordlist path #
        cmd = command_parser(conf_obj.cmd_arg, str(file))
        # Execute system command with parsed wordlist #
        output = system_cmd(conf_obj, cmd, None)

        try:
            # Open the output file and write results #
            with out_file.open('ab') as out_file:
                out_file.write(output)

        # If error occurs during file operation #
        except OSError as file_err:
            error_query(str(out_file), 'ab', file_err)


if __name__ == '__main__':
    RET = 0
    # Initial the program configuration instance #
    config_obj = ProgramConfig()
    # Add any wordlist text files into config class list #
    config_obj.parse_in_files()

    # Parse command line arguments #
    arg_parser = argparse.ArgumentParser(description='A tool for automating bruting/fuzzing '
                                                     'wordlists with tools of choice')
    arg_parser.add_argument('command', help='Command to execute with <wordlist> delimiter to '
                                            'dynamically parse contents of WordlistDock')
    parsed_args = arg_parser.parse_args()

    # Validate and store parsed arg in to config class #
    config_obj.parse_cmd_arg(parsed_args.command)

    # If the WordlistDock directory is missing #
    if not config_obj.wordlist_folder.exists():
        # Create the missing dir #
        config_obj.wordlist_folder.mkdir(parents=True)
        # Print error and tell user to put wordlists in the dock #
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
