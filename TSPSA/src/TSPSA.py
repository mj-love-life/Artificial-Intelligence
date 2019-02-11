# _*_ coding: utf-8 _*_

import numpy
import math
import tsplib95
import random
import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import cProfile
import argparse
# 解决中文乱码问题
myfont = fm.FontProperties(size=14)
matplotlib.rcParams["axes.unicode_minus"] = False


# 存储邻接矩阵
global DisMatrix
# 存储总的长度
global distance

# 领域操作的随机参数
global x_index
global y_index

global temps
global precisions
global dists
global dists_accepted
global index_accepted
global problem
global dimension
global show_process
global path
# 计算一个节点的相邻的两条边的和
# index指的是数组中的位置，array是数组 dimension是数组长度
# 方便在交换的时候的计算新的路径总长度
def neighbor_dis(index, array, dimension):
    dis = DisMatrix[array[index]][array[(index + 1) % dimension]]
    dis = dis + DisMatrix[array[index]][array[(index - 1 + dimension) % dimension]]
    return dis


# 第一种交换方式：两个点进行交换
def method1(array):
    array1 = copy.deepcopy(array)
    array1[x_index], array1[y_index] = array1[y_index], array1[x_index]
    dimension = len(array)
    new_dis = distance + neighbor_dis(x_index, array1, dimension) + neighbor_dis(y_index, array1, dimension) - neighbor_dis(x_index, array, dimension) - neighbor_dis(y_index, array, dimension)
    #print(new_dis, array1)
    return new_dis, array1

# 新的路径为存放在new_path中，减少内存分配次数
def method1_fast(cur_path, new_path):
    global dimension
    new_path[x_index], new_path[y_index] = cur_path[y_index], cur_path[x_index]
    num_min, num_max = x_index, y_index
    # assure y_index > x_index
    if y_index < x_index:
        num_min, num_max = y_index, x_index
    # assert y_index > x_index(function swap_fast ensure this)
    for i in range(num_max - num_min - 1):
        new_path[num_min + 1 + i] = cur_path[num_min + 1 + i]
    new_dis = distance + neighbor_dis(x_index, new_path, dimension) + neighbor_dis(y_index, new_path, dimension) - neighbor_dis(x_index, cur_path, dimension) - neighbor_dis(y_index, cur_path, dimension)
    return new_dis

# 第二种交换方式，两个点之间的点进行逆序
def method2(array):
    array2 = copy.deepcopy(array)
    num_min = min(x_index, y_index)
    num_max = max(x_index, y_index)
    for i in range(num_max - num_min + 1):
        array2[num_min + i] = array[num_max - i]
    dimension = len(array)
    new_dis = distance + neighbor_dis(x_index, array2, dimension) + neighbor_dis(y_index, array2, dimension) - neighbor_dis(x_index, array, dimension) - neighbor_dis(y_index, array, dimension)
    return new_dis, array2

def method2_fast(cur_path, new_path):
    global dimension
    num_min, num_max = x_index, y_index
    # assure y_index > x_index
    if y_index < x_index:
        num_min, num_max = y_index, x_index
    # assert y_index > x_index(function swap_fast ensure this)
    for i in range(num_max - num_min + 1):
        new_path[num_min + i] = cur_path[num_max - i]
    new_dis = distance + neighbor_dis(x_index, new_path, dimension) + neighbor_dis(y_index, new_path, dimension) - neighbor_dis(x_index, cur_path, dimension) - neighbor_dis(y_index, cur_path, dimension)
    return new_dis

# 第三种交换方式，一个点的前移
def method3(array):
    array3 = copy.deepcopy(array)
    num_min = min(x_index, y_index)
    num_max = max(x_index, y_index)
    temp = array[num_max]
    for i in range(num_max - num_min):
        array3[num_max - i] = array[num_max - i - 1]
    array3[num_min] = temp
    dimension = len(array)
    new_dis = distance - neighbor_dis(num_max, array, dimension) - DisMatrix[array[num_min]][array[(num_min - 1 +dimension) % dimension]] + neighbor_dis(num_min, array3, dimension) + DisMatrix[array3[num_max]][array3[(num_max + 1) % dimension]]
    return new_dis, array3

def method3_fast(cur_path, new_path):
    global dimension
    global DisMatrix
    num_min, num_max = x_index, y_index
    # assure y_index > x_index
    if y_index < x_index:
        num_min, num_max = y_index, x_index
    # assert y_index > x_index(function swap_fast ensure this)
    temp = cur_path[num_max]
    for i in range(num_max - num_min):
        new_path[num_max - i] = cur_path[num_max - i - 1]
    new_path[num_min] = temp
    new_dis = distance - neighbor_dis(num_max, cur_path, dimension) - DisMatrix[cur_path[num_min]][cur_path[(num_min - 1 + dimension) % dimension]] + neighbor_dis(num_min, new_path, dimension) + DisMatrix[new_path[num_max]][new_path[(num_max + 1) % dimension]]
    return new_dis

