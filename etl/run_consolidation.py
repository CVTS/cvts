import sys
from consolidate_month import ConsolidateWholeMonth


def main(month):
    cwm = ConsolidateWholeMonth(month)
    cwm.consolidate()


if __name__ == '__main__':
    month = sys.argv[1]
    main(month)
