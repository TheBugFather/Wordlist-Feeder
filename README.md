<div align="center" style="font-family: monospace">
<h1>Wordlist-Feeder</h1>
&#9745;&#65039; Bandit verified &nbsp;|&nbsp; &#9745;&#65039; Synk verified &nbsp;|&nbsp; &#9745;&#65039; Pylint verified 9.88/10
<br><br>

![alt text](https://github.com/ngimb64/Wordlist-Feeder/blob/main/WordlistFeeder.png?raw=true)
</div>

## Purpose
Wordlist feeder is designed to assist automating bruting/fuzzing tools with numerous wordlists.
All the desired wordlists to be executed are stored in the WordlistDock and feed into executable to brute/fuzz.

### License
The program is licensed under [GNU Public License v3.0](LICENSE.md)

### Contributions or Issues
[CONTRIBUTING](CONTRIBUTING.md)

## Prereqs
This program runs on Windows 10 and Debian-based Linux, written in Python 3.10.6

This program is updated to Python version 3.10.6 .

## Installation
- Run the setup.py script to build a virtual environment and install all external packages in the created venv.

> Examples:<br> 
>       &emsp;&emsp;- Windows:  `python setup.py venv`<br>
>       &emsp;&emsp;- Linux:  `python3 setup.py venv`

- Once virtual env is built traverse to the (Scripts-Windows or bin-Linux) directory in the environment folder just created.
- For Windows, in the venv\Scripts directory, execute `activate` or `activate.bat` script to activate the virtual environment.
- For Linux, in the venv/bin directory, execute `source activate` to activate the virtual environment.
- If for some reason issues are experienced with the setup script, the alternative is to manually create an environment, activate it, then run pip install -r packages.txt in project root.
- To exit from the virtual environment when finished, execute `deactivate`.

## How it works
> Example: `python wordlist_feeder.py "C:\Users\Username\Documents\Tools\hashcat-6.2.5\hashcat.exe" "<exec_name> -m 10900 -a 0 -o cracked.txt hashes.txt <wordlist>"`

- If hashes are cracked in this example they would be saved in cracked.txt located in the hashcat directory specified in the first arg

- Make sure hashes file is in the same directory as target executable in first arg (hashcat, john, wfuzz, etc)
- The first arg is the path to the target executable, which is used for changing directories and command execution
- The second arg is the command syntax of the target executable with two parameters:
  - <exec_name> - the name of the executable to launch command syntax
  - \<wordlist> - the path to the wordlist to be feed into the executable tool