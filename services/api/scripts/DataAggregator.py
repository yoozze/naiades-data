
import csv
import os
import datetime


class DataAggregator:

    def __init__(self, dataFilePath):
        self.dataFilePath = dataFilePath
        self.destinationFileName = ''
        self.fields2ReadIndexes = {}
        self.dataSourceArray = []
        self.dataAggregateArray = []

    def readFile2DataObject(self, fields2Read):
        '''
        Function reads csv into a dataSourceArray.

        :param fields2Read: array of fields to be read
        :return: None
        '''

        with open(self.dataFilePath, encoding='utf-8') as source_file:

            csv_reader = csv.reader(source_file, delimiter=',')
            loop_n = 0
            for row in csv_reader:

                # Header
                if loop_n == 0:
                    # Extract data indexes
                    for fieldName in fields2Read:
                        index = row.index(fieldName)
                        self.fields2ReadIndexes[index] = fieldName

                    loop_n += 1
                    continue

                # Data
                self.dataSourceArray.append(row)

        return None

    def aggregateData(self, deltaTimeInSeconds, timeWindow=[-1, -1], filterDataToTimeInterval=[]):
        '''
        Functins aggregates data according given parameters.

        :param fileNameTag: prependix to a file name
        :param deltaTimeInSeconds: the delta time between two consecutive samples
        :param timeWindow: array of two unix timestamps defining the timewindow of samples to be 
        included; -1 is undefined, including all of the samples
        :param filterDataToTimeInterval: array of thwo hours: the first number sets hour from and 
        the second hour to; for example [0,4] will retain samples between midnight and 4am
        :return: None
        '''

        # Aggregate data
        self.dataAggregateArray = []
        aggregatedValues_temp = {}
        for index, fieldName in self.fields2ReadIndexes.items():
            aggregatedValues_temp[index] = 0.0

        # Define time window
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

            # Check if sample within time window
            if time_window_from > time_current:
                continue
            if time_window_to < time_current:
                continue

            if len(filterDataToTimeInterval) > 0:
                # Concert unix time to date
                dt = datetime.datetime.fromtimestamp(time_current)
                if dt.hour < filterDataToTimeInterval[0]:
                    continue
                if dt.hour > filterDataToTimeInterval[1]:
                    continue

            # Initialize
            if time_aggregate == 0:
                time_aggregate = time_current + deltaTimeInSeconds

            # Extract aggregated values
            if time_current >= time_aggregate:
                # Aggregate
                new_row = [time_aggregate]
                for index, fieldName in self.fields2ReadIndexes.items():
                    new_row.append(aggregatedValues_temp[index] / num_of_ephos)
                self.dataAggregateArray.append(new_row)

                # Reset vars
                time_aggregate = time_current + deltaTimeInSeconds
                num_of_ephos = 0
                for index, fieldName in self.fields2ReadIndexes.items():
                    aggregatedValues_temp[index] = 0.0

            # Aggregate
            num_of_ephos += 1
            for index, fieldName in self.fields2ReadIndexes.items():
                aggregatedValues_temp[index] += float(row[index])

        return None

    def save2File(self, filePath):
        '''
        Function saves self.dataAggregateArray to a file

        :param fileName: name of the target file
        :return: None
        '''

        with open(filePath, mode='w', encoding='utf-8') as target_file:
            data_writer = csv.writer(target_file, delimiter=',')

            # Write header
            fieldsList = ['time'] + list(self.fields2ReadIndexes.values())
            data_writer.writerow(fieldsList)

            # Write data
            for row in self.dataAggregateArray:
                data_writer.writerow(row)
