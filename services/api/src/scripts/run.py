#!/usr/bin/python

import sys
import getopt

import DataAggregator


def main(argv):
    input_file = ''
    # output_file = ''
    delta_time = 3600
    try:
        opts, args = getopt.getopt(
            argv, "hi:o:d:", ["ifile=", "dtime="])
    except getopt.GetoptError:
        print('run.py -i <input_file> -d <delta_time>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -i <input_file> -d <delta_time>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        # elif opt in ("-o", "--ofile"):
        #     output_file = arg
        elif opt in ("-d", "--dtime"):
            delta_time = int(arg)
    print('Input file is', input_file)
    # print('Output file is', output_file)
    print('Delta time is', delta_time)

    da = DataAggregator.DataAggregator('', input_file)
    da.readFile2DataObject(["flow_rate_value", "totalizer1", "totalizer2", "consumer_totalizer",
                           "analog_input1", "analog_input2", "batery_capacity", "alarms_in_decimal"])
    da.aggregateData("flow", delta_time)


if __name__ == "__main__":
    main(sys.argv[1:])
