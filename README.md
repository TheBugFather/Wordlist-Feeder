### Running program

---
- Make sure hashes file is in the same directory as target executable in first arg (hashcat, john, wfuzz, etc)
- The first arg is the path to the target executable, which is used for changing directories and command execution
- The second arg is the command syntax of the target executable with two parameters:
  - <exec_name> - the name of the executable to launch command syntax
  - \<wordlist> - the path to the wordlist to be feed into the executable tool

Example:

`python wordlist_feeder.py "C:\Users\Rod\Documents\Tools\hashcat-6.2.5\hashcat.exe" "<exec_name> --status --show -m 10900 -a 0 hashes.txt <wordlist>"`

- If hashes are cracked in this example they would be saved in cracked.txt located in the hashcat directory specified in the first arg