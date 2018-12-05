import random
class Initialization():
    def __init__(self, dataname):
        ### dataname, data_data_path, data_weight_path, data_degree_path: (str)
        self.dataname = dataname
        self.data_data_path = "data/" + dataname + "/" + dataname + '_data.txt'
        self.data_weight_path = "data/" + dataname + "/" + dataname + '_weight.txt'
        self.data_degree_path = "data/" + dataname + "/" + dataname + '_degree.txt'
        self.data_wallet_path = "data/" + dataname + "/" + dataname + '_wallet.txt'

    def setEdgeWeight(self):
        #  -- set weight on edge --
        fw = open(self.data_weight_path, 'w')
        with open(self.data_data_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + val + " " + str(round(random.random(), 2)) + "\n")
        fw.close()
        f.close()

    def setSeedCost(self):
        #  -- count the degree --
        ### numnode: (int) the number of nodes in data
        fw = open(self.data_degree_path, 'w')
        with open(self.data_data_path) as f:
            numnode = 0
            list = []
            for line in f:
                (node1, node2) = line.split()
                numnode = max(numnode, int(node1), int(node2))
                list.append(node1)

        for num in range(1, numnode):
            # --- node, the cost of the node ---
            fw.write(str(num) + " " + str(list.count(str(num))) + "\n")
        fw.close()
        f.close()

    def constructSeedCostDict(self):
        # -- calculate the cost for each seed
        ### seedcost: (dict) the set of cost for each seed
        ### seedcost[num]: (float2) the degree of num's seed
        ### numnode: (int) the number of nodes in data
        ### maxdegree: (int) the maximum degree in data
        seedcost = {}
        with open(self.data_degree_path) as f:
            numnode, maxdegree = 0, 0
            list = []
            for line in f:
                (node, degree) = line.split()
                numnode = max(numnode, int(node))
                maxdegree = max(maxdegree, int(degree))
                list.append([node, degree])
            for num in range(numnode + 1):
                seedcost[str(num)] = round(int(list[num][1]) / maxdegree, 2)
        f.close()
        return seedcost

    def constructGraphDict(self):
        # -- build graph --
        ### graph: (dict) the graph
        ### graph[node1]: (dict) the set of node1's receivers
        ### graph[node1][node2]: (str) the weight one the edge of node1 to node2
        graph = {}
        with open(self.data_weight_path) as f:
            for line in f:
                (node1, node2, wei) = line.split()
                if node1 in graph:
                    graph[node1][node2] = str(wei)
                else:
                    graph[node1] = {node2: str(wei)}
        f.close()
        return graph

    def setNodeWallet(self):
        fw = open(self.data_wallet_path, 'w')
        with open(self.data_degree_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + str(round(random.uniform(0, 2), 2)) + "\n")
        fw.close()
        f.close()

