file = open('hdb-carpark-information.csv', 'r')

data = file.readlines()

data[1] = data[1].split(',')
for i in range(data[1].__len__()):
    data[1][i] = data[1][i].strip('"')
print(data[1])