
'''
Parameters setup:

Creating data sets is done in two steps:
0. converting data (if needed)
1. cleaning raw data
2. creating data sets

0. converting raw data
----
Script is performing various conversions like:
- transformind time data into the unix format (e.g. 11/26/2021 13:14:00 => 1614308400)
- transforming values into floats (e.g. 2,33 => 2.33)

1. cleaning raw data
----
Script clears rows with empty fields, inspects maximums and minimums, which can be removed from raw data set.
@rawDataFileName            is a filename containing raw data
@cleanDataFileName          is a filename containing cleaned data
@targetFields               is the list of fields to be included in cleaned datafile
@targetFieldsOutputTitles   are the fieldnames replacing @targetFields in the output file

2. creating datasets
----
Script takes in cleaned and inspected data file and creates data sets according parameters.
@cleanDataFileNameInspected     is the file name from which data sets are created (this file is - compared to @cleanDataFileName - also manually inspected)
@aggregatedDataFileTag          is a string prepending all output files (containing data sets)
@targetFieldsOutputTitles       are data filed names to be included in output files
'''


# available actions: convert, clean OR aggregate
action = "aggregate"
rawDataFileName = "braila-flow-anomaly-raw.csv"
cleanDataFileName = "braila-flow-anomaly-filtered.csv"
timeFormat = "%m/%d/%Y %H:%M:%S"
coversionFields = {
    "time": "time",
    "flow":"float",
    "pressure":"float"
}
targetFields = ["flow", "pressure"]
targetFieldsOutputTitles = ["flow", "pressure"]
cleanDataFileNameInspected = "braila-flow-anomaly-filtered.csv"
aggregatedDataFileTag = "braila-flow-anomaly"


# ****************************************
# ****************************************

# first, we need to clean data
# first, we need to clean data

if action == "clean":
    import DataCleaner

    filePath = ''
    fileSourceName = rawDataFileName
    fileTargetName = cleanDataFileName

    dc = DataCleaner.DataCleaner(filePath, fileSourceName)
    dc.readFile2DataObject(targetFields)

    '''
    # print extremes to define max and min allowed values
    # print extremes to define max and min allowed values

    dc.printMaxMinValues("flow_rate_value")
    dc.printMaxMinValues("analog_input2")

    # remove rows with illicit values
    # remove rows with illicit values

    dc.removeRowsWithValuesOutOfRange("flow_rate_value", -500, 500)
    #dc.printMaxMinValues("flow_rate_value")
    '''

    # when made sure, no illicit data in the set, save to file
    # when made sure, no illicit data in the set, save to file

    dc.save2File(fileTargetName, targetFieldsOutputTitles)

# ****************************************
# ****************************************

# after cleaning, data needs to be converted
# after cleaning, data needs to be converted

if action == "convert":
    import DataConverter

    filePath = ''
    fileSourceName = rawDataFileName
    fileTargetName = cleanDataFileName

    dcv = DataConverter.DataConverter(filePath, fileSourceName)
    dcv.readNConvertFile2DataObject(timeFormat, coversionFields)
    dcv.save2File(fileTargetName)


# ****************************************
# ****************************************

# second, we need to setup various data samples for analysis
# second, we need to setup various data samples for analysis

if action == "aggregate":
    import DataAggregator

    filePath = ''
    fileSourceName = cleanDataFileNameInspected
    fileTargetTag = aggregatedDataFileTag

    da = DataAggregator.DataAggregator(filePath, fileSourceName)
    da.readFile2DataObject(targetFieldsOutputTitles)

    # execute aggregations (aggregations are automatically saved to file)
    # execute aggregations (aggregations are automatically saved to file)

    #1 hour
    deltaTimeInSeconds = 3600
    da.aggregateData(fileTargetTag, deltaTimeInSeconds)

    # 6 hours
    # deltaTimeInSeconds = 3600 * 6
    # da.aggregateData(fileTargetTag, deltaTimeInSeconds)

    # deltaTimeInSeconds = 3600
    # timeFrame = [1637712300, 1637889840]
    # filter2HoursInDay = [0,4]
    # da.aggregateData(fileTargetTag, deltaTimeInSeconds, timeWindow=timeFrame, filterDataToTimeInterval=filter2HoursInDay)


