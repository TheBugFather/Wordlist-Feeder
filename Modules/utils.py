""" Built-in modules """
import errno
import logging
import sys


def error_query(err_path: str, err_mode: str, err_obj):
    """
    Looks up the errno message to get description.

    :param err_path:  The path to the file where the error occurred.
    :param err_mode:  The file mode used during the error.
    :param err_obj:  The error message instance.
    :return:  Nothing
    """
    # If file does not exist #
    if err_obj.errno == errno.ENOENT:
        print_err(f'{err_path} does not exist')
        logging.error('%s does not exist', err_path)

    # If the file does not have read/write access #
    elif err_obj.errno == errno.EPERM:
        print_err(f'{err_path} does not have permissions for {err_mode}'
                  ' file mode, if file exists confirm it is closed')
        logging.error('%s does not have permissions for %s file mode, if file '
                      'exists confirm it is closed', err_path, err_mode)

    # File IO error occurred #
    elif err_obj.errno == errno.EIO:
        print_err(f'IO error occurred during {err_mode} mode on {err_path}')
        logging.error('IO error occurred during %s mode on %s', err_mode, err_path)

    # If other unexpected file operation error occurs #
    else:
        print_err(f'Unexpected file operation error occurred accessing {err_path}: {err_obj.errno}')
        logging.error('Unexpected file operation error occurred accessing %s: %s',
                      err_path, err_obj.errno)


def print_err(msg: str):
    """
    Prints error message through standard error.

    :param msg:  The error message to be displayed.
    :return:  Nothing
    """
    #  Print error via standard error #
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)
