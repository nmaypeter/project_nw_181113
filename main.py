from Diffusion_NormalIC_v2 import *

if __name__ == "__main__":
    diffusionthrehold = 0.01
    for setting in range(1, 7):
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

        ini = Initialization(data_name)

        graph_dict = ini.constructGraphDict()
        seedcost_dict = ini.constructSeedCostDict()

        product_list = []
        with open("product/" + product_name + ".txt") as f:
            for line in f:
                (p, c, r, price) = line.split()
                product_list.append([float(p), float(c), round(float(p) + float(c), 2)])

        eva = Evaluation(graph_dict, product_list, diffusionthrehold)
        total_budget = 1
        times = 50 - 1

        for total_budget in range(1, 11):
            result_name = "result/" + data_name + "_" + product_name + "/" + data_name + "_" + product_name + "_b" + str(total_budget) + "_i" + str(times+1) + ".txt"
            fileresult = eva.getFileResult(result_name)
            seed_result_list, avg_pr_list = eva.sortResult(fileresult)
            print(setting, total_budget, avg_pr_list)