class Product():
    def __init__(self, numprice, numratio):
        ### numprice: (int) the kinds of generated price
        ### numratio: (int) the kinds of generated ratio
        ### numproduct: (int) the kinds of generated product
        self.numprice = numprice
        self.numratio = numratio
        self.numproduct = numprice * numratio

    def setPriceRatioSimilar(self):
        # -- set some products with similar ratio --
        ### ratiolist: (list) the set ti store all candidate
        ### ratiolist[num]: (list) [num's profit, num's cost, num's ratio]
        ### ratiolist[num][]: (float2)
        ### maxs: (int) the number for consecutive similar ratio cumulatively, to find the number equal to the product number
        ### sp: (int) the pointer to the last consecutive ratio, to record what products are
        ratiolist = []
        maxs, sp = 0, 0
        while (maxs < self.numproduct - 1):
            generateprofit = round(random.random(), 2)
            generatecost = round(random.random(), 2)
            # -- define the profit and cost and price --
            if generateprofit == 0 or generatecost == 0 or generateprofit + generatecost >= 1:
                continue
            ratiolist.append((generateprofit, generatecost, round(generateprofit / generatecost, 2)))
            # - sort the ratiolist with ratio -
            ratiolist.sort(key=lambda tup: tup[2])
            for num in range(len(ratiolist) - 1):
                if maxs == self.numproduct - 1:
                    continue
                if len(ratiolist) >= self.numproduct and abs(ratiolist[num][2] - ratiolist[num + 1][2]) <= 0.1:
                    s += 1
                    if s >= maxs:
                        maxs = s
                        sp = num
                else:
                    s = 0
                    sp = 0

        ### productlist: (list) the set of output products with similar ratio
        ### productlist[num]: (list) [num's profit, num's cost, num's ratio, num's price]
        ### productlist[num][]: (float2)
        # -- set output products --
        productlist = []
        sp = sp - self.numproduct + 1
        for num in range(self.numproduct):
            sp = sp + 1
            productlist.append(ratiolist[sp])

        fw = open("product/prod_ratio_similar_n" + str(self.numproduct) + "p1000.txt", 'w')
        for p, c, r in productlist:
            # --- profit, cost, ratio, price ---
            fw.write(str(p) + " " + str(c) + " " + str(r) + " " + str(p + c) + "\n")
        fw.close()
        return productlist

    def setPriceDiffRatioDiff(self):
        # -- set the price with different prices and ratios
        ### plist: (list) the list to record different price
        ### plist[num]: (float2) the bias price for output price
        ### rlist: (list) the list to record different ratio
        ### rlist[num]: (float2) the bias ratio for output ratio
        plist, rlist = [], []

        # -- set the bias price --
        # -- the multiple between each bias price has to be greater than 2 --
        ### dp: (int) the definition of price
        dp = 1
        while dp:
            for p in range(self.numprice):
                plist.append(round(random.uniform(p / self.numprice, (p + 1) / self.numprice), 2))

            for p in range(len(plist) - 1):
                if plist[p + 1] - plist[p] < 0.1 or plist[p] < 0.1:
                    dp += 1
                    continue

            if dp == 1:
                dp = 0
            else:
                dp = 1
                plist = []

        # -- set the bias ratio --
        # -- the difference between each bias ratio has to be greater tha 0.1 --
        ### dr: (int) the definition of ratio
        dr = 1
        while dr:
            rlist = []
            for r in range(self.numratio):
                rlist.append(round(random.uniform(0, 2), 2))
                rlist.sort()

            if 0.0 in rlist:
                continue

            for r in range(len(rlist) - 1):
                if rlist[r + 1] / rlist[r] < 2:
                    dr += 1
                    continue
            for r in range(len(rlist) - 1):
                if rlist[r + 1] - rlist[r] < 0.1 or rlist[r] < 0.1:
                    dr += 1
                    continue

            if dr == 1:
                dr = 0
            else:
                dr = 1

        # -- set output products --
        ### productlist: (list) the set to record output products
        ### productlist[num]: (list) [num's profit, num's cost, num's ratio, num's price]
        ### productlist[num][]: (float2)
        productlist = []
        for r in range(len(rlist)):
            for p in range(len(plist)):
                price, profit, cost = 0.0, 0.0, 0.0
                while price == 0.0 or profit == 0.0 or cost == 0.0 or price > 1:
                    price = plist[p] + random.uniform(-0.5, 0.5) * 0.1
                    profit = round(price * (rlist[r] / (1 + rlist[r])), 2)
                    cost = round(price * (1 / (1 + rlist[r])), 2)
                    price = round(profit + cost, 2)
                productlist.append([profit, cost, round((profit / cost), 2), price])

        fw = open("product/prod_r" + str(self.numratio) + "p" + str(self.numprice) + "n1000.txt", 'w')
        for p, c, r, pr in productlist:
            fw.write(str(p) + " " + str(c) + " " + str(r) + " " + str(pr) + "\n")
        fw.close()
        return productlist

if __name__ == "__main__":
    ## input ##
    ## data_name: (str) the dataset ##
    ## num_price: (int) the kinds of generated price ##
    ## num_ratio: (int) the kinds of generated ratio ##
    data_name = "email"
    num_price, num_ratio = 2, 2

    ini = Initialization(data_name)
    prod = Product(num_price, num_ratio)

    # ini.setEdgeWeight()
    # ini.setSeedCost()
    # ini.setNodeWallet()

    graph_dict = ini.constructGraphDict()
    seedcost_dict = ini.constructSeedCostDict()
    # prod.setPriceRatioSimilar()
    prod.setPriceDiffRatioDiff()

    # print(graph_dict)