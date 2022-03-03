
import csv
import os
import datetime

class DataAggregator:

    def __init__(self, fileDataPath, fileDataName):

        # file data path
        self.fileDataPath = fileDataPath
        self.sourceFileName = fileDataName

        # data vars
        self.fields2ReadIndexes = {}
        self.dataSourceArray = []
        self.dataAggregateArray = []

    def readFile2DataObject(self, fields2Read):
        '''
        Function reads csv into a dataSourceArray.

        :param fields2Read: array of fields to be read
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, self.sourceFileName)
        with open(fullFilePath, encoding='utf-8') as source_file:

            csv_reader = csv.reader(source_file, delimiter=',')
            loop_n = 0
            for row in csv_reader:

                # header
                # header

                if loop_n == 0:
                    # extract data indexes
                    for fieldName in fields2Read:
                        index = row.index(fieldName)
                        self.fields2ReadIndexes[index] = fieldName

                    loop_n += 1
                    continue

                # data
                # data

                self.dataSourceArray.append(row)

        return None

    def aggregateData(self, fileNameTag, deltaTimeInSeconds, timeWindow = [-1,-1], filterDataToTimeInterval = []):
        '''
        Functins aggregates data according given parameters.

        :param fileNameTag: prependix to a file name
        :param deltaTimeInSeconds: the delta time between two consecutive samples
        :param timeWindow: array of two unix timestamps defining the timewindow of samples to be included; -1 is undefined, including all of the samples
        :param filterDataToTimeInterval: array of thwo hours: the first number sets hour from and the second hour to; for example [0,4] will retain samples between midnight and 4am
        :return: None
        '''

        # aggregate data
        # aggregate data

        self.dataAggregateArray = []
        aggregatedValues_temp = {}
        for index, fieldName in self.fields2ReadIndexes.items():
            aggregatedValues_temp[index] = 0.0
        # define time window
        time_window_from = timeWindow[0]
        if time_window_from < 0:
            first_row = self.dataSourceArray[0]
            time_window_from = float(first_row[0])

        time_window_to = timeWindow[1]
        if time_window_to < 0:
            last_row = self.dataSourceArray[-1:][0]
            time_window_to = float(last_row[0])

        time_aggregate = 0
        num_of_ephos = 0
        for row in self.dataSourceArray:
            time_current = int(float(row[0]))

            # check if sample within time window
            # check if sample within time window

            if time_window_from > time_current:
                continue
            if time_window_to < time_current:
                continue

            if len(filterDataToTimeInterval) > 0:
                # concert unix time to date
                dt = datetime.datetime.fromtimestamp(time_current)
                if dt.hour < filterDataToTimeInterval[0]:
                    continue
                if dt.hour > filterDataToTimeInterval[1]:
                    continue

            # initialize
            # initialize

            if time_aggregate == 0:
                time_aggregate = time_current + deltaTimeInSeconds

            # extract aggregated values
            # extract aggregated values

            if time_current >= time_aggregate:
                # execute aggregation
                # self.fields2ReadIndexes[index] = fieldName
                new_row = [time_aggregate]
                for index, fieldName in self.fields2ReadIndexes.items():
                    new_row.append(aggregatedValues_temp[index] / num_of_ephos)
                self.dataAggregateArray.append(new_row)

                # reset vars
                time_aggregate = time_current + deltaTimeInSeconds
                num_of_ephos = 0
                for index, fieldName in self.fields2ReadIndexes.items():
                    aggregatedValues_temp[index] = 0.0

            # aggregate
            # aggregate

            num_of_ephos += 1
            for index, fieldName in self.fields2ReadIndexes.items():
                aggregatedValues_temp[index] += float(row[index])

        # save aggregated data to file
        # save aggregated data to file

        fileName = fileNameTag + "-" + str(deltaTimeInSeconds)
        if time_window_from > 0:
            fileName += "-F" + str(int(time_window_from))
        else:
            fileName += "-F0"
        if time_window_to > 0:
            fileName += "-T" + str(int(time_window_to))
        else:
            fileName += "-T0"
        if len(filterDataToTimeInterval) > 0:
            fileName += "-hourFrom" + str(filterDataToTimeInterval[0]) + "-hourTo" + str(filterDataToTimeInterval[1])
        fileName += ".csv"

        self.save2File(fileName)
        return None


    def save2File(self, fileName):
        '''
        Function saves self.dataAggregateArray to a file

        :param fileName: name of the target file
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, fileName)

        with open(fullFilePath, mode='w', encoding='utf-8') as target_file:
            #data_writer = csv.writer(target_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer = csv.writer(target_file, delimiter=',')

            # write header
            # write header

            fieldsList = ['time'] + list(self.fields2ReadIndexes.values())
            data_writer.writerow(fieldsList)

            # write data
            # write data

            for row in self.dataAggregateArray:
                data_writer.writerow(row)