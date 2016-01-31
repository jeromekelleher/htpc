#!/usr/bin/env python3
"""
Central script to run the HTPC.
"""

import configparser
import datetime
import io
import json
import os.path
import subprocess
import syslog

import requests


class HtpcManager(object):
    """
    Class used to manage power on and power off times for the HTPC.
    """
    def __init__(self, username, password):
        self._username = username
        self._password = password
        # the number of minutes before the next recording start we should
        # schedule a wakeup for.
        self._wakeup_time_buffer = datetime.timedelta(minutes=10)
        # If there is more than this number of minutes until the next
        # recording we should shutdown.
        self._idle_shutdown_buffer = datetime.timedelta(minutes=5)
        self._set_tvheadend_status()
        self._set_kodi_status()
        self.log("HTPC Manager initialised")

    def _set_kodi_status(self):
        self._kodi_running = False
        try:
            subprocess.check_output(["pidof", "kodi.bin"])
            self._kodi_running = True
        except subprocess.CalledProcessError:
            pass

    def _set_tvheadend_status(self):
        url = "http://localhost:9981/api/dvr/entry/grid_upcoming"
        response = requests.post(url, auth=(self._username, self._password))
        json_doc = json.loads(response.text)
        start_times = []
        for entry in json_doc["entries"]:
            start = datetime.datetime.fromtimestamp(entry["start_real"])
            start_times.append(start)
        self._next_recording_start = min(start_times)

    def shutdown_required(self):
        """
        Returns True if the system should shutdown.
        """
        now = datetime.datetime.now()
        return (
            (not self._kodi_running) and
            self._next_recording_start > now + self._idle_shutdown_buffer)

    def set_wakeup_timer(self):
        """
        Sets the wakeup timer using the RTC wake alarm.
        """
        wakeup_time = self._next_recording_start - self._wakeup_time_buffer
        unix_time = str(int(wakeup_time.timestamp()))
        rtc = "/sys/class/rtc/rtc0/wakealarm"
        # First clear the timer
        with open(rtc, "w") as f:
            f.write("0")
        with open(rtc, "w") as f:
            f.write(unix_time)
        self.log("Set wakeup time to {}".format(wakeup_time))

    def shutdown(self):
        """
        Shuts down the system immediately.
        """
        self.log("Shutting down")
        subprocess.check_call(["/sbin/shutdown", "-h", "now"])

    def log_status(self):
        self.log("kodi running:", self._kodi_running)
        self.log("tvheadend next recording", self._next_recording_start)
        self.log("shutdown required:", self.shutdown_required())

    def log(self, *args):
        buff = io.StringIO()
        print(*args, file=buff, end="")
        syslog.syslog(buff.getvalue())


def read_credentials():
    filename = os.path.expanduser("~/.htpc_manager")
    config = configparser.ConfigParser()
    with open(filename) as config_file:
        config.read_file(config_file)
    section = "CREDENTIALS"
    tvheadend_user = config.get(section, "tvheadend_user")
    tvheadend_password = config.get(section, "tvheadend_password")
    return tvheadend_user, tvheadend_password


def main():
    username, password = read_credentials()
    manager = HtpcManager(username, password)
    manager.log_status()
    if manager.shutdown_required():
        manager.set_wakeup_timer()
        manager.shutdown()


if __name__ == "__main__":
    main()
