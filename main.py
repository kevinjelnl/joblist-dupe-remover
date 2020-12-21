import argparse
from pathlib import Path
import logging
import xml.etree.ElementTree as ET
import collections

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


def find_duplicates(xmlfile):
    """Find the dupes in the xml

    Args:
        xmlfile (etree): The parsed jobfile

    Returns:
        list: The list with duplicated etree items
    """
    namelist = []
    dupelist = []
    for item in xmlfile.findall(".//Item"):
        name = item.find("Name").text
        if name in namelist:
            dupelist.append(item)
            continue
        namelist.append(name)
    if dupelist:
        return dupelist
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
    save_path = Path(str(floc).replace(".xml", "_clean.xml"))
    with open(f"{save_path}", "wb") as f:
        f.write(ET.tostring(xmlfile))
    return


def cl_args():
    parser = argparse.ArgumentParser(
        description="Recreates a joblist")
    parser.add_argument(
        "-f", nargs=1, required=True, help="The location of the joblist")
    return parser.parse_args()


def main():
    args = cl_args()
    fileloc = Path(args.f[0])
    xmlfile = loadXML(fileloc)
    dupes = find_duplicates(xmlfile)
    if not dupes:
        return
    write_joblist(xmlfile, fileloc, dupes)
    log.info(f"Amount of duplicates removed: {len(dupes)}")
    return


if __name__ == "__main__":
    main()
    pass
