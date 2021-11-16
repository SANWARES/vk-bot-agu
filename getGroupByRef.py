from schedule_group import Group_1_back
test = Group_1_back()

dir_new = {}

for podr in test.items():
    print(podr[0])
    dir_new[podr[0]] = {}
    for group in podr[1].items():
        print(group)
        dir_new[podr[0]][group[1]] = group[0]

    print(dir_new)