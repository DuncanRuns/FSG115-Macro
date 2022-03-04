import os

VERSION = "1.0.2"
print("FSG115Macro v"+VERSION+" by DuncanRuns")


def installDependencies():
    modules = [
        "keyboard",
        "global-hotkeys",
        "pypiwin32",
        "pyttsx3"
    ]
    for module in modules:
        os.system("python -m pip install "+module)


try:
    import win32.win32gui
    import win32com.client
    import keyboard
    import global_hotkeys
    import pyttsx3
    import time
    import json
    import re
    import typing
    import threading
except:
    installDependencies()
    import time
    import keyboard
    import global_hotkeys
    import json
    import win32.win32gui
    import re
    import typing
    import threading
    import win32com.client
    import pyttsx3


SHELL = win32com.client.Dispatch("WScript.Shell")

DEFAULT_SETTINGS = {
    "threads": 4,
    "java": "java",
    "hotkey": "u",
    "filterWhilePlaying": False,
    "useAtum": False,
    "waitTime": 0.1,
    "stopResetsLocation": 13,
    "minecraftDir": os.path.expanduser("~/AppData/Roaming/.minecraft")
}
SETTINGS_LOCATION = "FSG115Macro.json"


class TTS:
    ENGINE = pyttsx3.init()

    @staticmethod
    def say(message: str):
        threading.Thread(target=TTS._say_activity, args=(message,)).start()

    @staticmethod
    def _say_activity(message: str):
        print("[TTS] "+message)
        if TTS.ENGINE._inLoop:
            TTS.ENGINE.endLoop()
        TTS.ENGINE.say(message)
        TTS.ENGINE.runAndWait()


class FSGRunner:
    JAR_MATCH_FUNC = re.compile('FSG115-.*\\..*\\..*\\.jar').match

    def __init__(self, threads: int, java: str):
        self.threads = threads
        self.java = java

    @staticmethod
    def _is_fsg_jar(name: str):
        return FSGRunner.JAR_MATCH_FUNC(name) and name.endswith(".jar")

    @staticmethod
    def _get_fsg_jar_version(name: str) -> typing.Union[int, None]:
        try:
            vStr = name[7:name.index(".jar")]
            args = vStr.split(".")
            return int(args[0]) * 1000000 + int(args[1]) * 1000 + int(args[2])
        except:
            return None

    @staticmethod
    def _get_jar() -> typing.Union[str, None]:
        max_version = 0
        found = None
        for name in os.listdir():
            if FSGRunner.JAR_MATCH_FUNC(name):
                version = FSGRunner._get_fsg_jar_version(name)
                if version is not None and version > max_version:
                    found = name
                    max_version = version
        return found

    def _get_command(self) -> typing.Union[str, None]:
        jar = FSGRunner._get_jar()
        if jar is None:
            return None
        return f"{self.java} -jar {jar} {self.threads} write"

    def run_filter(self) -> bool:
        command = self._get_command()
        if command is None:
            return False
        os.system(self._get_command())
        return True

    @staticmethod
    def read_file():
        out_text: str
        with open("out.txt", "r") as out_file:
            out_text = out_file.read()
            out_file.close()

        out_lines = out_text.split("\n")
        seed = out_lines[0]
        token = out_lines[1]
        return (seed, token)


class TokenLogger:
    FILE_LOCATION = "tokens.txt"

    @staticmethod
    def log(seed: str, token: str):
        new_log_text: str
        if os.path.isfile(TokenLogger.FILE_LOCATION):
            with open(TokenLogger.FILE_LOCATION, "r") as log_file:
                log_text = log_file.read()
                log_file.close()
            new_log_text = f"{log_text}\n{seed} - {token}"
        else:
            new_log_text = f"{seed} - {token}"
        with open(TokenLogger.FILE_LOCATION, "w+") as log_file:
            log_file.write(new_log_text)
            log_file.close()


