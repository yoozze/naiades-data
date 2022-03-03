
import csv
import os
import datetime
import time
import datetime

class DataConverter:

    def __init__(self, fileDataPath, fileDataName):

        # file data path
        self.fileDataPath = fileDataPath
        self.sourceFileName = fileDataName

        # data vars
        self.fields2ReadIndexes = {}
        self.dataSourceArray = []
        self.dataConvertedArray = []

    def readNConvertFile2DataObject(self, dateFormat, conversionRulesDict):
        '''
        Function reads csv into a dataSourceArray.

        :param conversionRulesDict: array of fields with conversion rules
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, self.sourceFileName)
        with open(fullFilePath, encoding='utf-8') as source_file:

            csv_reader = csv.reader(source_file, delimiter=';')
            loop_n = 0
            for row in csv_reader:

                # header
                # header

                if loop_n == 0:
                    # extract data indexes
                    for fieldName,fieldType in conversionRulesDict.items():
                        index = row.index(fieldName)
                        self.fields2ReadIndexes[index] = fieldName

                    loop_n += 1
                    continue

                # data
                # data

                new_row = []
                for indexRow,valueRow in enumerate(row):

                    currFieldName = self.fields2ReadIndexes[indexRow]
                    currConversionRule = conversionRulesDict[currFieldName]

                    if currConversionRule == "time":
                        value = time.mktime(datetime.datetime.strptime(valueRow, dateFormat).timetuple())
                    elif currConversionRule == "float":
                        value = float(valueRow.replace(",", "."))

                    # append converted value
                    new_row.append(value)

                self.dataConvertedArray.append(new_row)

        return None

    def save2File(self, fileName):
        '''
        Function saves self.dataAggregateArray to a file

        :param fileName: name of the target file
        :return: None
        '''

        fullFilePath = os.path.join(self.fileDataPath, fileName)

        # the time value, usually with index 0, must be increasing with index
        # the time value, usually with index 0, must be increasing with index

        if self.dataConvertedArray[0][0] > self.dataConvertedArray[1][0]:
            self.dataConvertedArray.reverse()

        # save data
        # save data

        with open(fullFilePath, mode='w', encoding='utf-8') as target_file:
            #data_writer = csv.writer(target_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer = csv.writer(target_file, delimiter=',')

            # write header
            # write header

            fieldsList = list(self.fields2ReadIndexes.values())
            data_writer.writerow(fieldsList)

            # write data
            # write data

            for row in self.dataConvertedArray:
                data_writer.writerow(row)