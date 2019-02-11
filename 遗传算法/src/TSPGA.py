import random
import numpy
import tsplib95
import math
import copy
import matplotlib.pyplot as plt

global problem # TSP问题
global dimension # problem的规模，即城市的数量
global DisMatrix # 存储城市间距离的矩阵
global paths #存储群体中每个个体的路径
global distances # 存储群体中每个个体的路径长度


POPU_SIZE = 100 #种群规模，即包含多少个体
MAX_GENS = 20000 #最大演化代数
P_CROSSOVER = 0.9 #交叉概率
P_MUTATION = 0.4 #变异概率


# 计算某个路径的长度
def cal_length(aPath):
    dis = 0
    for i in range(dimension - 1):
        dis += DisMatrix[aPath[i]][aPath[i+1]]
    dis += DisMatrix[aPath[dimension - 1]][aPath[0]]
    return dis


#计算种群中每个个体的选择概率，存储在数组中并返回
#采用基于排名的选择，根据个体i的适应值在群体中的排名来分配其选择概率
def cal_p():
    sort_index = numpy.argsort(distances) #得到升序数列对应的索引
    p = numpy.zeros([POPU_SIZE]) #记录每个个体的选择概率的数组

    #根据一个线性函数分配选择概率p
    for i in range(POPU_SIZE):
        p[sort_index[i]] = (1.1 - 0.2*(i+1)/(POPU_SIZE+1))/POPU_SIZE

    #计算概率和，用于转盘赌选择
    sum_p = numpy.zeros([POPU_SIZE])
    for i in range(POPU_SIZE):
        if i == 0:
            sum_p[i] = p[i]
            continue
        sum_p[i] = sum_p[i-1] + p[i]
    return sum_p

#辅助函数
def select_help(n, sum_p):
    for i in range(len(sum_p)):
        if n < sum_p[i]:
            return i

# 按轮盘赌方式选择两个父体进行遗传操作
def select(sum_p):
    n = random.random()
    m = random.random()
    f1 = select_help(n, sum_p)
    f2 = select_help(m, sum_p)
    while f2 == f1:
        m = random.random()
        f2 = select_help(m, sum_p)
    return f1, f2

# 遗传操作产生子代
def generate_son():
    sum_p = cal_p() # 计算选择概率
    f1, f2 = select(sum_p) # 选择两个父体
    fPath1 = copy.deepcopy(paths[f1])
    fPath2 = copy.deepcopy(paths[f2])
    if random.random() < P_CROSSOVER: # 是否进行交叉操作
        shift = math.floor(random.random() + 0.5)
        for i in range(3):
            index = random.randint(1, dimension - 2)
            temp = fPath1[index]
            fPath1[index] = fPath2[index + shift]
            for j in range(dimension):
                if fPath1[j] == fPath2[index + shift]:
                    fPath1[j] = temp
                    break

    if random.random() < P_MUTATION: # 是否变异 
        x_index = random.randint(1, dimension - 1)
        y_index = random.randint(1, dimension - 1)
        while x_index == y_index:
            y_index = random.randint(1, dimension - 1)
        if random.random() < 1/3:
            fPath1[x_index], fPath1[y_index] = fPath1[y_index], fPath1[x_index]
        elif random.random() < 2/3:
            tempPath = copy.deepcopy(fPath1)
            num_min = min(x_index, y_index)
            num_max = max(x_index, y_index)
            temp = tempPath[num_max]
            for i in range(num_max - num_min):
                fPath1[num_max - i] = tempPath[num_max - i - 1]
            fPath1[num_min] = temp
        else:
            tempPath = copy.deepcopy(fPath1)
            num_min = min(x_index, y_index)
            num_max = max(x_index, y_index)
            for i in range(num_max - num_min + 1):
                fPath1[num_min + i] = tempPath[num_max - i]
    return fPath1

# GA算法求解
def tsp_ga():
    genNum = 0 #演化代数
    while genNum < MAX_GENS:
        genNum += 1
        newPaths = [] # 子代
        newDistances = numpy.zeros([POPU_SIZE]) # 子代个体的TSP路径长度

        for i in range(POPU_SIZE):
            newPath = generate_son()
            newPaths.append(newPath)
            newDistances[i] = cal_length(newPath)
    
        for i in range(POPU_SIZE):
            if newDistances[i] < distances[i] or random.random() < 0.2:
                distances[i] = newDistances[i]
                paths[i] = copy.deepcopy(newPaths[i])
        if genNum % 10 == 0:
            print(min(distances))
            generate_picture_dyn(paths[0], distances[0])

def generate_picture_dyn(path, distance): 
    position_x = numpy.zeros([dimension + 1])
    position_y = numpy.zeros([dimension + 1])
    for i in range(dimension):
        position_x[i], position_y[i] = problem.get_display(path[i] + 1)
    position_x[dimension], position_y[dimension] = problem.get_display(path[0] + 1)
    plt.cla() # 清除原有图像
    precision = 100 * (distance - 15780) / 15780
    title = 'distance:' + str(distance) + '    precision:' + str(precision) + '%'
    plt.title(title)
    plt.plot(position_x, position_y, 'b.-')
    plt.pause(0.1)

#计算两个城市之间的距离
def cal_distance(i, j):
    #获取城市(i+1)和(j+1)的坐标
    x1, y1 = problem.get_display(i + 1)
    x2, y2 = problem.get_display(j + 1)
    return math.sqrt((x1-x2)**2 + (y1 - y2)**2)

#生成存储任意两个城市间距离的矩阵
def generate_matrix():
    global DisMatrix
    DisMatrix = numpy.zeros([dimension, dimension]) #创建了一个dim*dim的矩阵，其元素值均为0.0
    for i in range(dimension):
        DisMatrix[i][i] = float("inf") #每个城市到自身的距离设置为正无穷大
        for j in range(i):
            dis = cal_distance(i, j)
            DisMatrix[i][j] = dis #将城市(i+1)和(j+1)之间的距离记入矩阵
            DisMatrix[j][i] = dis #两个城市之间的距离是对称的，得到对称矩阵

#初始化群体
def init_popu():
    global paths
    global distances
    aPath = numpy.array([i+1 for i in range(dimension - 1)]) #城市编号数组，用于打乱来产生一个随机个体
    paths = []
    distances = numpy.zeros([POPU_SIZE])

    for i in range(POPU_SIZE):
        numpy.random.shuffle(aPath)
        currentPath = [0]
        currentPath.extend(aPath)
        paths.append(currentPath)
        distances[i] = cal_length(currentPath)
        

def init():
    global problem
    global dimension
    # 载入TSP问题数据（load_problem 需要指定一个 distance function）
    problem = tsplib95.load_problem("../tc/d198.tsp", special=cal_distance)
    # 初始化变量
    dimension = problem.dimension
    generate_matrix()
    init_popu()
    print("初始路径长度：{0}".format(distances))
    # 打开交互模式，非阻塞画图
    plt.figure(figsize=(8, 6), dpi=80)
    plt.ion()

def main():
    init()
    tsp_ga()
    print("最短路径长度：{0}".format(min(distances)))
    print("最短路径：{0}".format(paths[0]))
    print('该问题已找到的最优解：15780')
    print('误差：%.2f%%' % (100 * (min(distances) - 15780) / 15780))


if __name__ == "__main__":
    main()