class FSG115Macro:

    SAVE_MATCH_FUNC = re.compile(
        '\\[..:..:..\\] \\[.*\\]: Stopping worker threads').match

    def __init__(self, threads: int, java: str, filter_while_playing: bool, use_atum: bool, wait_time: float, stop_resets_location: int, minecraft_directory: str):
        self._total_threads = threads
        self._fsg_runner = FSGRunner(threads, java)

        self._seed_lock = threading.Lock()
        self._seed = None

        self._running_finder_lock = threading.Lock()
        self._running_finder = False
        self._filter_thread: threading.Thread = None

        self._running_macro_lock = threading.Lock()
        self._running_macro = False
        self._filter_while_playing = filter_while_playing
        self._use_atum = use_atum
        self._wait_time = wait_time
        self._current_window = None
        self._stop_resets_location = stop_resets_location
        self._minecraft_directory = minecraft_directory

    def run_macro(self):
        threading.Thread(target=self._macro_activity).start()

    def _macro_activity(self):
        if self._is_in_minecraft() and (not self._get_running_macro()):
            self._set_running_macro(True)

            self._current_window = self._get_window()

            self._ensure_main_menu()
            self._ensure_seed()

            if self._get_seed() is None:
                TTS.say("Error")
                print("!!! No seed available, probably missing jar file !!!")
            else:

                TTS.say("Seed Found")
                time.sleep(1)

                self._activate_window(self._current_window)
                time.sleep(0.5)
                self._create_fsg_world()

            self._set_running_macro(False)

            if self._filter_while_playing:
                self._run_filter_thread()

    def _create_fsg_world(self):
        keys: str
        if self._use_atum:
            keys = "eeeTStapttsTs"
        else:
            keys = "eeetsttttwstapttwstttpTTws"
        self._run_keys(keys)
        self._set_seed(None)

    def _run_keys(self, keys: str):
        for key in keys:
            if key == "t":
                keyboard.press_and_release("tab")
            elif key == "T":
                keyboard.press_and_release("shift+tab")
            elif key == "s":
                keyboard.press_and_release("space")
            elif key == "S":
                keyboard.press_and_release("shift+space")
            elif key.lower() == "a":
                keyboard.press_and_release("ctrl+a")
            elif key.lower() == "e":
                keyboard.press_and_release("esc")
            elif key.lower() == "p":
                keyboard.write(self._get_seed())
            elif key == "w":
                time.sleep(self._wait_time)

    def _ensure_main_menu(self):
        latest_log_location = os.path.join(
            self._minecraft_directory, "logs", "latest.log")
        if FSG115Macro._is_in_minecraft_world():
            has_log_file = os.path.isfile(latest_log_location)
            start_line: str
            if not has_log_file:
                print("!!! No latest.log found. minecraftDir might be incorrect !!!")
            else:
                with open(latest_log_location, "r") as log_file:
                    log_text = log_file.read()
                    log_file.close()
                start_line = log_text.split("\n")[-2]
            if self._use_atum:
                self._run_keys("etttttts")
                for i in range(self._stop_resets_location):
                    self._run_keys("t")
                self._run_keys("s")
            else:
                self._run_keys("eTseee")
            if has_log_file:
                saved_world = False
                while not saved_world:
                    time.sleep(0.1)
                    with open(os.path.join(self._minecraft_directory, "logs", "latest.log"), "r") as log_file:
                        log_text = log_file.read()
                        log_file.close()
                    log_lines = log_text.split("\n")
                    for line in log_lines[-8:]:
                        if FSG115Macro.SAVE_MATCH_FUNC(line) and line.endswith("worker threads"):
                            saved_world = True
                        elif line == start_line:
                            saved_world = False
            else:
                print(
                    "Waiting 5 seconds instead of ensuring main menu due to not finding latest.log")
                time.sleep(5)

    def _ensure_seed(self):
        # Wait for finder thread to finish (this should run if filter_while_playing is true)
        if self._get_running_finder():
            TTS.say("Searching")
            self._filter_thread.join()

        # Check if seed exists, if not, run the filter thread
        if self._get_seed() is None:
            TTS.say("Searching")
            self._run_filter_thread()

        # Wait for finder thread to finish (this should run if filter_while_playing is false)
        if self._get_running_finder():
            self._filter_thread.join()

    @staticmethod
    def _get_window() -> int:
        return win32.win32gui.GetForegroundWindow()

    @staticmethod
    def _activate_window(window: int):
        global SHELL
        SHELL.SendKeys('%')
        win32.win32gui.ShowWindow(window, 5)
        win32.win32gui.SetForegroundWindow(window)
        pass

    @staticmethod
    def _is_in_minecraft() -> bool:
        title: str = win32.win32gui.GetWindowText(
            win32.win32gui.GetForegroundWindow())
        return title.startswith("Minecraft* 1.15.2")

    @staticmethod
    def _is_in_minecraft_world() -> bool:
        title: str = win32.win32gui.GetWindowText(
            win32.win32gui.GetForegroundWindow())
        return title.startswith("Minecraft* 1.15.2") and not title.endswith("1.15.2")

    def _get_seed(self) -> str:
        self._seed_lock.acquire()
        seed = self._seed
        self._seed_lock.release()
        return seed

    def _set_seed(self, seed: str) -> None:
        self._seed_lock.acquire()
        self._seed = seed
        self._seed_lock.release()

    def _get_running_finder(self) -> bool:
        self._running_finder_lock.acquire()
        running_finder = self._running_finder
        self._running_finder_lock.release()
        return running_finder

    def _set_running_finder(self, running_finder: bool) -> None:
        self._running_finder_lock.acquire()
        self._running_finder = running_finder
        self._running_finder_lock.release()

    def _get_running_macro(self) -> bool:
        self._running_macro_lock.acquire()
        running_macro = self._running_macro
        self._running_macro_lock.release()
        return running_macro

    def _set_running_macro(self, running_macro: bool) -> None:
        self._running_macro_lock.acquire()
        self._running_macro = running_macro
        self._running_macro_lock.release()

    def _run_filter_thread(self):
        if not self._get_running_finder():
            self._set_running_finder(True)
            self._filter_thread = threading.Thread(
                target=self._filter_activity)
            self._filter_thread.start()

    def _filter_activity(self):
        if self._fsg_runner.run_filter():
            result = self._fsg_runner.read_file()
            self._set_seed(result[0])
            TokenLogger.log(result[0], result[1])
        else:
            print("!!! NO FSG JAR FOUND !!!")
        self._set_running_finder(False)


