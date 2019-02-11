# 使用爬山算法和模拟退火算法求解TSP问题

## 环境要求

- python3.5 / python3.7



## 代码和演示

```sh
$ cd ./src
# 查看使用方法
$ python ./TSPSA.py --help
# usage: TSPSA.py [-h] [--alg ALG] [--inter INTER] [--exter EXTER] [--it IT]
                [--mt MT] [--rate RATE]

# A program for soluting the TSP-198 problem with SA or mounting climbing
# algorithm

# optional arguments:
#  -h, --help     show this help message and exit
#  --alg ALG      choose an algorithm: mc or sa, default by mc
#  --inter INTER  parameter for mc or sa: internal loop counts, default by 100
#  --exter EXTER  parameter for mc: external loop counts, default by 400
#  --it IT        parameter for sa: initial temperature
#  --mt MT        parameter for sa: min temperature
#  --rate RATE    parameter for sa: temperature decreasing rate
# 使用默认参数直接运行
$ python ./TSPSA.py
```

