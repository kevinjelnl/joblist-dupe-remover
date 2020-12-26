import logging
import os
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
import collections
import subprocess
from time import sleep
import shutil

logging.basicConfig(format='%(asctime)s,%(msecs)d | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)

log = logging.getLogger(__name__)


def loadXML(infile):
    """Tries to parse the given xml file

    Args:
        infile (path): The location of the xml file

    Raises:
        SystemExit: When item could not parsed

    Returns:
        etree: The parsed xml file
    """
    try:
        tree = ET.parse(infile)
        return tree.getroot()
    except Exception as error:
        log.critical(f" {error}")
        raise SystemExit("Could not parse given joblist!")


def find_oldest_item(dupedict):
    """Finds the oldest dupes in the joblist

    Args:
        dupedict (dict): The dict with (all the) dupes

    Returns:
        list: Dupes from the joblist (elements)
    """
    done = []
    dupelist = []
    for k, v in sorted(dupedict.items(), reverse=True):
        if not v["name"] in done:
            done.append(v["name"])
            continue
        dupelist.append(v["elem"])
    return dupelist


def build_item_dict(item):
    itemdict = {
        "name":     item.find("Name").text,
        "status":   item.attrib["Status"],
        "stamp":    item.find("FolderName").text,
        "elem":     item
    }
    return itemdict


def find_duplicates(xmlfile):
    """Find the dupes in the xml

    Args:
        xmlfile (etree): The parsed jobfile

    Returns:
        list: The list with duplicated etree items
    """
    # kv based on names
    jobdict = {}
    # kv based on datetime
    dupedict = {}
    for item in xmlfile.findall(".//Item"):
        itemdict = build_item_dict(item)
        if itemdict["name"] in jobdict:  # dupe found based on: <Name>Element</Name>
            # find original stamp
            origin_stamp = jobdict[itemdict["name"]]["stamp"]
            if not origin_stamp in dupedict:  # original not in dupedict
                dupedict[origin_stamp] = jobdict[itemdict["name"]]
            # add current dupe to dupelist
            dupedict[itemdict["stamp"]] = itemdict
            continue
        # unique item
        jobdict[itemdict["name"]] = itemdict

    if dupedict:
        return dupedict
    return None


def write_joblist(xmlfile, floc, dupes):
    """Writes out the joblist

    Args:
        xmlfile (etree): The original joblist
        floc (Path): The original file location
        dupes (list): The dupelist with etree elements
    """
    for dupe in dupes:
        xmlfile.remove(dupe)
    save_path = Path(str(floc))  # .replace(".xml", "_clean.xml"))
    with open(f"{save_path}", "wb") as f:
        f.write(ET.tostring(xmlfile))
    return


def cleanup_dirs(dupes):
    """Removes the directories

    Args:
        dupes (list): The dupe elements from the joblist
    """
    jobdirs = Path(os.getenv("DC_JOBDIR"))
    for elem in dupes:
        dir_to_remove = elem.find(".//FolderName").text
        shutil.rmtree(str(jobdirs.joinpath(dir_to_remove)))
    return


def handle_app(close=False):
    """Handles the closing and opening of the controller

    Args:
        close (bool, optional): Results in opening or closing the app. Defaults to False.
    """
    msg = "the controller..."
    if close:
        log.info(f"Closing {msg}")
        subprocess.Popen(
            f"taskkill /T /IM {os.getenv('DC_CONTROLLER_IMAGENAME')}", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        log.info(f"Starting {msg}")
        subprocess.Popen(f"{os.getenv('DC_CONTROLLER_LOC')}", shell=False,
                         stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sleep(3)
    return


def test_env():
    """Test if the env vars are set (see set_env.bat)

    Returns:
        bool: True when correct
    """
    env_vars = ["DC_JOBDIR", "DC_CONTROLLER_LOC", "DC_CONTROLLER_IMAGENAME"]
    for envname in env_vars:
        _testenv = os.getenv(f"{envname}")
        if not _testenv:
            log.critical(f"Missing env var: {envname}!")
            return False
    return True


def main():
    if not test_env():
        raise SystemExit(
            "Could not continue because of missing env variables!")

    # close the application
    handle_app(True)

    fileloc = Path(os.getenv("DC_JOBDIR")).joinpath("joblist.xml")
    xmlfile = loadXML(fileloc)
    dupes = find_duplicates(xmlfile)
    if not dupes:
        log.warning(f"No duplicates found...")
        handle_app()
        return

    # handle the removal of the dupes
    items_to_remove = find_oldest_item(dupes)
    cleanup_dirs(items_to_remove)
    write_joblist(xmlfile, fileloc, items_to_remove)
    log.info(f"Amount of duplicates removed: {len(items_to_remove)}")
    # open the app
    handle_app()
    return


if __name__ == "__main__":
    main()
    pass
