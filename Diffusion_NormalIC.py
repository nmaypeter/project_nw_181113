from Initialization import *
import time

class NormalIC():
    def __init__(self, graph_dict, seedcost_dict, total_budget, num_product, product_list, ctrlexpect):
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
        ### ctrlexpect: (str) the controller for which expected function is used
        self.graph_dict = graph_dict
        self.seedcost_dict = seedcost_dict
        self.total_budget = total_budget
        self.num_product = num_product
        self.product_list = product_list
        self.ctrlexpect = ctrlexpect
        self.diffusionthrehold = 0.01

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
        ep = 0.0

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        if nnode in self.graph_dict:
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

    def getMostValuableSeed(self, a_node_set, b_set, cur_budget):
        # -- find the seed with maximum expected profit from all combinations of nodes and products --
        ### mep: (list) the current maximum expected profit: [expected profit, which product, which node]
        ### expect_profit_list: (list) the list of expected profit for all combinations of nodes and products
        ### expect_profit_list[k]: (list) the list of expected profit for k-product
        ### expect_profit_list[k][i]: (float4) the expected profit for i-node for k-product
        mep = [0.0, 0, '-1']
        expect_profit_list = []
        for num in range(self.num_product):
            expect_profit_list.append([])

        nc = NormalIC(self.graph_dict, self.seedcost_dict, self.total_budget, self.num_product, self.product_list, self.ctrlexpect)
        for k in range(self.num_product):
            for i in self.seedcost_dict:
                # print(k, i)
                if i in b_set:
                    ep = 0.0
                elif self.seedcost_dict[i] + cur_budget > self.total_budget:
                    # print("over budget: " + str(i))
                    b_set.add(i)
                    ep = 0.0
                else:
                    ep = nc.getSeedExpectProfit(k, i, 1.0, a_node_set[k])

                expect_profit_list[k].append(ep)
                if self.ctrlexpect == "p":
                    if ep > mep[0]:
                        mep = [ep, k, i]
                elif self.ctrlexpect == "d":
                    if self.seedcost_dict[i] == 0:
                        continue
                    if mep[2] not in self.seedcost_dict:
                        d = 0.0
                    else:
                        d = mep[0] / self.seedcost_dict[mep[2]]
                    if ep / self.seedcost_dict[i] > d:
                        mep = [ep, k, i]

        return mep, ban_set

    def addSeedIntoSeedSet(self, mep, s_set, a_n_set, b_set, cur_profit, cur_budget):
        # -- add the seed with maximum expected profit into seed set --
        s_set[mep[1]].add(mep[2])
        a_n_set[mep[1]].add(mep[2])
        b_set.add(mep[2])
        # print("into seedset: " + str(mep[2]))
        cur_profit += self.product_list[mep[1]][0]
        cur_budget += self.seedcost_dict[mep[2]]

        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when seed is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from seed
        try_a_n_list = []
        # -- add the receivers of seed into try_a_n_list --
        # -- notice: prevent the seed from owing no receiver --
        if mep[2] in self.graph_dict:
            outdict = self.graph_dict[mep[2]]
            for out in outdict:
                if float(outdict[out]) >= self.diffusionthrehold and out not in a_n_set[mep[1]]:
                    try_a_n_list.append([out, float(outdict[out])])

        # -- activate the candidate nodes actually --
        while len(try_a_n_list) > 0:
            rr = random.random()
            if rr < try_a_n_list[0][1]:
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
        return s_set, a_n_set, b_set, cur_profit, cur_budget

if __name__ == "__main__":
    ## input ##
    ## data_name: (str) the dataset ##
    ## product_name: (str) the product ##
    ## total_budget: (int) the seed budget ##
    ## num_price: (int) the kinds of generated price ##
    ## num_ratio: (int) the kinds of generated ratio ##
    ## ctrlexpect: (str) the controller for which expected function is used ##
    data_name = "email"
    product_name = "prod_ratio_similar_n3p1"
    total_budget = 1
    num_price, num_ratio = 3, 1
    num_product = num_price * num_ratio
    ctrlexpect = "p"

    ini = Initialization(data_name)

    graph_dict = ini.constructGraphDict()
    seedcost_dict = ini.constructSeedCostDict()

    ### product_list: (list) [profit, cost, price]
    product_list = []
    with open("product/" + product_name + ".txt") as f:
        for line in f:
            (p, c, r, pr) = line.split()
            product_list.append([float(p), float(c), round(float(p) + float(c), 2)])

    ### current_profit: (float4) the profit currently
    ### current_budget: (float4) the used budget currently
    ### seed_set: (list) the set of seeds for all products
    ### seed_set[k]: (set) the set of seeds for k-product
    ### activated_node_set: (list) the set of activated nodes for all products
    ### activated_node_set[k]: (set) the set of activated nodes for k-product
    ### ban_set: (set) the set of impossible seeds for all products
    ###                1. it belongs to seed set
    ###                2. it will be over the budget if add the node
    while total_budget <= 1:
        ### result: (list) all results
        ### result[i]: (list) the result after i iteration [current_profit, current_budget, seed_set]
        ### avg_pro: (float4) accumulated profit for iterations in order to avenge
        ### avg_bud: (float4) accumulated budget for iterations in order to avenge
        start_time = time.time()

        iteration_times = 1
        result, avg_pro, avg_bud = [], 0.0, 0.0

        for times in range(iteration_times):
            print("budget = " + str(total_budget) + ", iteration = " + str(times))
            current_profit, current_budget = 0.0, 0.0
            seed_set, activated_node_set, ban_set = [], [], set()
            for num in range(num_product):
                seed_set.append(set())
                activated_node_set.append(set())

            # -- main --
            nc = NormalIC(graph_dict, seedcost_dict, total_budget, num_product, product_list, ctrlexpect)
            while current_budget <= total_budget and len(ban_set) != len(seedcost_dict):
                mep, ban_set = nc.getMostValuableSeed(activated_node_set, ban_set, current_budget)
                if mep[2] == '-1':
                    break
                seed_set, activated_node_set, ban_set, current_profit, current_budget = \
                    nc.addSeedIntoSeedSet(mep, seed_set, activated_node_set, ban_set, current_profit, current_budget)

            result.append([round(current_profit, 2), round(current_budget, 2), seed_set])
            avg_pro += current_profit
            avg_bud += current_budget
            print("time: " + str(round(time.time() - start_time, 2)) + "sec")

            how_long = round(time.time() - start_time, 2)
            print("total time: " + str(how_long) + "sec")
            print(result)

            # fw = open("result/" + data_name + "_" + product_name + "_" + ctrlexpect + "/"
            #           + data_name + "_" + product_name + "_b" + str(total_budget) + "_i" + str(times+1) + "_" + ctrlexpect + ".txt", 'w')
            # fw.write("data = " + data_name + "\n" +
            #          "product= " + str(total_budget) + "\n" +
            #          "iteration_times = " + str(times+1) + "\n" +
            #          "avg_profit = " + str(round(avg_pro / (times+1), 2)) + "\n" +
            #          "avg_budget = " + str(round(avg_bud / (times+1), 2)) + "\n" +
            #          "avg_time = " + str(round(how_long / (times+1), 2)) + "\n")
            #
            # for r in result:
            #     fw.write("\n" + str(result.index(r)) + ", " + str(round(r[0], 2)) + ", " + str(round(r[1], 2)) + ", " + str(r[2]))
            # fw.close()
        total_budget += 1