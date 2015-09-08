import subprocess


def docker_vm_uid():
    """
    Returns the UID of the default docker user inside the VM

    When a host is using boot2docker or docker-machine to run docker with
    boot2docker.iso (As on Mac OS X), the UID that mounts the shared filesystem
    inside the VirtualBox VM is likely different than the user's UID on the host.
    :return: The numeric UID (as a string) of the docker account inside
    the boot2docker VM
    """
    if boot2docker_running():
        return boot2docker_uid()
    elif docker_machine_running():
        return docker_machine_uid()
    else:
        return None


def check_output_and_strip(cmd):
    """
    Passes a command list to subprocess.check_output, returning None
    if an expected exception is raised
    :param cmd: The command to execute
    :return: Stripped string output of the command, or None if error
    """
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return result.strip()
    except (OSError, subprocess.CalledProcessError, TypeError, AttributeError):
        # OSError is raised if command doesn't exist
        # CalledProcessError is raised if command returns nonzero
        # AttributeError is raised if result cannot be strip()ped
        return None


def docker_machine_name():
    """
    Get the machine name of the active docker-machine machine
    :return: Name of the active machine or None if error
    """
    return check_output_and_strip(['docker-machine', 'active'])


def cmd_output_matches(check_cmd, expected_status):
    """
    Runs a command and compares output to expected
    :param check_cmd: Command list to execute
    :param expected_status: Expected output, e.g. "Running" or "poweroff"
    :return: Boolean value, indicating whether or not command result matched
    """
    if check_output_and_strip(check_cmd) == expected_status:
        return True
    else:
        return False


def boot2docker_running():
    """
    Checks if boot2docker CLI reports that boot2docker vm is running
    :return: True if vm is running, False otherwise
    """
    return cmd_output_matches(['boot2docker', 'status'], 'running')


def docker_machine_running():
    """
    Asks docker-machine for active machine and checks if its VM is running
    :return: True if vm is running, False otherwise
    """
    machine_name = docker_machine_name()
    return cmd_output_matches(['docker-machine', 'status', machine_name], 'Running')


def cmd_output_to_int(cmd):
    """
    Runs the provided command and returns the integer value of the result
    :param cmd: The command to run
    :return: Integer value of result, or None if an error occurred
    """
    result = check_output_and_strip(cmd)  # may return None
    if result is not None:
        try:
            result = int(result)
        except ValueError:
            # ValueError is raised if int conversion fails
            result = None
    return result


def boot2docker_uid():
    """
    Gets the UID of the docker user inside a running boot2docker vm
    :return: the UID, or None if error (e.g. boot2docker not present or stopped)
    """
    return cmd_output_to_int(['boot2docker', 'ssh', 'id', '-u'])


def docker_machine_uid():
    """
    Asks docker-machine for active machine and gets the UID of the docker user
    inside the vm
    :return: the UID, or None if error (e.g. docker-machine not present or stopped)
    """
    machine_name = docker_machine_name()
    return cmd_output_to_int(['docker-machine', 'ssh', machine_name, "id -u"])


if __name__ == '__main__':
    print docker_vm_uid()
