from Initialization import *
import time

def sortSecond(val):
    return val[1]

class NormalIC():
    def __init__(self, graph_dict, seedcost_dict, total_budget, num_product, product_list, whether_seed_buy_product_itself, diffusionthrehold):
        ### graph_dict: (dict) the graph
        ### graph_dict[node1]: (dict) the set of node1's receivers
        ### graph_dict[node1][node2]: (float2) the weight one the edge of node1 to node2
        ### seedcost_dict: (dict) the set of cost for each seed
        ### seedcost_dict[num]: (dict) the degree of num's seed
        ### total_ budget: (int) the budget to select seed
        ### num_product: (int) the kinds of products
        ### product_list: (list) the set to record products
        ### product_list[num]: (list) [num's profit, num's cost, num's ratio]
        ### product_list[num][]: (float)
        self.graph_dict = graph_dict
        self.seedcost_dict = seedcost_dict
        self.total_budget = total_budget
        self.num_product = num_product
        self.product_list = product_list
        self.whether_seed_buy_product_itself = whether_seed_buy_product_itself
        self.diffusionthrehold = diffusionthrehold

    def getSeedExpectProfit(self, prod, nnode, activated_prob, a_n_set):
        # -- calculate the expected profit for single node when it's chosen as a seed --
        ### temp_a_n_set: (set) the union set of activated node set and temporary activated nodes when nnode is a new seed
        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when nnode is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from nnode
        ### ep: (float2) the expected profit
        temp_a_n_set = a_n_set.copy()
        temp_a_n_set.add(nnode)
        try_a_n_list = []
        ep = self.seedcost_dict[nnode] * (whether_seed_buy_product_itself - 1)

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        outdict = self.graph_dict[nnode]
        for out in outdict:
            if float(outdict[out]) * activated_prob >= self.diffusionthrehold:
                try_a_n_list.append([out,  float(outdict[out]) * activated_prob])

        while len(try_a_n_list) > 0:
            # -- add the value calculated by activated probability * profit of this product --
            ep += try_a_n_list[0][1] * self.product_list[prod][0]
            # -- add the receiver of node into try_a_n_list --
            # -- notice: prevent the node from owing no receiver --
            if try_a_n_list[0][0] not in self.graph_dict:
                del try_a_n_list[0]
                continue
            # -- activate the receivers temporally --
            if try_a_n_list[0][0] not in temp_a_n_set:
                temp_a_n_set.add(try_a_n_list[0][0])
                outdictw = self.graph_dict[try_a_n_list[0][0]]
                for outw in outdictw:
                    if try_a_n_list[0][1] * float(outdictw[outw]) >= self.diffusionthrehold:
                        try_a_n_list.append([outw, round(try_a_n_list[0][1] * float(outdictw[outw]), 4)])
            del try_a_n_list[0]
        return round(ep, 4)

    def calAllSeedProfit(self):
        # -- calculate expected profit from all combinations of nodes and products --
        ### expect_profit_list: (list) the list of expected profit for all combinations of nodes and products
        ### expect_profit_list[k]: (list) the list of expected profit for k-product
        ### expect_profit_list[k][i]: (float4) the expected profit for i-node for k-product
        expect_profit_list = []
        for num in range(self.num_product):
            expect_profit_list.append([])

        nc = NormalIC(self.graph_dict, self.seedcost_dict, self.total_budget, self.num_product, self.product_list,
                      self.whether_seed_buy_product_itself, self.diffusionthrehold)
        for k in range(self.num_product):
            for i in self.seedcost_dict:
                if i not in self.graph_dict:
                    ep = self.product_list[k][0] * self.whether_seed_buy_product_itself - self.seedcost_dict[i]
                else:
                    ep = nc.getSeedExpectProfit(k, i, 1.0, set())
                expect_profit_list[k].append(ep)
        return expect_profit_list

    def getMostValuableSeed(self, ep_list, nb_set, cur_budget):
        # -- find the seed with maximum expected profit from all combinations of nodes and products --
        ### mep: (list) the current maximum expected profit: [expected profit, which product, which node]
        mep = [0.0, 0, '-1']

        ban_set = []
        for k in range(self.num_product):
            ban_set.append(set())
            for i in nb_set[k]:
                if self.seedcost_dict[i] + cur_budget > self.total_budget:
                    ban_set[k].add(i)
                    continue

                if ep_list[k][int(i)] <= 0:
                    ban_set[k].add(i)
                    continue

                if ep_list[k][int(i)] > mep[0]:
                    mep = [ep_list[k][int(i)], k, i]

        for k in range(self.num_product):
            for i in ban_set[k]:
                nb_set[k].remove(i)

        return mep, nb_set

    def addSeedIntoSeedSet(self, mep, s_set, a_n_set, nb_set, cur_profit, cur_budget):
        # -- add the seed with maximum expected profit into seed set --
        s_set[mep[1]].add(mep[2])
        a_n_set[mep[1]].add(mep[2])
        for k in range(self.num_product):
            if mep[2] in nb_set[k]:
                nb_set[k].remove(mep[2])
        # print("into seedset: " + str(mep[2]))
        cur_profit += self.product_list[mep[1]][0] * self.whether_seed_buy_product_itself
        cur_budget += self.seedcost_dict[mep[2]]

        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when seed is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from seed
        try_a_n_list = []
        # -- add the receivers of seed into try_a_n_list --
        # -- notice: prevent the seed from owing no receiver --
        outdict = self.graph_dict[mep[2]]
        for out in outdict:
            if float(outdict[out]) >= self.diffusionthrehold and out not in a_n_set[mep[1]]:
                try_a_n_list.append([out, float(outdict[out])])

        # -- activate the candidate nodes actually --
        while len(try_a_n_list) > 0:
            rr = random.random()
            if rr <= try_a_n_list[0][1]:
                a_n_set[mep[1]].add(try_a_n_list[0][0])
                cur_profit += self.product_list[mep[1]][0]

                if try_a_n_list[0][0] not in self.graph_dict:
                    del try_a_n_list[0]
                    continue
                outdictw = self.graph_dict[try_a_n_list[0][0]]
                for outw in outdictw:
                    if try_a_n_list[0][1] * float(outdictw[outw]) >= self.diffusionthrehold and outw not in a_n_set[mep[1]]:
                        try_a_n_list.append([outw, try_a_n_list[0][1] * float(outdictw[outw])])
            del try_a_n_list[0]
        return s_set, a_n_set, nb_set, cur_profit, cur_budget

    def updateProfitList(self, k, ep_list, nb_set, a_n_set):
        nc = NormalIC(self.graph_dict, self.seedcost_dict, self.total_budget, self.num_product, self.product_list,
                      self.whether_seed_buy_product_itself, self.diffusionthrehold)
        for i in nb_set[k]:
            ep_list[k][int(i)] = nc.getSeedExpectProfit(k, i, 1.0, a_n_set[k])
        return ep_list