# 总的交换处理函数，三种交换方式取最优（局部贪心）
def swap(array, dimension):
    global x_index
    global y_index
    x_index = random.randint(1, dimension - 1)
    y_index = random.randint(1, dimension - 1)
    while x_index == y_index:
        y_index = random.randint(1, dimension - 1)
    result1 = method1(array)
    result2 = method2(array)
    result3 = method3(array)
    dis = result1[0]
    # disabled deep copy
    re_array = result1[1]
    if result1[0] > result2[0]:
        dis = result2[0]
        # disabled deep copy
        re_array = result2[1]
    if dis > result3[0]:
        dis = result3[0]
        # disabled deep copy
        re_array = result3[1]
    return dis, re_array

def swap_fast(cur_path, dimension):
    global x_index
    global y_index
    x_index = random.randint(1, dimension - 1)
    y_index = random.randint(1, dimension - 1)
    while x_index == y_index:
        y_index = random.randint(1, dimension - 1)
    new_path = copy.deepcopy(cur_path)
    result1 = method1_fast(cur_path, new_path)
    result2 = method2_fast(cur_path, new_path)
    result3 = method3_fast(cur_path, new_path)
    bestDis = min(result1, result2, result3)
    if result1 == bestDis:
        method1_fast(cur_path, new_path)
    elif result2 == bestDis:
        method2_fast(cur_path, new_path)
    else: 
        method3_fast(cur_path, new_path) 
    return bestDis, new_path

# 计算两点之间的距离函数
def cal_distance(problem, x, y):
    #获取地理位置
    x1, x2 = problem.get_display(x + 1)
    y1, y2 = problem.get_display(y + 1)
    #计算距离
    return math.sqrt((x1-y1)**2 + (x2 - y2)**2)


# 生成邻接矩阵
def generate_matrix(problem, dimension):
    global DisMatrix
    DisMatrix = numpy.zeros([dimension, dimension])
    for i in range(dimension):
        DisMatrix[i][i] = float("inf")
        for j in range(i):
            DisMatrix[i][j] = cal_distance(problem, i, j)
            DisMatrix[j][i] = DisMatrix[i][j]


# 模拟退火算法核心（注释掉if条件中的or部分就是贪心算法）
def tsp_sa(initial_temp, min_temp, rate, round_times):
    global distance
    global temps
    global precisions
    global dists
    global dists_accepted
    global index_accepted
    global path
    temps = []
    precisions = []
    dists = []
    dists_accepted = []
    index_accepted = []
    # 降温次数
    epoch = 0
    # 记录当前找到的最优解
    bestArray = []
    bestDistance = float("inf")
    # disable deep copy
    curPath = path

    while initial_temp > min_temp:
        temps.append(initial_temp)
        for i in range(round_times):
            new_result = swap_fast(curPath, dimension)
            dists.append(new_result[0])
            diff = abs(distance - new_result[0])
            # 记录目前找到的最优解
            if new_result[0] < bestDistance:
                bestDistance = new_result[0]
                # disable deep copy
                bestArray = new_result[1]
            # 若符号条件则接受新解
            if new_result[0] < distance or random.random() < math.exp(-1*(diff/initial_temp)):
                distance = new_result[0]
                # disable deep copy
                curPath = new_result[1]
                dists_accepted.append(distance)
                index_accepted.append(round_times * epoch + i)
        initial_temp = initial_temp * rate
        epoch += 1
        precisions.append(100 * (bestDistance - 15780) / 15780)
        if show_process:
            generate_picture_dyn(copy.deepcopy(curPath), problem, epoch, initial_temp, distance, 100 * (distance - 15780) / 15780, 'sa', initial_temp * rate <= min_temp)
        #print('当前降温次数，温度，路径长度，误差率：NO.%4d %.2f*C %.2f %.2f%%' % (epoch, initial_temp, distance, 100 * (distance - 15780) / 15780))
    return bestArray, bestDistance, epoch


# 局部搜索算法（爬山算法）
def local_search(max_search_times, round_times):
    global distance
    global temps
    global dists
    global dists_accepted
    global index_accepted
    global path
    temps = []
    dists = []
    dists_accepted = []
    index_accepted = []
    # 降温次数
    epoch = 0
    # disable deep copy
    curPath = path
    for epoch in range(max_search_times):
        #temps.append(initial_temp)
        # 记录当前邻域找到的最优解
        bestArray = []
        bestDistance = float("inf")
        bestIndex = 0
        for i in range(round_times):
            new_result = swap(curPath, dimension)
            dists.append(new_result[0])
            #diff = abs(distance - new_result[0])
            # 记录目前找到的最优解
            if new_result[0] < bestDistance:
                bestDistance = new_result[0]
                # disable deep copy
                bestArray = new_result[1]
                bestIndex = i
        # 若邻域中的最优解好于当前解则更新当前解
        if bestDistance < distance:
            distance = bestDistance
            # disable deep copy
            curPath = bestArray
            dists_accepted.append(distance)
            index_accepted.append(round_times * epoch + bestIndex)
        if show_process:
            generate_picture_dyn(copy.deepcopy(curPath), problem, epoch, round_times, distance, 100 * (distance - 15780) / 15780, 'ls', epoch == max_search_times - 1)
        #print('当前邻域搜索次数，邻域规模，路径长度，误差率：%4d %.2f %.2f %.2f%%' % (epoch, round_times, distance, 100 * (distance - 15780) / 15780))
    return curPath, distance, max_search_times

