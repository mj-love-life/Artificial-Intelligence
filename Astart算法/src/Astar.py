from numpy import *
import copy
global N
maxsize = 1000


# 计算逆序和
def calculat_inverse(arr):
    inverse_sum = 0
    n = len(arr)
    m = n ** 2 - 1
    for i in range(n ** 2):
        temp = [k + 1 for k in range(i, m - 1)]
        for j in temp:
            if arr[int(j / n), j % n] == 0:
                continue
            elif arr[int(i / n), i % n] > arr[int(j / n), j % n]:
                inverse_sum = inverse_sum + 1
    return inverse_sum


# 判断是否能够到达目的状态
# 用于判断是否有解
def judge(start, target_state):
    return (calculat_inverse(start) % 2) == (calculat_inverse(target_state) % 2)


# 根据所给定的num产生随机初始状态
def start_generate(target, num):
    # num = min(500, num)
    temp = copy.deepcopy(target)
    for i in range(num):
        dir = random.randint(1, 4)
        temp = move(temp, dir)[0]
    return temp


# 返回参数列表
# 下一个状态数组  是否成功得移动
def move(matrix_, dir):
    # x表示row
    # y表示col
    x, y = 0, 0
    next_state = copy.deepcopy(matrix_)
    # dir 为 1-4 分别代表着 上 下 左 右
    for i in range(N):
        for j in range(N):
            if matrix_[i, j] == 0:
                x, y = i, j
                break
    if (x == 0 and dir == 1) or (x == N - 1 and dir == 2) or (y == 0 and dir == 3) or (y == N - 1 and dir == 4):
        return [next_state, False]
    if dir == 1:
        next_state[x, y], next_state[x - 1, y] = next_state[x - 1, y], next_state[x, y]
    elif dir == 2:
        next_state[x, y], next_state[x + 1, y] = next_state[x + 1, y], next_state[x, y]
    elif dir == 3:
        next_state[x, y], next_state[x, y - 1] = next_state[x, y - 1], next_state[x, y]
    elif dir == 4:
        next_state[x, y], next_state[x, y + 1] = next_state[x, y + 1], next_state[x, y]
    else:
        return [next_state, False]
    return [next_state, True]


# 九数码
# 评估函数2
# 放错元素与正确位置的曼哈顿距离
# 返回一个数字
def evaluate2(current, target_state):
    distances = 0
    # 如果是八数码为题则改为 arange(1, 9, 1, dtype=int)
    for i in arange(0, 9, 1, dtype=int):
        index_1 = argwhere(current == i)
        index_2 = argwhere(target_state == i)
        distances = distances + (abs(index_1[0][0] - index_2[0][0]) + abs(index_1[0][1] - index_2[0][1]))
    return distances


# 九数码
# 评估函数1
# 放错位置的元素的个数
# 返回一个数字
def evaluate(current, target_state):
    temp = current - target_state
    count = 0
    '''
    如果是八数码问题则改为：
    result = sum(temp != 0)
    if result > len(current)**2 - 1:
        result = len(current)**2 - 1
    return result
    '''
    return sum(temp != 0)

# 八数码
# 评估函数3 八数码问题
# 放错位置的元素的个数
# 返回一个数字
def evaluate3(current, target_state):
    temp = current - target_state
    result = sum(temp != 0)
    if result > len(current)**2 - 1:
        result = len(current)**2 - 1
    return result


# 八数码
# 评估函数4
# 放错元素与正确位置的哈密顿距离
# 返回一个数字
def evaluate4(current, target_state):
    distances = 0
    for i in arange(1, 9, 1, dtype=int):
        index_1 = argwhere(current == i)
        index_2 = argwhere(target_state == i)
        distances = distances + (abs(index_1[0][0] - index_2[0][0]) + abs(index_1[0][1] - index_2[0][1]))
    return distances


# 判断是否在状态表中
def checkadd(states, b, n):
    for i in range(n):
        if str(states[i]) == str(b):
            return i
    return -1