class Evaluation():
    def __init__(self, graph_dict, product_list, diffusionthrehold):
        self.graph_dict = graph_dict
        self.product_list = product_list
        self.diffusionthrehold = diffusionthrehold

    def getFileResult(self, result_name):
        lnum = 0
        with open(result_name) as f:
            fileresult = []
            for line in f:
                lnum += 1
                if lnum <= 5:
                    continue
                (l) = line.split()
                seeds = ""
                for s in l[3: len(l)]:
                    seeds = seeds + s
                fileresult.append([l[0], float(l[1]), float(l[2]), eval(seeds)])
        fileresult.sort(key=sortSecond, reverse=True)
        f.close()
        return fileresult

    def getSeedProfit(self, s_set):
        cur_profit = 0.0
        try_a_n_list = []
        a_n_set, profit_ratio_list = [], []

        for k in range(len(s_set)):
            a_n_set.append(set())
            profit_ratio_list.append(0.0)

        for k in s_set:
            for s in k:
                a_n_set[s_set.index(k)].add(s)
                cur_profit += self.product_list[s_set.index(k)][0]
                if s not in self.graph_dict:
                    continue
                outdict = self.graph_dict[s]
                for out in outdict:
                    if float(outdict[out]) >= self.diffusionthrehold:
                        try_a_n_list.append([s_set.index(k), out, float(outdict[out])])

        while len(try_a_n_list) > 0:
            # random.shuffle(try_a_n_list)
            rr = random.random()
            if rr < try_a_n_list[0][2]:
                a_n_set[try_a_n_list[0][0]].add(try_a_n_list[0][1])
                cur_profit += self.product_list[try_a_n_list[0][0]][0]
                profit_ratio_list[try_a_n_list[0][0]] += self.product_list[try_a_n_list[0][0]][0]

                if try_a_n_list[0][1] not in self.graph_dict:
                    del try_a_n_list[0]
                    continue

                outdictw = self.graph_dict[try_a_n_list[0][1]]
                for outw in outdictw:
                    if try_a_n_list[0][2] * float(outdictw[outw]) >= self.diffusionthrehold and outw not in a_n_set[try_a_n_list[0][0]]:
                        try_a_n_list.append([try_a_n_list[0][0], outw, try_a_n_list[0][2] * float(outdictw[outw])])
            del try_a_n_list[0]
        return round(cur_profit, 2), profit_ratio_list

    def sortResult(self, fileresult):
        seed_result_list = []
        eva = Evaluation(self.graph_dict, self.product_list, self.diffusionthrehold)
        for r in fileresult:
            # print(fileresult.index(r))
            flag = 0
            for sr in seed_result_list:
                if r[3] == sr[2]:
                    flag = 1
            if flag:
                continue
            avg_profit = 0.0
            avg_profit_ratio_list = [0.0] * len(r[3])
            for num in range(10):
                avg_pro, avg_pro_ratio_list = eva.getSeedProfit(r[3])
                avg_profit += avg_pro
                for apr in range(len(r[3])):
                    avg_profit_ratio_list[apr] += avg_pro_ratio_list[apr]
            avg_profit = avg_profit / 10
            for apr in range(len(r[3])):
                avg_profit_ratio_list[apr] = round(avg_profit_ratio_list[apr] / 10, 2)
            seed_result_list.append([fileresult.index(r), round(avg_profit, 2), r[3], avg_profit_ratio_list])
        seed_result_list.sort(key=sortSecond, reverse=True)
        avg_pr_list = [0.0] * len(r[3])
        for sr in seed_result_list:
            for num in range(len(sr[3])):
                avg_pr_list[num] += sr[3][num]
        sumpr = sum(avg_pr_list)
        for num in range(len(avg_pr_list)):
            avg_pr_list[num] = round(100 * avg_pr_list[num] / sumpr, 2)
        return seed_result_list, avg_pr_list

