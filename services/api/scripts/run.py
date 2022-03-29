#!/usr/bin/python

import os
import sys
import getopt


def main(argv):

    cliHelp = 'run.py -i <input_file> -o <output_file> -d <delta_time_secs>'

    # Define base params
    deltaTime = 3600
    inputFile = ''
    outputFile = ''

    # Read input arguments
    try:
        opts, args = getopt.getopt(
            argv, "hi:o:d:", ["ifile=", "dtime="])
    except getopt.GetoptError:
        print(cliHelp)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(cliHelp)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg
        elif opt in ("-d", "--dtime"):
            deltaTime = int(arg)

    # Exit if required arguments are missing
    if inputFile == '' or outputFile == '':
        print(cliHelp)
        sys.exit()

    # Exit if input file doesn't exists
    if not os.path.isfile(inputFile):
        print("File <" + inputFile + "> not found.")
        sys.exit()

    # Make sure that output dir exists
    outputFilePath = os.path.dirname(outputFile)
    os.makedirs(outputFilePath, exist_ok=True)

    import DataCleaner

    # Define output file & fields to target
    dataCleanerOutputFile = outputFile + ".temp"
    targetFields = ["flow_rate_value", "totalizer1", "totalizer2", "consumer_totalizer",
                    "analog_input1", "analog_input2", "batery_capacity", "alarms_in_decimal"]

    # Clean data
    dc = DataCleaner.DataCleaner(inputFile)
    dc.readFile2DataObject(targetFields)
    dc.save2File(dataCleanerOutputFile)

    # Aggregate data
    import DataAggregator

    da = DataAggregator.DataAggregator(dataCleanerOutputFile)
    da.readFile2DataObject(targetFields)
    da.aggregateData(deltaTime)
    da.save2File(outputFile)

    #  Remove temp cleaned file
    os.remove(dataCleanerOutputFile)


if __name__ == "__main__":
    main(sys.argv[1:])
