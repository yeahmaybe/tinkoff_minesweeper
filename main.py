from random import randrange as rand
import re
import queue as qu
from os import listdir

class Cell:
    __isOpened = bool()
    __hasFlag = bool()
    __hasBomb = bool()

    __bombs_around = int()

    def __init__(self):
        self.__isOpened = False
        self.__hasFlag = False
        self.__hasBomb = False
        self.__bombs_around = 0

    def isOpened(self):
        return self.__isOpened

    def hasBomb(self):
        return self.__hasBomb

    def hasFlag(self):
        return self.__hasFlag

    def open(self):
        self.__isOpened = True

    def mine(self):
        self.__hasBomb = True
        self.__bombs_around = 9

    def flag(self):
        self.__hasFlag = True

    def deflag(self):
        self.__hasFlag = False

    def set_bombs_number(self, num):
        if type(num) == int:
            self.__bombs_around = num
            return True
        else:
            return False

    def bombs_around(self):
        return self.__bombs_around


class Matrix:
    __rows = int()
    __columns = int()
    __cells = list()
    __cells_num = int()
    __bombs_number = int()
    __flags_number = int()

    def rows(self):
        return self.__rows

    def columns(self):
        return self.__columns

    def inRange(self, args):
        if 0 <= args[0] <= self.rows() and 0 <= args[1] <= self.columns():
            return True

        return False

    def cells(self):
        return self.__cells

    def cellAt(self, row, column):
        if 0 <= row < self.rows() and 0 <= column < self.columns():
            return self.__cells[row][column]

    def bombs_around(self, row, column):
        return self.cellAt(row, column).bombs_around()

    def bombs_number(self):
        return self.__bombs_number

    def set_bombs_number(self, num):
        if self.__bombs_number == 0:
            self.__bombs_number = num
            self.__flags_number = num
        else:
            return False

    def demine(self):
        self.__bombs_number -= 1

    def contain(self, row, column):
        if 0 <= row < self.rows() and 0 <= column < self.columns():
            return True
        return False

    def flags_remain(self):
        return self.__flags_number

    def flag_decrease(self):
        self.__flags_number -= 1

    def __init__(self, rows=None, columns=None):

        isLoading = False
        if rows and columns:
            isLoading = True

        if not isLoading:
            print("Введите высоту и ширину поля:", end=' ')
            rows, columns = self.__enter_numbers(2)

        self.__rows = rows
        self.__columns = columns
        self.__cells_num = rows * columns

        self.__cells = []
        for r in range(rows):
            tmp = []
            for c in range(columns):
                tmp.append(Cell())
            self.__cells.append(tmp)

        if not isLoading:
            self.__mine_bombs()
            for r in range(self.rows()):
                for c in range(self.columns()):
                    self.__count_bombs_around(r, c)

    def __enter_numbers(self, num):
        ans = []
        entered = False
        while not entered:
            number = input()
            try:
                ans = list(map(int, number.split()))
                if len(ans) == num:
                    entered = True
                else:
                    print("Количество чисел должно быть равным", num)
            except:
                print("Введите число!")
        return ans

    def __mine_bombs(self):
        print('Введите количество бомб:', end=' ')
        self.__bombs_number = self.__enter_numbers(1)[0]
        self.__flags_number = self.__bombs_number

        cells = list()
        for cellnum in range(self.rows() * self.columns()+1):
            cells.append(cellnum)

        for i in range(self.__bombs_number):
            index = rand(0, len(cells)-1)
            num = cells[index]
            cells.remove(num)

            target = self.cellAt(num // self.columns(), num % self.columns())
            target.mine()

    def __count_bombs_around(self, row, column):
        if not self.cellAt(row, column).hasBomb():
            counter = 0
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if self.contain(row + y, column + x) and self.cellAt(row + y, column + x).hasBomb():
                        counter += 1
            self.cellAt(row, column).set_bombs_number(counter)

    def set_bombs_around(self, row, column):
        self.__count_bombs_around(row, column)

    def draw(self):
        for row in range(self.rows()):
            for column in range(self.columns()):
                code = self.bombs_around(row, column)
                target = self.cellAt(row, column)

                if target.hasFlag():
                    print(flag_char, end='  ')

                elif not target.isOpened():
                    print(closed_char, end='  ')
                elif code == 0:
                    print(opened_char, end='  ')
                elif code == 9:
                    print(bomb_char, end='  ')
                else:
                    print(self.bombs_around(row, column), end='  ')
            print()

    def uncover(self):
        for row in self.__cells:
            for cell in row:
                cell.open()
                cell.deflag()

    def isUncovered(self):
        for row in self.__cells:
            for cell in row:
                if not cell.isOpened():
                    return False
        return True

    def clear_around(self, row, column):
        queue = qu.Queue()
        queue.put(row * self.columns() + column)

        while not queue.empty():
            num = queue.get()
            Y = num // self.columns()
            X = num % self.columns()
            for y in range(-1, 2):
                for x in range(-1, 2):
                    target = self.cellAt(Y + y, X + x)
                    if self.contain(Y + y, X + x) and not target.isOpened():
                        target.open()
                        if target.bombs_around() == 0:
                            queue.put((Y + y) * self.columns() + X + x)



class Command:
    __type = str()
    __args = list()

    __turn = str()
    __flag = str()
    __list = list()
    __commands = list()

    def __init__(self, text):
        self.__common = [r'\s*help\s*',
                         r'\s*new\s*',
                         r'\s*quit\s*']

        self.__special = [r'\s*save\s*',
                          r'\s*save\s+\w+',
                          r'\s*load\s*',
                          r'\s*load\s+\w+']

        self.__list = ['help - список команд',
                       'new - новая игра',
                       'save <название> - соханить',
                       'load <название> - загрузить',
                       'X Y open - открыть ячейку',
                       'X Y flag - поставить флаг',
                       'quit - выйти']

        self.__open = r'\s*\d+\s+\d+\s+open\s*'
        self.__flag = r'\s*\d+\s+\d+\s+flag\s*'

        defined = False
        for tp in self.__common:
            if re.fullmatch(tp, text.lower()):
                self.__type = text.lower().split()[0]
                self.__args = None
                defined = True

        for tp in self.__special:
            if re.fullmatch(tp, text.lower()):
                self.__type = text.lower().split()[0]
                self.__args = text.lower().split()[1:]
                defined = True

        if not defined:
            if re.fullmatch(self.__open, text.lower()):
                self.__type = list(text.split())[2]
                self.__args = list(map(int, text[:-4].split()))
            elif re.fullmatch(self.__flag, text.lower()):
                self.__type = list(text.split())[2]
                self.__args = list(map(int, text[:-4].split()))
            else:
                self.__type = None
                self.__args = None

    def type(self):
        return self.__type

    def list(self):
        return self.__list

    def arg(self, n):
        if n == 0:
            return self.__args[0]
        if n == 1:
            return self.__args[1]
        else:
            return None

    def args(self):
        return self.__args

    def quit(self):
        return Command('quit')


class Administrator:
    __field: Matrix
    __field = None
    __cycle = 15

    def defeat(self):
        self.__field.uncover()
        self.__field.draw()
        print('Сапер ошибается лишь раз в жизни. Но можно начать новую!')
        self.__field = None

    def victory(self):
        self.__field.uncover()
        self.__field.draw()
        print('Задача выполнена! Ждем на следующем задании.')
        self.__field = None

    def isWin(self):
        if self.__field.isUncovered() \
                or self.__field.bombs_number() == 0:
            return True
        return False

    def help(self):
        instruction = Command('None')
        print('-------Список команд--------')
        print(*instruction.list(), sep='\n')
        print('----------------------------')

    def new(self):
        self.__field = Matrix()
        self.__field.draw()

    def turn(self, instruction):

        flagsDecreased = False
        notEnoughFlags = False
        alreadyFlag = False
        alreadyOpen = False

        if not self.__field:
            print('Игра еще не началась. Чтобы начать, введите "new"')
        else:
            if not listener.__field.inRange(list(map(int, instruction.args()))):
                print('Нет клетки с такой координатой!')
                return 0

            target = self.__field.cellAt(instruction.arg(0) - 1, instruction.arg(1) - 1)

            if target.hasFlag():
                alreadyFlag = True

            elif target.isOpened():
                alreadyOpen = True

            else:
                target.open()
                if instruction.type() == 'open':
                    if target.hasBomb():
                        self.defeat()
                        return 0

                    if target.bombs_around() == 0:
                        self.__field.clear_around(instruction.arg(0) - 1, instruction.arg(1) - 1)

                elif instruction.type() == 'flag':
                    target.flag()
                    self.__field.flag_decrease()
                    if target.hasBomb():
                        self.__field.demine()
                    flagsDecreased = True

                if self.isWin():
                    self.victory()
                    return 0
                elif self.__field.flags_remain() == 0:
                    self.defeat()
                    return 0

            self.__field.draw()
            if flagsDecreased: print("Флагов осталось: ", self.__field.flags_remain())
            if notEnoughFlags: print("Не осталось флагов!")
            if alreadyFlag: print('В этой клетке уже выставлен флаг')
            if alreadyOpen: print('Эта клетка уже открыта')

    def save(self, instruction):
        if not self.__field:
            print('Нет активной сессии')
            return 0
        if not instruction.args():
            name = input('Введите имя сохранения: ')
        else:
            name = instruction.arg(0)
        file = open(name+'-sv', 'w')
        file.write(str(self.__field.rows()) + 'x' + str(self.__field.columns()) + '/')

        line = ""
        rank = 0
        for row in self.__field.cells():
            for cell in row:
                status = ''
                rank += 1
                if rank > self.__cycle:
                    line += '.'
                    rank = 1

                if not cell.hasBomb() and not cell.isOpened():
                    status = 0
                elif not cell.hasBomb() and cell.hasFlag():
                    status = 1
                elif not cell.hasBomb() and cell.isOpened():
                    status = 2
                elif cell.hasBomb() and not cell.hasFlag():
                    status = 3
                elif cell.hasBomb() and cell.hasFlag():
                    status = 4

                line += str(status)
        while rank < self.__cycle:
            line += '0'
            rank += 1
        crypted_line = line.split('.')
        for i in range(len(crypted_line)):
            crypted_line[i] = str(int(crypted_line[i], 5))

        file.write('.'.join(crypted_line))
        print('Game saved as', '"' + name + '"')

    def load(self, instruction):
        if not instruction.args():
            files = listdir()
            if filter(lambda f: f.endswith('-sv'), files):
                saves = filter(lambda f: f.endswith('-sv'), files)
                print('Текущие сохранения:')
                for save in saves:
                    print(save[:-3])
            name = input('Введите имя сохранения: ')
        else:
            name = instruction.arg(0)

        try:
            file = open(name+'-sv')
        except IOError as e:
            print(u'Такого сохранения нет!')
            return 0

        file = open(name+'-sv', 'r')
        rows = ''
        columns = ''
        c = file.read(1)
        while c != 'x':
            rows += c
            c = file.read(1)
        c = file.read(1)
        while c != '/':
            columns += c
            c = file.read(1)

        rows = int(rows)
        columns = int(columns)

        self.__field = Matrix(rows, columns)
        save = list(map(int, file.read().split('.')))

        mines = 0

        for num in range(len(save)):
            register = to5(save[num], self.__cycle)
            for i in range(len(register)):
                stat = register[i]
                row = (num * self.__cycle + i) // columns
                column = (num * self.__cycle + i) % columns
                target = self.__field.cellAt(row, column)

                if stat == '1':
                    target.flag()
                elif stat == '2':
                    target.open()
                elif stat == '3':
                    target.mine()
                    mines += 1
                elif stat == '4':
                    target.mine()
                    mines += 1
                    target.flag()

        self.__field.set_bombs_number(mines)

        for row in range(rows):
            for column in range(columns):
                self.__field.set_bombs_around(row, column)

        self.__field.draw()

    def execute(self, instruction: Command):

        if not instruction.type():
            print('Неизвестная команда. Введите "help" для получения списка команд')

        elif instruction.type() == 'help':
            self.help()

        elif instruction.type() == 'new':
            self.new()

        elif instruction.type() == 'open' \
                or instruction.type() == 'flag':
            self.turn(instruction)

        if instruction.type() == 'save':
            self.save(instruction)

        if instruction.type() == 'load':
            self.load(instruction)


def to5(num, cycle):
    if num == 0:
        ans = '0'
    ans = ''
    while num > 0:
        ans = str(num % 5) + ans
        num //= 5
    while len(ans) < cycle:
        ans = '0'+ans
    return ans

closed_char = '■'
opened_char = '□'
flag_char = '⚑'
bomb_char = '*'

listener = Administrator()
command = Command('help')

while command.type() != 'quit':
    listener.execute(command)
    command = Command(input())
