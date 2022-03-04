# FSG115-Macro
 Macro for 1.15 FSG written in python.

## Usage

Run the provided .exe file in releases or run the source .py file to start the macro. If you do not already have an options file it will create one on the first run.

A 1.15 FSG Jar file is required to run this macro. You can download one from https://github.com/DuncanRuns/FSG115/releases. The .bat file(s) are not required to run the macro. The macro will automatically find the most updated version in the same folder.

The macro is running if the console window is open. Activate the macro by pressing the hotkey specified in the options file (default: `u`). You can activate it from inside a world (with no menus open) or from the title screen.

To stop the macro, close the console window containing it.

## Options File

The options file `FSG115Macro.json` is a json file created when running the macro if it does not already exist. The macro will close itself immediately if it must create the file.

Once created, the file should have various options which you are able to customize.

- `threads` - default: `4`
    - Specifies how many threads the filter should run in order to find a seed. More = Faster = Laggier
- `java` - default: `"java"`
    - Specifies the location of java which will be used for the filter. The default "java" means that it will use the system default.
- `hotkey` - default: `"u"`
    - Specifies the hotkey used to activate the macro. Can be multiple keys, given that they are seperated by a plus symbol (`+`). [Key names can be found here](https://github.com/DuncanRuns/FSG115-Macro/blob/main/keys.txt).
- `filterWhilePlaying` - default: `false`
    - Specifies whether the macro will immediately begin searching for a new seed as soon as you enter the world to prevent waiting on the main menu.
- `useAtum` - default: `false`
    - Specifies whether to use the Atum mod to load into the seed.
- `waitTime` - default: `0.1`
    - Specifies the amount of time the macro will pause on each screen when creating the world **without atum**. This setting does not do anything if `useAtum` = `true`.
- `stopResetsLocation` - default: `13`
    - Specifies the amount of tab presses needed to get to the "Stop Resets & Quit" button provided by atum. This setting does not do anything if `useAtum` = `false`.
- `minecraftDir` - default: user's default launcher .minecraft
    - Usually ends in `.minecraft`. **Do not specify the saves folder**. 
    - The format must use either double backslash `\\` or forwards slashes `/`. **No single backslashes**.
    - Specifies the game directory in use. This value is used to determine the location of latest.log and lets the macro know when you are done exiting the world.

After changing values in the options file, a restart of the macro is required in order for the changes to take effect.
