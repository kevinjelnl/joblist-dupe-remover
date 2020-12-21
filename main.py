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
    try:
        tree = ET.parse(infile)
        return tree.getroot()
    except Exception as error:
        log.critical(f" {error}")
        raise SystemExit("Could not parse given joblist!")


def find_duplicates(xmlfile):
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
