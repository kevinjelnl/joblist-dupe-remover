# Removes duplicates from a joblist xml
Scans the joblist.xml to check for duplicates and removes them.

Notifies after running the amount of dupes that are removed on the cmdline:
![Example](./example.png?raw=true)

The ./data folder contains the original jobfile.xml and the clean one after running trough the script. 

## Data
Use the -f flag to select the xml file as input variable. Writes the joblist out with a postfix _clean (this should not be used in production!).