# 算法核心
def a_start(states, current, target_state, tag):
    # 根据tag选择对应的评估函数
    if tag == 1:
        method = evaluate
    elif tag == 2:
        method = evaluate2
    elif tag == 3:
        method = evaluate3
    elif tag == 4:
        method = evaluate4
    path = zeros([maxsize], dtype=uint)
    # 记录是否访问过
    visited = array([False for i in range(maxsize)])
    # 估计函数值
    evaluate_value = array([0 for i in range(maxsize)])
    # 路径的长度
    depth = array([0 for i in range(maxsize)])
    # 记录状态的变换
    curpos = copy.deepcopy(current)
    id, curid = 0, 0
    evaluate_value[id] = method(curpos, target_state)
    states[id] = current
    id = id + 1
    # 访问的节点的个数
    count = 0
    # 判断状态是否相同
    while not str(curpos) == str(target_state):
        for i in range(1, 5):
            tmp = move(curpos, i)
            # 判断是否移动成功
            if tmp[1]:
                state = checkadd(states, tmp[0], id)
                print("当前层数", depth[curid])
                print("前一代的评估值", method(curpos, target_state))
                print("当前的评估值", method(tmp[0], target_state))
                # 不在表中，存入表中
                if state == -1:
                    count = count + 1
                    path[id] = curid
                    depth[id] = depth[curid] + 1
                    evaluate_value[id] = method(tmp[0], target_state) + depth[id]
                    states[id] = tmp[0]
                    id = id + 1
                # 在表中，进行更新
                else:
                    l = depth[curid] + 1
                    fit = method(tmp[0], target_state) + l
                    if fit < evaluate_value[state]:
                        path[state] = curid
                        depth[state] = l
                        evaluate_value[state] = fit
        visited[curid] = True
        min_eval = -1
        # 取出最小的节点
        open_count = 0
        for i in range(id):
            if visited[i] == False and (min_eval == -1 or evaluate_value[i] < evaluate_value[min_eval]):
                open_count += 1
                min_eval = i
        curid = min_eval
        curpos = states[curid]
        print("当前open表的数目是：", open_count)
        print("当前总的结点数目是：", count)
        print("当前最小的节点评估值是：", evaluate_value[curid], "当前最小的节点是")
        print(states[curid])
        print("+"*100)
        if id == maxsize:
            return -1
    # curid表示最后的状态的id值，count表示总的结点的数目, path表示变换的路径，evaluate_value表示每一个结点的评估值
    return curid, count, path, evaluate_value


# 打印结果
def display(arr, num):
    print("第" + str(num) + "次移动的结果")
    print(arr)


def process(states, current, target_state, tag):
    print("_" * 100)
    print("原状态")
    print(current)
    print("方法: ", tag)
    id, count, path, evaluate_value = a_start(states, current, target_state, tag)
    shortest = []
    # print("总共访问的节点的个数" + str(count))
    while id != 0:
        shortest.append(id)
        id = path[id]
    shortest.reverse()
    for i in range(len(shortest)):
        print("_" * 100)
        print(evaluate_value[shortest[i]])
        display(states[shortest[i]], i + 1)



# 主函数
def main():
    global N
    func = 0;
    if func == 1:
        size = int(input("please input the size of the matrixs(odd): "))
        arr1 = zeros([size, size], dtype=uint)
        arr2 = zeros([size, size], dtype=uint)
        print("please input the matrix1's num with enter\n")
        for i in range(size*size):
            arr1[int(i/size)][i%size] = input()
        print("please input the matrix2's num with enter\n")
        for i in range(size * size):
            arr2[int(i/size)][i % size] = input()
        if str(sort(arr1.reshape(1, size*size))) != str(sort(arr2.reshape(1, size*size))) :
            print("fail")
            return
        if judge(arr1, arr2):
            print("successful")
        else:
            print("fail")
        return
    N = int(input("size is(odd number): "))
    num = abs(int(input("how many steps would you want to break: ")))
    target_state = zeros([N, N], dtype=uint)
    states = zeros([maxsize, N, N], dtype=uint)
    for i in range(N):
        for j in range(N):
            target_state[i, j] = (i * N + j + 1) % N ** 2
    current = start_generate(target_state, num)
    process(states, current, target_state, tag=1)
    process(states, current, target_state, tag=2)
    process(states, current, target_state, tag=3)
    process(states, current, target_state, tag=4)

# 程序入口
if __name__ == "__main__":
    main()