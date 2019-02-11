import math
import numpy as np
import scipy.io as scio


# 读入训练样本数据
fileName = '../data/mnist_train.mat' # raw_input()读取指定文件
trainSampleData = scio.loadmat(fileName)
trainSamples = trainSampleData["mnist_train"]
trainSamples /= 256.0 # 特征向量归一化

# 读入训练样本的期望输出数据
fileName = '../data/mnist_train_labels.mat' # raw_input()读取指定文件
trainLabelsData = scio.loadmat(fileName)
trainLabels = trainLabelsData["mnist_train_labels"]


# 配置神经网络参数
samplesNum = len(trainSamples) # 样本容量
print("Train sample capacity: {0}".format(samplesNum))
inputNum = len(trainSamples[0]) # 输入层神经元数
outputNum = 10 # 输出神经元数，分别代表数字0-9
hiddenNum = 45 # 隐层神经元数(经验公式)

# 初始化输入层与隐层之间的连接权值矩阵为一个(inputNum*hiddenNum)维的随机矩阵
w = 0.2 * np.random.random((inputNum, hiddenNum)) - 0.1
# 初始化隐层与输出层之间的连接权值矩阵为一个(hiddenNum*outputNum)维的随机矩阵
v = 0.2 * np.random.random((hiddenNum, outputNum))- 0.1

hiddenOffset = np.zeros(hiddenNum) # 隐层偏置向量
outputOffset = np.zeros(outputNum) # 输出层偏置向量
inputLearnRate = 0.2 # 输入层权值学习率
hiddenLearnRate = 0.2 # 隐层学权值习率


# 必要函数定义
def get_act(x):
    actArr = []
    for i in x:
        actArr.append(1/(1+math.exp(-i)))
    actArr = np.array(actArr)
    return actArr


# 训练
print("Start training...")
for count in range(0, samplesNum):
    expectLabels = np.zeros(outputNum)
    expectLabels[trainLabels[count]] = 1 # 期望的输出值
    # 正向传播（np.dot()为矩阵乘积）
    hiddenValue = np.dot(trainSamples[count], w) + hiddenOffset # 隐层值
    hiddenAct = get_act(hiddenValue) # 隐层输出
    outputValue = np.dot(hiddenAct, v) + outputOffset # 输出层值
    outputAct = get_act(outputValue) # 输出层输出

    # 误差反传
    e = expectLabels - outputAct # 计算输出误差
    # 计算各层误差信号
    outputDelta = e * outputAct * (1-outputAct)
    hiddenDelta = hiddenAct * (1-hiddenAct) * np.dot(v, outputDelta)    
    # 调整各层权值
    for i in range(0, outputNum):
        v[:,i] += hiddenLearnRate * outputDelta[i] * hiddenAct
    for i in range(0, hiddenNum):
        w[:,i] += inputLearnRate * hiddenDelta[i] * trainSamples[count]
    #更新各层偏置
    outputOffset += hiddenLearnRate * outputDelta
    hiddenOffset += inputLearnRate * hiddenDelta
print("Training complete.")

# 测试网络
# 读入测试样本数据
fileName = '../data/mnist_test.mat' # raw_input()读取指定文件
testSamplesData = scio.loadmat(fileName)
testSamples = testSamplesData["mnist_test"]
testSamples /= 256.0
print("Test sample capacity: {0}".format(len(testSamples)))

# 读入测试样本的期望输出的数据
fileName = '../data/mnist_test_labels.mat' # raw_input()读取指定文件
testLabelsData = scio.loadmat(fileName)
testLabels = testLabelsData["mnist_test_labels"]
rightCount = np.zeros(10)
expectCount = np.zeros(10)

# 统计测试样本期望输出中各个数字的数目
for i in testLabels:
    expectCount[i] += 1

for count in range(len(testSamples)):
    hiddenValue = np.dot(testSamples[count], w) + hiddenOffset
    hiddenAct = get_act(hiddenValue)
    outputValue = np.dot(hiddenAct, v) + outputOffset
    outputAct = get_act(outputValue)
    if np.argmax(outputAct) == testLabels[count]:
        rightCount[testLabels[count]] += 1
rightSum = rightCount.sum()
print("The number of right result: {0}".format(rightSum))
rate = rightSum / len(testSamples)
print("The recognition rate: {0}%".format(rate * 100))
print("The number of each digit in expect output: {0}".format(expectCount))
print("The number of right result of each digit: {0}".format(rightCount))
rateArr = rightCount / expectCount
print("The recognition rate of each digit: {0}".format(rateArr))