if __name__ == "__main__":
    ## input ##
    ## data_name: (str) the dataset ##
    ## product_name: (str) the product ##
    ## num_price: (int) the kinds of generated price ##
    ## num_ratio: (int) the kinds of generated ratio ##
    ## total_budget: (int) the seed budget ##
    setting = 1
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
    num_product = num_ratio * num_price
    total_budget = 1
    whether_seed_buy_product_itself = 1
    diffusionthrehold = 0.01
    print(data_name, product_name, total_budget, num_ratio, num_price)

    ini = Initialization(data_name)

    graph_dict = ini.constructGraphDict()
    seedcost_dict = ini.constructSeedCostDict()

    ### product_list: (list) [profit, cost, price]
    product_list = []
    with open("product/" + product_name + ".txt") as f:
        for line in f:
            (p, c, r, price) = line.split()
            product_list.append([float(p), float(c), round(float(p) + float(c), 2)])

    # os.mkdir("result/" + data_name + "_" + product_name)
    # os.chdir("result/" + data_name + "_" + product_name)

    ### current_profit: (float4) the profit currently
    ### current_budget: (float4) the used budget currently
    ### seed_set: (list) the set of seeds for all products
    ### seed_set[k]: (set) the set of seeds for k-product
    ### activated_node_set: (list) the set of activated nodes for all products
    ### activated_node_set[k]: (set) the set of activated nodes for k-product
    ### nban_set: (set) the set of possible seeds for all products
    ###                1. it belongs to seed set
    ###                2. it will be over the budget if add the node
    while total_budget <= 2:
        ### result: (list) all results
        ### result[i]: (list) the result after i iteration [current_profit, current_budget, seed_set]
        ### avg_pro: (float4) accumulated profit for iterations in order to avenge
        ### avg_bud: (float4) accumulated budget for iterations in order to avenge
        start_time = time.time()

        iteration_times = 2
        result, avg_pro, avg_bud = [], 0.0, 0.0

        nc = NormalIC(graph_dict, seedcost_dict, total_budget, num_product, product_list,
                      whether_seed_buy_product_itself, diffusionthrehold)

        all_profit_list = nc.calAllSeedProfit()
        for times in range(iteration_times):
            print("budget = " + str(total_budget) + ", iteration = " + str(times))
            current_profit, current_budget = 0.0, 0.0
            seed_set, activated_node_set, nban_set = [], [], []
            for num in range(num_product):
                seed_set.append(set())
                activated_node_set.append(set())
                nban_set.append(set())
                for g in graph_dict:
                    nban_set[num].add(g)
            expect_profit_list = all_profit_list
            mep, nban_set = nc.getMostValuableSeed(expect_profit_list, nban_set, current_budget)

            # -- main --
            while current_budget <= total_budget and mep[2] != '-1':
                seed_set, activated_node_set, nban_set, current_profit, current_budget = \
                    nc.addSeedIntoSeedSet(mep, seed_set, activated_node_set, nban_set, current_profit, current_budget)
                expect_profit_list = nc.updateProfitList(mep[1], expect_profit_list, nban_set, activated_node_set)
                mep, nban_set = nc.getMostValuableSeed(expect_profit_list, nban_set, current_budget)

            result.append([round(current_profit, 2), round(current_budget, 2), seed_set])
            avg_pro += current_profit
            avg_bud += current_budget

            how_long = round(time.time() - start_time, 2)
            print("total time: " + str(how_long) + "sec")
            print(result[times])
            print("avg_profit = " + str(round(avg_pro / (times+1), 2)) + ", avg_budget = " + str(round(avg_bud / (times+1), 2)))

            if (times + 1) % 10 == 0:
                fw = open("result/" + data_name + "_" + product_name + "_sn/" +
                          data_name + "_" + product_name + "_b" + str(total_budget) + "_i" + str(times+1) + ".txt", 'w')
                fw.write("data = " + data_name + ", product= " + str(total_budget) + ", iteration_times = " + str(times+1) + "\n" +
                         "avg_profit_per_iteration = " + str(round(avg_pro / (times+1), 2)) + "\n" +
                         "avg_budget_per_iteration = " + str(round(avg_bud / (times+1), 2)) + "\n" +
                         "total time: " + str(how_long) + "sec, avg_time = " + str(round(how_long / (times+1), 2)) + "sec\n")

                for r in result:
                    fw.write("\n" + str(result.index(r)) + " " + str(round(r[0], 2)) + " " + str(round(r[1], 2)) + " " + str(r[2]))
                fw.close()
        print(data_name, product_name, total_budget, num_price, num_ratio)
        total_budget += 1