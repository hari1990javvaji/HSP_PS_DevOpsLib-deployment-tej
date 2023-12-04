"""
Execute commands using subprocess
"""
import subprocess


def execute_command(command,
                    cwd=None):
    """
    Execute command using subprocess and poll process results
    :param command:
    :param cwd:
    :return:
    """

    if cwd is None:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

    else:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd=cwd)
    process_output = process.communicate()[0]
    process_exit_code = process.returncode
    return process_exit_code, process_output


def execute_command_shell(command,
                          cwd=None):
    """
    Execute command using subprocess and poll process results
    :param command:
    :param cwd:
    :return:
    """

    if cwd is None:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   shell=True)
    else:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd=cwd,
                                   shell=True)
    process_output = process.communicate()[0]
    process_exit_code = process.returncode
    return process_exit_code, process_output


def execute_command_non_blocking(command,
                                 command_name,
                                 cwd=None,
                                 ):
    """
    Return subprocess object for a command
    :param command:
    :param command_name:
    :param cwd:
    :return:
    """
    command_log_file_name = command_name + ".txt"

    if cwd is None:
        with open(command_log_file_name, "wb") as _file:
            process = subprocess.Popen(command,
                                       stdout=_file,
                                       stderr=subprocess.STDOUT)
    else:
        with open(command_log_file_name, "wb") as _file:
            process = subprocess.Popen(command,
                                       stdout=_file,
                                       stderr=subprocess.STDOUT,
                                       cwd=cwd)
    return process