def closing_sequence():
    print("Macro will not run, closing in 10 seconds...")
    time.sleep(5)
    print("5...")
    time.sleep(1)
    print("4...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)


def main():
    json_settings: dict
    successful_load: bool
    if os.path.isfile(SETTINGS_LOCATION):
        try:
            with open(SETTINGS_LOCATION, "r") as json_file:
                json_settings = json.load(json_file)
                json_file.close()
                successful_load = True
        except:
            print("!!! Failed to read .json file, format is probably wrong !!!")
            successful_load = False
            time.sleep(1)
            closing_sequence()
    else:
        successful_load = False
        json_settings = DEFAULT_SETTINGS.copy()
        with open(SETTINGS_LOCATION, "w+") as json_file:
            json.dump(DEFAULT_SETTINGS, json_file, indent=4)
            json_file.close()
        print("!!! No json file found, created defaults !!!")
        time.sleep(1)
        closing_sequence()
    
    if FSGRunner._get_jar() is None:
        successful_load = False
        print("!!! No FSG jar found, please download one and/or place in the same directory !!!")
        time.sleep(1)
        closing_sequence()

    if successful_load:
        print("Load successful, FSG115Macro is now running.")
        fm = FSG115Macro(
            json_settings.get("threads", DEFAULT_SETTINGS["threads"]),
            json_settings.get("java", DEFAULT_SETTINGS["java"]),
            json_settings.get("filterWhilePlaying",
                              DEFAULT_SETTINGS["filterWhilePlaying"]),
            json_settings.get("useAtum", DEFAULT_SETTINGS["useAtum"]),
            json_settings.get("waitTime", DEFAULT_SETTINGS["waitTime"]),
            json_settings.get("stopResetsLocation",
                              DEFAULT_SETTINGS["stopResetsLocation"]),
            json_settings.get("minecraftDir", DEFAULT_SETTINGS["minecraftDir"])
        )

        global_hotkeys.register_hotkeys([
            [json_settings.get("hotkey", DEFAULT_SETTINGS["hotkey"]).split(
                "+"), fm.run_macro, None]
        ])
        global_hotkeys.start_checking_hotkeys()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
