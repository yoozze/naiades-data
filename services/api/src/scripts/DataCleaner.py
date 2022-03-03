
import csv
import os

class DataCleaner:

    def __init__(self, fileDataPath, fileDataName):

        # file data path
        self.fileDataPath = fileDataPath
        self.fileDataName = fileDataName

        # data vars
        self.fields2ReadIndexes = {}
        self.dataArray = []
        self.dataByFieldsName = {}

    def readFile2DataObject(self, fields2Read):
        '''
        Function reads csv into a dataArray and skips non time-incremental samples as well as rows with empty values.

        :param fields2Read: array of fields to be read
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, self.fileDataName)
        with open(fullFilePath, encoding='utf-8') as source_file:

            csv_reader = csv.reader(source_file, delimiter=',')
            loop_n = 0
            for row in csv_reader:

                # just in case: ignore empty lines
                # just in case: ignore empty lines

                if len(row) == 0:
                    continue

                # 0 row
                # 0 row

                if loop_n == 0:
                    # extract data indexes
                    for fieldName in fields2Read:
                        index = row.index(fieldName)
                        self.fields2ReadIndexes[index] = fieldName

                    loop_n += 1
                    continue

                # skip first row due to derivatives
                # skip first row due to derivatives

                if loop_n == 1:
                    loop_n += 1
                    old_row = row
                    continue

                # timeseries must be incremental
                # timeseries must be incremental

                time_int = int(float(row[0]))
                time_old_int = int(float(old_row[0]))
                if time_old_int == time_int:
                    # ignore repeating time value
                    old_row = row
                    continue
                if time_old_int > time_int:
                    # ignore past sample in the row
                    continue

                # have empty fields?
                # have empty fields?

                areFieldsEmpty = False
                for index,fieldName in self.fields2ReadIndexes.items():
                    if row[index] == "":
                        areFieldsEmpty = True
                        #print(row)
                        continue

                if areFieldsEmpty:
                    continue

                # assign non empty values to self.dataByFieldsName
                # assign non empty values to self.dataByFieldsName

                for index,fieldName in self.fields2ReadIndexes.items():
                    if index not in self.dataByFieldsName:
                        self.dataByFieldsName[index] = []
                    self.dataByFieldsName[index].append(float(row[index]))

                self.dataArray.append(row)
                old_row = row

            # sort data
            for index, fieldName in self.fields2ReadIndexes.items():
                self.dataByFieldsName[index].sort()

        return None

    def printMaxMinValues(self, fieldName, numValues = 50):

        fieldIndex = list(self.fields2ReadIndexes.keys())[list(self.fields2ReadIndexes.values()).index(fieldName)]

        print(fieldName)
        print("First 100 values:")
        print(self.dataByFieldsName[fieldIndex][0:numValues])

        print("Last 100 values:")
        print(self.dataByFieldsName[fieldIndex][-numValues:])
        print()

        return None

    def removeRowsWithValuesOutOfRange(self, fieldName, minValue, maxValue):
        '''
        Function removes rows with values out of range.

        :param fieldName: name of the filed
        :param minValue: min allowed value
        :param maxValue: max allowed value
        :return: None
        '''

        fieldIndex = list(self.fields2ReadIndexes.keys())[list(self.fields2ReadIndexes.values()).index(fieldName)]
        newDataArray = []
        self.dataByFieldsName[fieldIndex] = []

        for row in self.dataArray:
            if float(row[fieldIndex]) < minValue:
                continue
            if float(row[fieldIndex]) > maxValue:
                continue

            # all good, append data
            # all good, append data

            newDataArray.append(row)
            self.dataByFieldsName[fieldIndex].append(float(row[fieldIndex]))

        self.dataArray = newDataArray
        self.dataByFieldsName[fieldIndex].sort()
        return None

    def save2File(self, fileName, fieldsOutputTitles):
        '''
        Function saves self.dataArray to a file

        :param fileName: name of the target file
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, fileName)

        with open(fullFilePath, mode='w', encoding='utf-8') as target_file:
            #data_writer = csv.writer(target_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer = csv.writer(target_file, delimiter=',')

            # write header
            # write header

            #fieldsList = ['time'] + list(self.fields2ReadIndexes.values())
            fieldsList = ['time'] + fieldsOutputTitles
            data_writer.writerow(fieldsList)

            # write data
            # write data

            for row in self.dataArray:
                # create row
                new_row = [row[0]]
                for index, fieldName in self.fields2ReadIndexes.items():
                    new_row.append(row[index])
                # save data
                data_writer.writerow(new_row)