# 画出算法迭代过程
def generate_picture(array, problem, round_times, alg_name):
    global temps
    global precisions
    global dists
    temps_x = [i * round_times for i in range(len(temps))]
    dists_x = [i for i in range(len(dists))]
    if alg_name == 'sa':
        plt.figure()
        plt.title(alg_name)
        plt.plot(temps_x, temps, '-*', color='blue')
        plt.gca().set_xlabel('iteration index')
        plt.gca().set_ylabel('temperature')
        ax2 = plt.gca().twinx()
        ax2.plot(temps_x, precisions, '--', color='red')
        ax2.set_ylabel('precisions')

    plt.figure()
    for x in temps_x:
        plt.gca().axvline(x, ls='--', color='b')
    plt.title(alg_name)
    plt.plot(dists_x, dists, '-*', color='green', label='current path')
    plt.plot(index_accepted, dists_accepted, '-*', color='yellow', label='accepted path')
    plt.xlabel('iteration index')
    plt.ylabel('path length')
    plt.show()


# 动态画图
def generate_picture_dyn(array, problem, epoch, round_times, distance, precision, alg_name, isDone): 
    global dists_accepted
    global index_accepted
    position_x = numpy.zeros([len(array) + 1])
    position_y = numpy.zeros([len(array) + 1])
    for i in range(len(array)):
        position_x[i], position_y[i] = problem.get_display(array[i] + 1)
    position_x[len(array)], position_y[len(array)] = problem.get_display(1)
    # 清除原有图像
    plt.cla()
    if alg_name == 'sa':
        title = 'No.' + str(epoch) + '   temperature:' + str(round_times) + '\n distance:' + str(distance) + '    precision:' + str(precision) + '%'
    elif alg_name == 'ls':
        title = 'No.' + str(epoch) + '   ' + str(round_times) + ' times/epoch\n distance:' + str(distance) + '    precision:' + str(precision) + '%'
    if isDone:
        title = title + '\n Done ! ! !'
    plt.title(title)
    plt.plot(position_x, position_y, 'b.-')
    plt.pause(0.1)
    #plt.show()
    

def init():
    global distance
    global problem
    global dimension
    global path
    global show_process
    distance = 0
    problem = tsplib95.load_problem("../tc/d198.tsp", special=cal_distance)
    dimension = problem.dimension
    generate_matrix(problem, dimension)
    path = [i for i in range(dimension)]
    for i in range(len(path) - 1):
        distance = distance + DisMatrix[path[i]][path[i+1]]
    distance = distance + DisMatrix[path[len(path) - 1]][0]
    print('初始路径长度：', distance)
    # 打开交互模式，非阻塞画图
    plt.figure(figsize=(8, 6), dpi=80)
    plt.ion()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'A program for soluting the TSP-198 problem with SA or mounting climbing algorithm')
    parser.add_argument('--alg', required = False, help = 'choose an algorithm: mc or sa, default by mc', default = 'mc')
    parser.add_argument('--inter', required = False, help = 'parameter for mc or sa: internal loop counts, default by 100', default = 100)
    parser.add_argument('--exter', required = False, help = 'parameter for mc: external loop counts, default by 400', default = 400)
    parser.add_argument('--it', required = False, help = 'parameter for sa: initial temperature', default = 100)
    parser.add_argument('--mt', required = False, help = 'parameter for sa: min temperature', default = 0.01)
    parser.add_argument('--rate', required = False, help = 'parameter for sa: temperature decreasing rate', default = 0.98)
    args = parser.parse_args()
    if args.alg == 'sa' or args.alg == 'mc':
        alg_name = args.alg
    else:
        alg_name = 'mc'
    round_times = int(args.inter)
    exter = int(args.exter)
    initial_temp = float(args.it)
    min_temp = float(args.mt)
    rate = float(args.rate)
    # show_process = False
    show_process = True
    print('args: ', 'alg=', alg_name, '  inter=', round_times, '  exter=', exter, '  initial_temp=', initial_temp, '  min_temp=', min_temp, '  rate=', rate)
    init()
    #cProfile.run('tsp_sa(100, 0.1, 0.95, 1000)')
    # 
    if alg_name == 'mc':
        array, distance, epoch = local_search(exter, round_times)
    elif alg_name == 'sa':
        array, distance, epoch = tsp_sa(initial_temp, min_temp, rate, round_times)
    print('最佳路径：', array)
    print('路径长度：', distance)
    print('降温/邻域搜索次数：', epoch)
    print('该问题已找到的最优解：15780')
    print('误差：%.2f%%' % (100 * (distance - 15780) / 15780))
    plt.ioff()
    if show_process:
        plt.show()
    generate_picture(array, problem, round_times, alg_name)