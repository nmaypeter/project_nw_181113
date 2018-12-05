for total_budget in range(1, 11):
    fileresult = [[], [], []]
    for setting in range(2, 3):
        if setting == 1:
            data_name = "email"
            product_name = "prod_r1p3n1"
            num_ratio, num_price = 1, 3
        elif setting == 2:
            data_name = "email"
            product_name = "prod_r1p3n2"
            num_ratio, num_price = 1, 3
        elif setting == 3:
            data_name = "email"
            product_name = "prod_r1p4n1"
            num_ratio, num_price = 1, 4
        elif setting == 4:
            data_name = "email"
            product_name = "prod_r1p4n2"
            num_ratio, num_price = 1, 4
        elif setting == 5:
            data_name = "email"
            product_name = "prod_r1p5n1"
            num_ratio, num_price = 1, 5
        elif setting == 6:
            data_name = "email"
            product_name = "prod_r1p5n2"
            num_ratio, num_price = 1, 5
        elif setting == 7:
            data_name = "email"
            product_name = "prod_r2p2n1"
            num_ratio, num_price = 2, 2
        elif setting == 8:
            data_name = "email"
            product_name = "prod_r2p2n2"
            num_ratio, num_price = 2, 2
        for times in range(9, 109, 10):
            result_name = "result/" + data_name + "_" + product_name + "_sn/" + data_name + "_" + product_name + "_b" + str(total_budget) + "_i" + str(times+1) + ".txt"
            lnum = 0
            with open(result_name) as f:
                for line in f:
                    lnum += 1
                    if lnum == 1 or lnum == 3:
                        continue
                    elif lnum == 2:
                        (l) = line.split()
                        avg_pro = float(l[2])
                        fileresult[0].append(avg_pro)
                    elif lnum == 4:
                        atime, ttime = "", ""
                        (l) = line.split()
                        avg_time = list(l[5])
                        total_time = list(l[2])
                        for at in avg_time[0: len(avg_time) - 3]:
                            atime = atime + at
                        for tt in total_time[0: len(total_time) - 4]:
                            ttime = ttime + tt
                        fileresult[1].append(float(atime))
                        fileresult[2].append(float(ttime))
                    else:
                        break
    fw = open("result/avg_pro_b" + str(total_budget) + ".txt", 'w')
    for num in fileresult[0]:
        fw.write(str(num) + "\n")
    fw.close()
    fw = open("result/avg_time_b" + str(total_budget) + ".txt", 'w')
    for num in fileresult[1]:
        fw.write(str(num) + "\n")
    fw.close()
    fw = open("result/total_time_b" + str(total_budget) + ".txt", 'w')
    for num in fileresult[2]:
        fw.write(str(num) + "\n")
    fw.close()