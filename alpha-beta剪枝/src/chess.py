import sys, time
from PyQt5 import QtGui, QtWidgets
from numpy import *
import random

# 棋局
board = []
red_alive = []
black_alive = []

# 各个棋子的位置
positions = {}

# 棋子名称
red = ['bing_0', 'bing_1', 'bing_2', 'bing_3', 'bing_4', 'red_pao_0', 'red_pao_1', 'red_che_0',
     'red_ma_0', 'red_xiang_0', 'red_shi_0', 'shuai', 'red_shi_1', 'red_xiang_1', 'red_ma_1',
     'red_che_1']
black = ['zu_0', 'zu_1', 'zu_2', 'zu_3', 'zu_4', 'black_pao_0', 'black_pao_1', 'black_che_0', 'black_ma_0',
        'black_xiang_0', 'black_shi_0', 'jiang', 'black_shi_1', 'black_xiang_1', 'black_ma_1', 'black_che_1']

# 棋力值
importances = {
    'bing_0': -100,
    'bing_1': -100,
    'bing_2': -100,
    'bing_3': -100,
    'bing_4': -100,
    'red_pao_0': -450,
    'red_pao_1': -450,
    'red_che_0': -900,
    'red_che_1': -900,
    'red_ma_0': -400,
    'red_ma_1': -400,
    'red_xiang_0': -200,
    'red_xiang_1': -200,
    'red_shi_0': -200,
    'red_shi_1': -200,
    'shuai': -100000,
    'zu_0': 100,
    'zu_1': 100,
    'zu_2': 100,
    'zu_3': 100,
    'zu_4': 100,
    'black_pao_0': 450,
    'black_pao_1': 450,
    'black_che_0': 900,
    'black_che_1': 900,
    'black_ma_0': 400,
    'black_ma_1': 400,
    'black_xiang_0': 200,
    'black_xiang_1': 200,
    'black_shi_0': 200,
    'black_shi_1': 200,
    'jiang': 100000,
    '0': 0
}

# 走法
steps = {
    'ma': [(-1, -2), (-2, -1), (-1, 2), (2, -1), (1, -2), (-2, 1), (1, 2), (2, 1)],
    'shi': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    'xiang': [(2, 2), (2, -2), (-2, 2), (-2, -2)],
    'bing': [(-1, 0), (0, 1), (0, -1)],
    'zu': [(1, 0), (0, 1), (0, -1)],
    'jiang': [(0, 1), (0, -1), (1, 0), (-1, 0)],
    'shuai': [(0, 1), (0, -1), (1, 0), (-1, 0)]
}

class Chess(QtWidgets.QMainWindow):
    def __init__(self):
        print('initing...')
        # 获取屏幕大小，设置合适的棋局和棋子大小
        self.desktop = QtWidgets.QApplication.desktop()
        screenRect = self.desktop.screenGeometry()
        self.screenHeight = screenRect.height()
        self.screenWidth = screenRect.width()
        self.boardCellSize = int(int(self.screenHeight * 0.8) / 11)
        self.boardCellSize -= (self.boardCellSize % 8)
        self.pieceSize = int(self.boardCellSize * 0.75)
        self.offset = int((self.boardCellSize * 3) / 8)
        print('board cell size:', self.boardCellSize)
        print('pieceSize:', self.pieceSize)

        super().__init__()
        self.initUI()
        self.start = True
        self.human_move_done = True
        self.turn_color = 'F'
        self.nodeCounts = 0
        self.search_depth = 2

    def initUI(self):
        # 加载背景
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('images/board.png').scaled(self.boardCellSize * 10, self.boardCellSize * 11)))
        self.setPalette(palette)
        # 加载图片
        self.load_in_pngs()
        # 加载选择框
        gameAction = QtWidgets.QAction('Start a new game', self)
        gameAction.setShortcut('Ctrl+N')
        gameAction.setStatusTip('Start a new game')
        gameAction.triggered.connect(self.start)
        # 加载下边框
        self.statusBar()
        self.statusBar().showMessage('Ready')
        # 加载菜单
        menubar = self.menuBar()
        gameMenu = menubar.addMenu('&Game')
        gameMenu.addAction(gameAction)
        # 加载棋子
        self.init_board()
        # 设置界面大小
        self.resize(self.boardCellSize * 10, self.boardCellSize * 11)
        self.center()
        self.setWindowTitle('Chinese Chess AI')
        self.setMinimumSize(self.boardCellSize * 10, self.boardCellSize * 11)
        self.setMaximumSize(self.boardCellSize * 10, self.boardCellSize * 11)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_in_pngs(self):
        # 加载图片
        png = QtGui.QPixmap('images/zu.png').scaled(self.pieceSize, self.pieceSize)
        self.zu_0 = QtWidgets.QLabel(self)
        self.zu_0.setPixmap(png)
        self.zu_0.resize(self.pieceSize, self.pieceSize)
        self.zu_1 = QtWidgets.QLabel(self)
        self.zu_1.setPixmap(png)
        self.zu_1.resize(self.pieceSize, self.pieceSize)
        self.zu_2 = QtWidgets.QLabel(self)
        self.zu_2.setPixmap(png)
        self.zu_2.resize(self.pieceSize, self.pieceSize)
        self.zu_3 = QtWidgets.QLabel(self)
        self.zu_3.setPixmap(png)
        self.zu_3.resize(self.pieceSize, self.pieceSize)
        self.zu_4 = QtWidgets.QLabel(self)
        self.zu_4.setPixmap(png)
        self.zu_4.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/heipao.png').scaled(self.pieceSize, self.pieceSize)
        self.black_pao_0 = QtWidgets.QLabel(self)
        self.black_pao_0.setPixmap(png)
        self.black_pao_0.resize(self.pieceSize, self.pieceSize)
        self.black_pao_1 = QtWidgets.QLabel(self)
        self.black_pao_1.setPixmap(png)
        self.black_pao_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/heiche.png').scaled(self.pieceSize, self.pieceSize)
        self.black_che_0 = QtWidgets.QLabel(self)
        self.black_che_0.setPixmap(png)
        self.black_che_0.resize(self.pieceSize, self.pieceSize)
        self.black_che_1 = QtWidgets.QLabel(self)
        self.black_che_1.setPixmap(png)
        self.black_che_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/heima.png').scaled(self.pieceSize, self.pieceSize)
        self.black_ma_0 = QtWidgets.QLabel(self)
        self.black_ma_0.setPixmap(png)
        self.black_ma_0.resize(self.pieceSize, self.pieceSize)
        self.black_ma_1 = QtWidgets.QLabel(self)
        self.black_ma_1.setPixmap(png)
        self.black_ma_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/heixiang.png').scaled(self.pieceSize, self.pieceSize)
        self.black_xiang_0 = QtWidgets.QLabel(self)
        self.black_xiang_0.setPixmap(png)
        self.black_xiang_0.resize(self.pieceSize, self.pieceSize)
        self.black_xiang_1 = QtWidgets.QLabel(self)
        self.black_xiang_1.setPixmap(png)
        self.black_xiang_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/heishi.png').scaled(self.pieceSize, self.pieceSize)
        self.black_shi_0 = QtWidgets.QLabel(self)
        self.black_shi_0.setPixmap(png)
        self.black_shi_0.resize(self.pieceSize, self.pieceSize)
        self.black_shi_1 = QtWidgets.QLabel(self)
        self.black_shi_1.setPixmap(png)
        self.black_shi_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/jiang.png').scaled(self.pieceSize, self.pieceSize)
        self.jiang = QtWidgets.QLabel(self)
        self.jiang.setPixmap(png)
        self.jiang.resize(self.pieceSize, self.pieceSize)
        ##red
        png = QtGui.QPixmap('images/bing.png').scaled(self.pieceSize, self.pieceSize)
        self.bing_0 = QtWidgets.QLabel(self)
        self.bing_0.setPixmap(png)
        self.bing_0.resize(self.pieceSize, self.pieceSize)
        self.bing_1 = QtWidgets.QLabel(self)
        self.bing_1.setPixmap(png)
        self.bing_1.resize(self.pieceSize, self.pieceSize)
        self.bing_2 = QtWidgets.QLabel(self)
        self.bing_2.setPixmap(png)
        self.bing_2.resize(self.pieceSize, self.pieceSize)
        self.bing_3 = QtWidgets.QLabel(self)
        self.bing_3.setPixmap(png)
        self.bing_3.resize(self.pieceSize, self.pieceSize)
        self.bing_4 = QtWidgets.QLabel(self)
        self.bing_4.setPixmap(png)
        self.bing_4.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/hongpao.png').scaled(self.pieceSize, self.pieceSize)
        self.red_pao_0 = QtWidgets.QLabel(self)
        self.red_pao_0.setPixmap(png)
        self.red_pao_0.resize(self.pieceSize, self.pieceSize)
        self.red_pao_1 = QtWidgets.QLabel(self)
        self.red_pao_1.setPixmap(png)
        self.red_pao_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/hongche.png').scaled(self.pieceSize, self.pieceSize)
        self.red_che_0 = QtWidgets.QLabel(self)
        self.red_che_0.setPixmap(png)
        self.red_che_0.resize(self.pieceSize, self.pieceSize)
        self.red_che_1 = QtWidgets.QLabel(self)
        self.red_che_1.setPixmap(png)
        self.red_che_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/hongma.png').scaled(self.pieceSize, self.pieceSize)
        self.red_ma_0 = QtWidgets.QLabel(self)
        self.red_ma_0.setPixmap(png)
        self.red_ma_0.resize(self.pieceSize, self.pieceSize)
        self.red_ma_1 = QtWidgets.QLabel(self)
        self.red_ma_1.setPixmap(png)
        self.red_ma_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/hongxiang.png').scaled(self.pieceSize, self.pieceSize)
        self.red_xiang_0 = QtWidgets.QLabel(self)
        self.red_xiang_0.setPixmap(png)
        self.red_xiang_0.resize(self.pieceSize, self.pieceSize)
        self.red_xiang_1 = QtWidgets.QLabel(self)
        self.red_xiang_1.setPixmap(png)
        self.red_xiang_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/hongshi.png').scaled(self.pieceSize, self.pieceSize)
        self.red_shi_0 = QtWidgets.QLabel(self)
        self.red_shi_0.setPixmap(png)
        self.red_shi_0.resize(self.pieceSize, self.pieceSize)
        self.red_shi_1 = QtWidgets.QLabel(self)
        self.red_shi_1.setPixmap(png)
        self.red_shi_1.resize(self.pieceSize, self.pieceSize)
        png = QtGui.QPixmap('images/shuai.png').scaled(self.pieceSize, self.pieceSize)
        self.shuai = QtWidgets.QLabel(self)
        self.shuai.setPixmap(png)
        self.shuai.resize(self.pieceSize, self.pieceSize)

    def init_board(self):
        # 放置棋子
        global board
        global red_alive
        global black_alive
        global positions
        ##black
        self.zu_0.move(1 * self.boardCellSize - self.offset, 4 * self.boardCellSize - self.offset)
        self.zu_1.move(3 * self.boardCellSize - self.offset, 4 * self.boardCellSize - self.offset)
        self.zu_2.move(5 * self.boardCellSize - self.offset, 4 * self.boardCellSize - self.offset)
        self.zu_3.move(7 * self.boardCellSize - self.offset, 4 * self.boardCellSize - self.offset)
        self.zu_4.move(9 * self.boardCellSize - self.offset, 4 * self.boardCellSize - self.offset)
        self.black_pao_0.move(2 * self.boardCellSize - self.offset, 3 * self.boardCellSize - self.offset)
        self.black_pao_1.move(8 * self.boardCellSize - self.offset, 3 * self.boardCellSize - self.offset)
        self.black_che_0.move(1 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_che_1.move(9 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_ma_0.move(2 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_ma_1.move(8 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_xiang_0.move(3 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_xiang_1.move(7 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_shi_0.move(4 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.black_shi_1.move(6 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        self.jiang.move(5 * self.boardCellSize - self.offset, 1 * self.boardCellSize - self.offset)
        ##red
        self.bing_0.move(1 * self.boardCellSize - self.offset, 7 * self.boardCellSize - self.offset)
        self.bing_1.move(3 * self.boardCellSize - self.offset, 7 * self.boardCellSize - self.offset)
        self.bing_2.move(5 * self.boardCellSize - self.offset, 7 * self.boardCellSize - self.offset)
        self.bing_3.move(7 * self.boardCellSize - self.offset, 7 * self.boardCellSize - self.offset)
        self.bing_4.move(9 * self.boardCellSize - self.offset, 7 * self.boardCellSize - self.offset)
        self.red_pao_0.move(2 * self.boardCellSize - self.offset, 8 * self.boardCellSize - self.offset)
        self.red_pao_1.move(8 * self.boardCellSize - self.offset, 8 * self.boardCellSize - self.offset)
        self.red_che_0.move(1 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_che_1.move(9 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_ma_0.move(2 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_ma_1.move(8 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_xiang_0.move(3 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_xiang_1.move(7 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_shi_0.move(4 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.red_shi_1.move(6 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        self.shuai.move(5 * self.boardCellSize - self.offset, 10 * self.boardCellSize - self.offset)
        # 用于记录选择的棋子的信息
        self.select = ''
        self.select_pos = [0, 0]
        # 初始化board，记录每一个的位置
        board = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                 ['0', 'black_che_0', 'black_ma_0', 'black_xiang_0', 'black_shi_0', 'jiang', 'black_shi_1', 'black_xiang_1', 'black_ma_1',
                  'black_che_1', '0'],
                 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                 ['0', '0', 'black_pao_0', '0', '0', '0', '0', '0', 'black_pao_1', '0', '0'],
                 ['0', 'zu_0', '0', 'zu_1', '0', 'zu_2', '0', 'zu_3', '0', 'zu_4', '0'],
                 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                 ['0', 'bing_0', '0', 'bing_1', '0', 'bing_2', '0', 'bing_3', '0', 'bing_4', '0'],
                 ['0', '0', 'red_pao_0', '0', '0', '0', '0', '0', 'red_pao_1', '0', '0'],
                 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                 ['0', 'red_che_0', 'red_ma_0', 'red_xiang_0', 'red_shi_0', 'shuai', 'red_shi_1', 'red_xiang_1',
                  'red_ma_1', 'red_che_1', '0'],
                 ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'], ]
        # 记录存活的棋子
        red_alive = ['bing_0', 'bing_1', 'bing_2', 'bing_3', 'bing_4', 'red_pao_0', 'red_pao_1', 'red_che_0',
                     'red_ma_0', 'red_xiang_0', 'red_shi_0', 'shuai', 'red_shi_1', 'red_xiang_1', 'red_ma_1',
                     'red_che_1']
        black_alive = ['zu_0', 'zu_1', 'zu_2', 'zu_3', 'zu_4', 'black_pao_0', 'black_pao_1', 'black_che_0', 'black_ma_0',
                       'black_xiang_0', 'black_shi_0', 'jiang', 'black_shi_1', 'black_xiang_1', 'black_ma_1', 'black_che_1']
        # 记录各个棋子的位置，被吃掉的棋子的位置为None
        for x in range(1, 11):
            for y in range(1, 10):
                if board[x][y] != '0':
                    positions[board[x][y]] = (x,y)

    def start(self):
        print('starting...')
        self.init_board()
        self.turn = 'H'  # human
        self.turn_color = 'R'  # red
        self.start = False
        self.vs_AI()

    def vs_AI(self):
        if self.turn == 'H':
            self.human_go()
        elif self.turn == 'A':  # AI
            self.ai_go()

    # 判断游戏是否结束
    def end_check(self):
        global red_alive
        global black_alive
        global positions
        # 如果帅或将不在了
        if 'shuai' not in red_alive or 'jiang' not in black_alive:
            return True
        else:
            x_in, y_in = positions['shuai']
            x_in2, y_in2 = positions['jiang']
            # print(x_in, y_in, x_in2, y_in2)
            if y_in == y_in2:
                max_ = max(x_in2, x_in)
                min_ = min(x_in, x_in2)
                # print(max_, min_)
                for i in range(min_+1, max_):
                    # print(board[i][y_in2])
                    if board[i][y_in2] != '0':
                        return False
                return True
            else:
                return False

    def celebrate(self):
        print('celebrate...')
        reply = QtWidgets.QMessageBox.information(self, " ", self.tr("游戏结束!"))

    def human_go(self):
        print('human_go...')
        self.select = ''
        self.select_pos = [0, 0]
        self.human_move_done = False
        self.statusBar().showMessage("Your turn!")

    def ai_go(self):
        print('ai_go...')
        self.statusBar().showMessage("AI turn!")
        self.sol = [0, 0]
        # 传入极大值与极小值
        self.nodeCounts = 0
        st = time.time()
        value = self.AlphaBeta(self.search_depth, -1000000, 1000000)
        et = time.time()
        print('node counts:', self.nodeCounts)
        print('time elapsed:', et - st, 'seconds')
        print((et - st) / self.nodeCounts * 1000, ' ms per node')
        print('evaluate value:', value)
        self.piece_move(self.sol[0], self.sol[1])
        if self.end_check():
            self.celebrate()
        else:
            self.turn = 'H'
            if self.turn_color == 'R':
                self.turn_color = 'B'
            else:
                self.turn_color = 'R'
            self.vs_AI()

    # AlphaBeta剪枝
    def AlphaBeta(self, depth, alpha, beta):
        global board
        global red_alive
        global black_alive
        moves = []
        des = [0, 0]
        ori = [0, 0]
        # 深度为0 或者胜负已定时返回启发值
        if depth == 0 or self.end_check():
            evaled = self.evaluate(depth % 2 == 0)
            if depth % 2 != 0:
                print('depth:', depth)
                print('eval:', evaled)
                print('end check board:')
                print(board)
            return evaled
        # 产生四层解法
        self.gen_moves(moves, depth)
        if depth % 2 == 0:
            # 对产生的步骤进行遍历
            while moves:
                # 获取里面的一个元素，ori表示的是原来的位置，des表示的是目标位置
                [ori[0], ori[1], des[0], des[1]] = moves[0]
                lastMove = (ori[0], ori[1], des[0], des[1])
                if board[des[0]][des[1]] != '0':
                    lastKill = board[des[0]][des[1]]
                else:
                    lastKill = ''
                del moves[0]
                self.make_a_move(ori[0], ori[1], des[0], des[1])
                # val = self.evaluate(False)
                # 递归生成下一层的解
                # if val >= alpha or abs(val - alpha) <= 5000:
                val = self.AlphaBeta(depth - 1, alpha, beta)
                #if depth == 4:
                    # print('  val:', val)
                    #print('  ', ori[0], ori[1], des[0], des[1])
                    #print('  alpha:', alpha, ' beta:', beta)
                alpha = max(val, alpha)
                # 用于恢复原状态
                self.move_back(lastMove, lastKill)
                # 选择最优的解
                if val == alpha:
                    if depth == self.search_depth:
                        self.select_pos[0] = ori[0]
                        self.select_pos[1] = ori[1]
                        self.select = board[ori[0]][ori[1]]
                        self.sol[0] = des[0]
                        self.sol[1] = des[1]
                # 进行beta剪枝
                if alpha >= beta:
                    break
            return alpha
        else:
            # 对产生的步骤进行遍历
            while moves:
                # 获取里面的一个元素，ori表示的是原来的位置，des表示的是目标位置
                [ori[0], ori[1], des[0], des[1]] = moves[0]
                lastMove = (ori[0], ori[1], des[0], des[1])
                if board[des[0]][des[1]] != '0':
                    lastKill = board[des[0]][des[1]]
                else:
                    lastKill = ''
                del moves[0]
                self.make_a_move(ori[0], ori[1], des[0], des[1])
                # val = self.evaluate(True)
                # 递归生成下一层的解
                # if val <= beta or abs(val - beta) <= 5000:
                val = self.AlphaBeta(depth - 1, alpha, beta)
                #if depth == 1:
                    #print('    val:', val)
                    #print('    ', ori[0], ori[1], des[0], des[1])
                    #print('    alpha:', alpha, ' beta:', beta)
                beta = min(val, beta)
                # 用于恢复原状态
                self.move_back(lastMove, lastKill)
                # 进行alpha剪枝
                if alpha >= beta:
                    break
            return beta

    def evaluate(self, isMaxGo):
        self.nodeCounts += 1
        global board
        global red_alive
        global black_alive
        global positions
        if positions['shuai'] == None:
            return 1000000
        elif positions['jiang'] == None:
            return -1000000
        isFaceToFace = True
        x1, y1 = positions['shuai']
        x2, y2 = positions['jiang']
        if y1 == y2:
            step = int((x2 - x1) / abs(x2 - x1))
            pos_x = x1
            for i in range(abs(x2 - x1) - 1):
                pos_x += step
                if board[pos_x][y1] != '0':
                    isFaceToFace = False
                    break
        else:
            isFaceToFace = False
        if isFaceToFace:
            if isMaxGo:
                print('ko at face to face')
                return 1000000
            else:
                return -1000000
        count = 0
        all_alive = red_alive + black_alive
        for piece in all_alive:
            x, y = positions[piece]
            count += importances[piece] * 2 + self.attack_ability(piece, isMaxGo)
            if importances[piece] < 0:
                count -= (11 - positions[piece][0]) * random.randint(-1, 1)
            else:
                count += positions[piece][0] * random.randint(-1, 1)
            count += random.randint(-10, 10) * positions[piece][1]
            '''
            if isMaxGo and importances[piece] > 0:
                count += self.attack_ability(piece, isMaxGo)
            elif isMaxGo == False and importances[piece] < 0:
                count += self.attack_ability(piece, isMaxGo)
            '''
        if count < -1000000:
            count = -1000000
        elif count > 1000000:
            count = 1000000
        return count

    def attack_ability(self, piece, isMaxGo):
        global positions
        global board
        global importances
        global steps
        if positions[piece] == None:
            return 0
        x, y = positions[piece]
        ability = 0
        factor = 1
        factor2 = 0.1
        factor3 = 0
        # red attack black (human attack ai)
        if board[x][y][:4] == 'bing' or board[x][y][:2] == 'zu':
            for step in steps[board[x][y][:-2]]:
                target_x = x + step[0]
                target_y = y + step[1]
                if importances[board[target_x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][target_y]]
                    else:
                        ability -= factor2 * importances[board[target_x][target_y]]
                    if (isMaxGo and board[target_x][target_y] == 'shuai') or (isMaxGo == False and board[target_x][target_y] == 'jiang'):
                        ability = -importances[board[target_x][target_y]] * 10
                        return ability
                else:
                    ability += factor *  importances[board[target_x][target_y]] / 2
        elif board[x][y][-5:-2] == 'pao':
            target_num = 0
            for i in range(1, 11):
                target_x = i
                if i < x:
                    target_x = x - i
                if i == x or board[target_x][y] == '0':
                    continue
                if target_num == 0:
                    target_num = 1
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[target_x][y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][y]]
                    else:
                        ability -= factor2 * importances[board[target_x][y]]
                    if (isMaxGo and board[target_x][y] == 'shuai') or (isMaxGo == False and board[target_x][y] == 'jiang'):
                        ability = -importances[board[target_x][y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[target_x][y] != 'shuai' and board[target_x][y] != 'jiang':
                    ability += factor *  importances[board[target_x][y]] / 2
                else:
                    ability += factor3 *  importances[board[target_x][y]] / 10
                target_num = 0
                if i > x:
                    break 
            target_num = 0
            for i in range(1, 10):
                target_y  = i
                if i < y:
                    target_y = y - i
                if i == y or board[x][target_y] == '0':
                    continue  
                if target_num == 0:
                    target_num = 1
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[x][target_y]]
                    else:
                        ability -= factor2 * importances[board[x][target_y]]
                    if (isMaxGo and board[x][target_y] == 'shuai') or (isMaxGo == False and board[x][target_y] == 'jiang'):
                        ability = -importances[board[x][target_y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[x][target_y] != 'shuai' and board[x][target_y] != 'jiang':
                    ability += factor *  importances[board[x][target_y]] / 2
                else:
                    ability += factor3 *  importances[board[x][target_y]] / 10
                target_num = 0
                if i > y:
                    break
        elif board[x][y][-5:-2] == 'che':
            for i in range(1, 11):
                target_x = i
                if i < x:
                    target_x = x - i
                if i == x or board[target_x][y] == '0':
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[target_x][y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][y]]
                    else:
                        ability -= importances[board[target_x][y]]
                    if (isMaxGo and board[target_x][y] == 'shuai') or (isMaxGo == False and board[target_x][y] == 'jiang'):
                        ability = -importances[board[target_x][y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[target_x][y] != 'shuai' and board[target_x][y] != 'jiang':
                    ability += factor *  importances[board[target_x][y]] / 2
                else:
                    ability += factor3 *  importances[board[target_x][y]] / 10
                if i > x:
                    break 
            for i in range(1, 10):
                target_y  = i
                if i < y:
                    target_y = y - i
                if i == y or board[x][target_y] == '0':
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[x][target_y]]
                    else:
                        ability -= factor2 * importances[board[x][target_y]]
                    if (isMaxGo and board[x][target_y] == 'shuai') or (isMaxGo == False and board[x][target_y] == 'jiang'):
                        ability = -importances[board[x][target_y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[x][target_y] != 'shuai' and board[x][target_y] != 'jiang':
                    ability += factor *  importances[board[x][target_y]] / 2
                else:
                    ability += factor3 *  importances[board[x][target_y]] / 10
                if i > y:
                    break
        elif board[x][y][-4:-2] == 'ma':
            for step in steps['ma']:      
                target_x = x + step[0]
                target_y = y + step[1]
                # 马脚的位置
                lock_pos_x = x + int(step[0] / 2)
                lock_pos_y = y + int(step[1] / 2)
                if self.is_legal_place(target_x, target_y) == False or board[lock_pos_x][lock_pos_y] != '0':
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[target_x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][target_y]]
                    else:
                        ability -= factor2 * importances[board[target_x][target_y]]
                    if (isMaxGo and board[target_x][target_y] == 'shuai') or (isMaxGo == False and board[target_x][target_y] == 'jiang'):
                        ability = -importances[board[target_x][target_y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[target_x][target_y] != 'shuai' and board[target_x][target_y] != 'jiang':
                    ability += factor *  importances[board[target_x][target_y]] / 2
                else:
                    ability += factor3 *  importances[board[target_x][target_y]] / 10
        elif board[x][y][-7:-2] == 'xiang':
            for step in steps['xiang']:
                target_x = x + step[0]
                target_y = y + step[1]
                # 象脚的位置
                lock_pos_x = x + int(step[0] / 2)
                lock_pos_y = y + int(step[1] / 2)
                if self.is_legal_place(target_x, target_y) == False or board[lock_pos_x][lock_pos_y] != '0':
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[target_x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][target_y]]
                    else:
                        ability -= factor2 * importances[board[target_x][target_y]]
                    if (isMaxGo and board[target_x][target_y] == 'shuai') or (isMaxGo == False and board[target_x][target_y] == 'jiang'):
                        ability = -importances[board[target_x][target_y]] * 10
                        return ability
                # 保护到己方的棋子
                elif board[target_x][target_y] != 'shuai' and board[target_x][target_y] != 'jiang':
                    ability += factor *  importances[board[target_x][target_y]] / 2
                else:
                    ability += factor3 *  importances[board[target_x][target_y]] / 10
        elif board[x][y][-5:-2] == 'shi':
            for step in steps['shi']:
                target_x = x + step[0]
                target_y = y + step[1]
                border_x = (1, 4)
                if board[x][y][:-6] == 'red':
                    border_x = (8, 11)
                if self.is_legal_place(target_x, target_y, border_x, (4, 7)) == False:
                    continue
                # 攻击范围内有敌方的棋子
                if importances[board[target_x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][target_y]]
                    else:
                        ability -= factor2 * importances[board[target_x][target_y]]
                # 保护到己方的棋子
                elif board[target_x][target_y] != 'shuai' and board[target_x][target_y] != 'jiang':
                    ability += factor *  importances[board[target_x][target_y]] / 2
                else:
                    ability += factor3 *  importances[board[target_x][target_y]] / 10
        elif board[x][y] == 'shuai' or board[x][y] == 'jiang':
            for step in steps['jiang']:
                target_x = x + step[0]
                target_y = y + step[1]
                border_x = (1, 4)
                border_y = (4, 7)
                if board[x][y] == 'shuai':
                    border_x = (8, 11)
                if self.is_legal_place(target_x, target_y, border_x, border_y) == False:
                    continue
                if importances[board[target_x][target_y]] * importances[board[x][y]] < 0:
                    # 当轮到broad[x][y]对应的棋子下棋时，攻击有效
                    if (isMaxGo * importances[board[x][y]] > 0) or (isMaxGo == False and importances[board[x][y]] < 0):
                        ability -= importances[board[target_x][target_y]]
                    else:
                        ability -= factor2 * importances[board[target_x][target_y]]
                else:
                    ability += factor *  importances[board[target_x][target_y]] / 2
        return int(ability)

    def is_legal_place(self, x, y, border_x = (1, 10), border_y = (1, 9)):
        if x < border_x[0] or x > border_x[1]:
            return False
        if y < border_y[0] or y > border_y[1]:
            return False
        return True

    # 产生解空间
    # 根据层数判断是哪一方进行操作
    def gen_moves(self, moves, depth):
        global board
        global red_alive
        global black_alive
        global positions
        red_go = False
        if depth % 2 == 0:
            red_go = False
        else:
            red_go = True

        color = self.turn_color
        select = self.select
        pos = self.select_pos[:]

        if red_go:
            self.turn_color = 'R'
            for piece in red_alive:
                x, y = positions[piece]
                if board[x][y] != '0':
                    self.select = board[x][y]
                    self.select_pos[0] = x
                    self.select_pos[1] = y
                    # 产生解空间
                    # 三个方向
                    if self.select.find('bing') != -1:
                        if self.moveable(x - 1, y):
                            moves.append([x, y, x - 1, y])
                        if self.moveable(x, y - 1):
                            moves.append([x, y, x, y - 1])
                        if self.moveable(x, y + 1):
                            moves.append([x, y, x, y + 1])
                    # 十字型（车与炮是一样的）
                    elif self.select.find('red_pao') != -1 or self.select.find('red_che') != -1:
                        for i in range(1, 11):
                            if self.moveable(i, y):
                                moves.append([x, y, i, y])
                        for i in range(1, 10):
                            if self.moveable(x, i):
                                moves.append([x, y, x, i])
                    # 日字走法：8种走位
                    elif self.select.find('red_ma') != -1:
                        if self.moveable(x + 1, y - 2):
                            moves.append([x, y, x + 1, y - 2])
                        if self.moveable(x - 1, y - 2):
                            moves.append([x, y, x - 1, y - 2])
                        if self.moveable(x - 1, y + 2):
                            moves.append([x, y, x - 1, y + 2])
                        if self.moveable(x + 1, y + 2):
                            moves.append([x, y, x + 1, y + 2])
                        if self.moveable(x - 2, y + 1):
                            moves.append([x, y, x - 2, y + 1])
                        if self.moveable(x - 2, y - 1):
                            moves.append([x, y, x - 2, y - 1])
                        if self.moveable(x + 2, y - 1):
                            moves.append([x, y, x + 2, y - 1])
                        if self.moveable(x + 2, y + 1):
                            moves.append([x, y, x + 2, y + 1])
                    # 田氏走法：4中走位
                    elif self.select.find('red_xiang') != -1:
                        if self.moveable(x + 2, y + 2):
                            moves.append([x, y, x + 2, y + 2])
                        if self.moveable(x + 2, y - 2):
                            moves.append([x, y, x + 2, y - 2])
                        if self.moveable(x - 2, y - 2):
                            moves.append([x, y, x - 2, y - 2])
                        if self.moveable(x - 2, y + 2):
                            moves.append([x, y, x - 2, y + 2])
                    # 斜式走法：4种走位
                    elif self.select.find('red_shi') != -1:
                        if self.moveable(x + 1, y + 1):
                            moves.append([x, y, x + 1, y + 1])
                        if self.moveable(x + 1, y - 1):
                            moves.append([x, y, x + 1, y - 1])
                        if self.moveable(x - 1, y - 1):
                            moves.append([x, y, x - 1, y - 1])
                        if self.moveable(x - 1, y + 1):
                            moves.append([x, y, x - 1, y + 1])
                    # 帅
                    elif self.select.find('shuai') != -1:
                        if self.moveable(x + 1, y):
                            moves.append([x, y, x + 1, y])
                        if self.moveable(x, y - 1):
                            moves.append([x, y, x, y - 1])
                        if self.moveable(x - 1, y):
                            moves.append([x, y, x - 1, y])
                        if self.moveable(x, y + 1):
                            moves.append([x, y, x, y + 1])
        else:
            self.turn_color = 'B'
            for piece in black_alive:
                x, y = positions[piece]
                if board[x][y] != '0':
                    self.select = board[x][y]
                    self.select_pos[0] = x
                    self.select_pos[1] = y
                    # 卒
                    if self.select.find('zu') != -1:
                        if self.moveable(x + 1, y):
                            moves.append([x, y, x + 1, y])
                        if self.moveable(x, y - 1):
                            moves.append([x, y, x, y - 1])
                        if self.moveable(x, y + 1):
                            moves.append([x, y, x, y + 1])
                    # 炮与车
                    elif self.select.find('black_pao') != -1 or self.select.find('black_che') != -1:
                        for i in range(1, 11):
                            if self.moveable(i, y):
                                moves.append([x, y, i, y])
                        for i in range(1, 10):
                            if self.moveable(x, i):
                                moves.append([x, y, x, i])
                    # 马
                    elif self.select.find('black_ma') != -1:
                        if self.moveable(x + 1, y - 2):
                            moves.append([x, y, x + 1, y - 2])
                        if self.moveable(x - 1, y - 2):
                            moves.append([x, y, x - 1, y - 2])
                        if self.moveable(x - 1, y + 2):
                            moves.append([x, y, x - 1, y + 2])
                        if self.moveable(x + 1, y + 2):
                            moves.append([x, y, x + 1, y + 2])
                        if self.moveable(x - 2, y + 1):
                            moves.append([x, y, x - 2, y + 1])
                        if self.moveable(x - 2, y - 1):
                            moves.append([x, y, x - 2, y - 1])
                        if self.moveable(x + 2, y - 1):
                            moves.append([x, y, x + 2, y - 1])
                        if self.moveable(x + 2, y + 1):
                            moves.append([x, y, x + 2, y + 1])
                    # 象
                    elif self.select.find('black_xiang') != -1:
                        if self.moveable(x + 2, y + 2):
                            moves.append([x, y, x + 2, y + 2])
                        if self.moveable(x + 2, y - 2):
                            moves.append([x, y, x + 2, y - 2])
                        if self.moveable(x - 2, y - 2):
                            moves.append([x, y, x - 2, y - 2])
                        if self.moveable(x - 2, y + 2):
                            moves.append([x, y, x - 2, y + 2])
                    # 士
                    elif self.select.find('black_shi') != -1:
                        if self.moveable(x + 1, y + 1):
                            moves.append([x, y, x + 1, y + 1])
                        if self.moveable(x + 1, y - 1):
                            moves.append([x, y, x + 1, y - 1])
                        if self.moveable(x - 1, y - 1):
                            moves.append([x, y, x - 1, y - 1])
                        if self.moveable(x - 1, y + 1):
                            moves.append([x, y, x - 1, y + 1])
                    # 将
                    elif self.select.find('jiang') != -1:
                        if self.moveable(x + 1, y):
                            moves.append([x, y, x + 1, y])
                        if self.moveable(x, y - 1):
                            moves.append([x, y, x, y - 1])
                        if self.moveable(x - 1, y):
                            moves.append([x, y, x - 1, y])
                        if self.moveable(x, y + 1):
                            moves.append([x, y, x, y + 1])
        self.turn_color = color
        self.select = select
        self.select_pos = pos[:]

    # 进行一个棋子的位移并移除相应的棋子
    def make_a_move(self, ox, oy, dx, dy):
        global board
        global red_alive
        global black_alive
        global positions
        if board[dx][dy] != '0':
            positions[board[ox][oy]] = (dx, dy)
            if board[dx][dy] in red_alive:
                red_alive.remove(board[dx][dy])
                positions[board[dx][dy]] = None
            elif board[dx][dy] in black_alive:
                black_alive.remove(board[dx][dy])
                positions[board[dx][dy]] = None
        board[dx][dy] = board[ox][oy]
        board[ox][oy] = '0'


    # 回退一步
    def move_back(self, lastMove, lastKill):
        global board
        global red
        global red_alive
        global black
        global black_alive
        global positions
        if lastMove == None:
            print('none error')
            return
        ox, oy, dx, dy = lastMove
        if board[dx][dy] == '':
            print('error', dx, dy)
        board[ox][oy] = board[dx][dy]
        positions[board[dx][dy]] = (ox, oy)
        if lastKill != '':
            board[dx][dy] = lastKill
            if lastKill in red:
                red_alive.append(lastKill)
                positions[lastKill] = (dx, dy)
            elif lastKill in black:
                black_alive.append(lastKill)
                positions[lastKill] = (dx, dy)
        else:
            board[dx][dy] = '0'

    # 鼠标事件监听
    def mousePressEvent(self, e):
        global board
        global red_alive
        global black_alive
        x = e.x() / self.boardCellSize
        y = e.y() / self.boardCellSize
        if (x - int(x) / 1 >= 0.5):
            x = int(x) + 1
        else:
            x = int(x)
        if (y - int(y) / 1 >= 0.5):
            y = int(y) + 1
        else:
            y = int(y)
        x = x + y
        y = x - y
        x = x - y
        if self.human_move_done == False and not (x == 0 or x == 11 or y == 0 or y == 10):
            if self.select == '' and board[x][y] != '0':
                self.select = board[x][y]
                self.select_pos = [x, y]
                self.statusBar().showMessage(self.select)
            elif self.select != '':
                if self.moveable(x, y):
                    self.piece_move(x, y)
                    self.human_move_done = True
                else:
                    self.select = ''
                    self.select_pos = [0, 0]
                    self.statusBar().showMessage(" ")

        if self.human_move_done and self.start == False:
            self.statusBar().showMessage(" ")
            if self.end_check():
                self.celebrate()
            else:
                self.turn = 'A'
                if self.turn_color == 'R':
                    self.turn_color = 'B'
                else:
                    self.turn_color = 'R'
                self.vs_AI()

    # 用于判断是否能够进行移动
    def moveable(self, x, y):
        global board
        global red_alive
        global black_alive
        # 判断是否超过象棋边界
        if x <= 0 or y <= 0 or x >= 11 or y >= 10:
            return False
        if self.select_pos == [x, y]:
            return False
        if self.turn_color == 'B':
            # 判断是否有棋子
            if board[x][y] in black_alive:
                return False
            # 卒的移动范围
            if self.select == 'zu_0' or self.select == 'zu_1' or self.select == 'zu_2' or self.select == 'zu_3' or self.select == 'zu_4':
                if self.select_pos[0] > x:
                    return False
                elif self.select_pos[0] <= 5 and y != self.select_pos[1]:
                    return False
                elif abs(y - self.select_pos[1]) + abs(x - self.select_pos[0]) > 1:
                    return False
                else:
                    return True
            # 炮的移动范围
            if self.select == 'black_pao_1' or self.select == 'black_pao_0':
                if board[x][y] in red_alive and self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 1:
                    return True
                elif board[x][y] == '0' and self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 0:
                    return True
                else:
                    return False
            # 车的移动范围
            if self.select == 'black_che_1' or self.select == 'black_che_0':
                if self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 0:
                    return True
                else:
                    return False
            # 马的移动范围
            if self.select == 'black_ma_1' or self.select == 'black_ma_0':
                if abs(y - self.select_pos[1]) == 2:
                    if abs(x - self.select_pos[0]) == 1 and board[self.select_pos[0]][int((y + self.select_pos[1]) / 2)] == '0':
                        return True
                elif abs(y - self.select_pos[1]) == 1:
                    if abs(x - self.select_pos[0]) == 2 and board[int((x + self.select_pos[0]) / 2)][self.select_pos[1]] == '0':
                        return True
                else:
                    return False
            # 象的移动范围
            if self.select == 'black_xiang_1' or self.select == 'black_xiang_0':
                if x > 5:
                    return False
                if abs(y - self.select_pos[1]) == 2 and abs(x - self.select_pos[0]) == 2:
                    if board[int((x + self.select_pos[0]) / 2)][int((y + self.select_pos[1]) / 2)] == '0':
                        return True
                else:
                    return False
            # 士的移动范围
            if self.select == 'black_shi_1' or self.select == 'black_shi_0':
                if self.select_pos[0] == 1 or self.select_pos[0] == 3:
                    if x != 2:
                        return False
                if self.select_pos[1] == 4 or self.select_pos[1] == 6:
                    if y != 5:
                        return False
                if self.select_pos[0] == 2 and self.select_pos[1] == 5:
                    if x != 1 and x != 3:
                        return False
                    if y != 4 and y != 6:
                        return False
                return True
            # 将的移动范围
            if self.select == 'jiang':
                if x > 3 or y < 4 or y > 6:
                    return False
                else:
                    return True
        # 以下是红方的移动范围，与上面的类似，只是数字的略微改变
        elif self.turn_color == 'R':
            if board[x][y] in red_alive:
                return False
            if self.select == 'bing_0' or self.select == 'bing_1' or self.select == 'bing_2' or self.select == 'bing_3' or self.select == 'bing_4':
                if self.select_pos[0] < x:
                    return False
                elif self.select_pos[0] >= 6 and y != self.select_pos[1]:
                    return False
                elif abs(y - self.select_pos[1]) + abs(x - self.select_pos[0]) > 1:
                    return False
                else:
                    return True
            if self.select == 'red_pao_1' or self.select == 'red_pao_0':
                if board[x][y] in black_alive and self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 1:
                    return True
                elif board[x][y] == '0' and self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 0:
                    return True
                else:
                    return False
            if self.select == 'red_che_1' or self.select == 'red_che_0':
                if self.hmn_between(self.select_pos[0], self.select_pos[1], x, y) == 0:
                    return True
                else:
                    return False
            if self.select == 'red_ma_1' or self.select == 'red_ma_0':
                if abs(y - self.select_pos[1]) == 2:
                    if abs(x - self.select_pos[0]) == 1 and board[self.select_pos[0]][
                        int((y + self.select_pos[1]) / 2)] == '0':
                        return True
                elif abs(y - self.select_pos[1]) == 1:
                    if abs(x - self.select_pos[0]) == 2 and board[int((x + self.select_pos[0]) / 2)][
                        self.select_pos[1]] == '0':
                        return True
                else:
                    return False
            if self.select == 'red_xiang_1' or self.select == 'red_xiang_0':
                if x < 6:
                    return False
                if abs(y - self.select_pos[1]) == 2 and abs(x - self.select_pos[0]) == 2:
                    if board[int((x + self.select_pos[0]) / 2)][int((y + self.select_pos[1]) / 2)] == '0':
                        return True
                else:
                    return False
            if self.select == 'red_shi_1' or self.select == 'red_shi_0':
                if self.select_pos[0] == 8 or self.select_pos[0] == 10:
                    if x != 9:
                        return False
                if self.select_pos[1] == 4 or self.select_pos[1] == 6:
                    if y != 5:
                        return False
                if self.select_pos[0] == 9 and self.select_pos[1] == 5:
                    if x != 8 and x != 10:
                        return False
                    if y != 4 and y != 6:
                        return False
                return True
            if self.select == 'shuai':
                if x < 8 or y < 4 or y > 6:
                    return False
                else:
                    return True

    # 判断两点之间的棋子的数目
    def hmn_between(self, x, y, dx, dy):
        global board
        global red_alive
        global black_alive
        count = 0
        if x != dx:
            if x > dx:
                x = x + dx
                dx = x - dx
                x = x - dx
            for num in range(x + 1, dx):
                if board[num][y] != '0':
                    count = count + 1
            return count
        elif y != dy:
            if y > dy:
                y = y + dy
                dy = y - dy
                y = y - dy
            for num in range(y + 1, dy):
                if board[x][num] != '0':
                    count = count + 1
            return count

    def piece_move(self, x, y):
        global board
        global red_alive
        global black_alive
        global positions
        if not board[x][y] == '0':
            positions[board[x][y]] = None
            if board[x][y] in red_alive:
                red_alive.remove(board[x][y])
            else:
                black_alive.remove(board[x][y])
            eval('self.' + board[x][y]).move(-1 * self.boardCellSize - self.offset, -1 * self.boardCellSize - self.offset)
        positions[self.select] = (x, y)
        # print('piece move:', self.select, x, y, self.select_pos[0], self.select_pos[1])
        board[x][y] = self.select
        board[self.select_pos[0]][self.select_pos[1]] = '0'
        eval('self.' + self.select).move(y * self.boardCellSize - self.offset, x * self.boardCellSize - self.offset)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Chess()
    print('chess loaded...')
    sys.exit(app.exec_())