#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from art import Ui_MainWindow

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.result = {}
        self.result['per_file_info'] = []
        self.result['total_file_info'] = [0, 0, 0, 0, 0]

        self.path_btn.clicked.connect(self.openFile)
        self.start_btn.clicked.connect(self.start)

        #列宽自动分配
        self.file_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        #手动可调整列宽
        self.file_table.horizontalHeader().setSectionResizeMode(2,QtWidgets.QHeaderView.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(3,QtWidgets.QHeaderView.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(4,QtWidgets.QHeaderView.Interactive)
        self.file_table.horizontalHeader().setSectionResizeMode(5,QtWidgets.QHeaderView.Interactive)
        #self.file_table.horizontalHeader().setSectionResizeMode(6,QtWidgets.QHeaderView.Interactive)


        #随内容分配列宽
        self.file_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1,QtWidgets.QHeaderView.ResizeToContents)

    def openFile(self):
        get_directory_path = QtWidgets.QFileDialog.getExistingDirectory(self,"选取指定文件夹","")
        self.path_LineEdit.setText(str(get_directory_path))

    def CalcLines(self, lineList, f_type):
        if f_type == '.vhd':
            result = self.CalcVHDL(lineList)
        elif f_type in ['.c', '.cpp', '.h', '.v']:
            result = self.CalcCV(lineList)
        return result

    def CalcVHDL(self,lineList):
        totalLines = len(lineList)
        lineNo = 0
        codeLines = 0
        commentLines = 0
        emptyLines = 0

        while lineNo < totalLines:
            line = lineList[lineNo].strip().decode('utf-8', 'ignore')
            if line.isspace():  # 空行
                emptyLines += 1
                lineNo += 1
                continue

            regMatch = re.match('^([^-]*)--+(.*)$', line)
            if regMatch != None:  # 注释行
                commentLines += 1

                # 代码&注释混合行
                if regMatch.group(1) != '':
                    codeLines += 1
            else:  # 代码行
                codeLines += 1

            lineNo += 1
            continue

        return [totalLines, codeLines, commentLines, emptyLines, '{:.2%}'.format(commentLines / totalLines)]

    def CalcCV(self, lineList):
        totalLines = len(lineList)
        lineNo = 0
        codeLines = 0
        commentLines = 0
        emptyLines = 0

        while lineNo < totalLines:
            line = lineList[lineNo].strip().decode('utf-8', 'ignore')
            if line == '' or line in ['\n','\r\n']:  # 空行
                emptyLines += 1
                lineNo += 1
                continue

            regMatch = re.match('^([^/]*)/(/|\*)+(.*)$', line)
            if regMatch != None:  # 注释行
                commentLines += 1

                # 代码&注释混合行
                if regMatch.group(1) != '':
                    codeLines += 1
                elif regMatch.group(2) == '*' and re.match('^.*\*/.+$', regMatch.group(3)) != None:
                    codeLines += 1

                # 行注释或单行块注释
                if '/*' not in line or '*/' in line:
                    lineNo += 1
                    continue

                # 跨行块注释
                lineNo += 1
                while lineNo < totalLines and '*/' not in line:
                    if line.isspace():
                        emptyLines += 1
                    else:
                        commentLines += 1
                    lineNo = lineNo + 1
                    continue
                commentLines += 1  # '*/'所在行
            else:  # 代码行
                codeLines += 1

            lineNo += 1
            continue

        return [totalLines, codeLines, commentLines, emptyLines, '{:.2%}'.format(commentLines / totalLines)]

    def get_result(self, file_path):
        self.result['per_file_info'] = []
        self.result['total_file_info'] = [0, 0, 0, 0, 0]

        if not os.path.exists(file_path):
            QMessageBox.warning(self, '警告', '“' + file_path + '”' + '路径不存在！！！', )
            return False

        if not os.path.isdir(file_path):
            QMessageBox.warning(self, '警告', file_path + '不是路径！！！', )
            return False

        select_type = self.get_selected_type()
        if len(select_type) == 0:
            QMessageBox.information(self, '提示', '请选择需要统计的文件类型！！！')
            return False

        for home, dirs, files in os.walk(file_path):
            for filename in files:
                f_type = os.path.splitext(filename)[1]
                if f_type in select_type:
                    try:
                        fileObj = open(os.path.join(home, filename), 'rb')
                        lineList = fileObj.readlines()
                        fileObj.close()
                    except IOError:
                        QMessageBox.warning(self, '警告', os.path.join(home, filename)+ '打开失败！！！')

                    per_file_countInfo = self.CalcLines(lineList,f_type)
                    per_file_countInfo.append(filename)
                    per_file_countInfo.append(home)
                    self.result['per_file_info'].append(per_file_countInfo)

                    for i in range(0, 4):
                        self.result['total_file_info'][i] = self.result['total_file_info'][i] + per_file_countInfo[i]

        if self.result['total_file_info'][0] != 0:
            self.result['total_file_info'][4] = '{:.2%}'.format(self.result['total_file_info'][2]/self.result['total_file_info'][0])
        return True

    def get_selected_type(self):
        select_type = []
        if self.C_checkBox.isChecked():
            select_type.append('.c')
            select_type.append('.cpp')
            select_type.append('.h')
        else:
            if '.c' in select_type:
                select_type.remove('.c')
            if '.cpp' in select_type:
                select_type.remove('.cpp')
            if '.h' in select_type:
                select_type.remove('.h')
        if self.V_checkBox.isChecked():
            select_type.append('.v')
        else:
            if '.v' in select_type:
                select_type.remove('.v')
        if self.VHD_checkBox.isChecked():
            select_type.append('.vhd')
        else:
            if '.vhd' in select_type:
                select_type.remove('.vhd')
        return select_type

    def clear_data(self):
        self.file_table.setRowCount(0)
        self.file_table.clearContents()
        self.sum_lines_lineEdit.setText('')
        self.code_lines_lineEdit.setText('')
        self.zhushi_lines_lineEdit.setText('')
        self.emp_lines_lineEdit.setText('')
        self.zhushilv_lineEdit.setText('')

    def show_result(self):
        self.clear_data()
        if len(self.result['per_file_info']) == 0:
            QMessageBox.information(self, '提示', '该路径下没有您选择的文件类型！！！')
            return

        for item in self.result['per_file_info']:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)

            file_name = QtWidgets.QTableWidgetItem(item[5])
            file_path = QtWidgets.QTableWidgetItem(item[6])
            total_lines = QtWidgets.QTableWidgetItem(str(item[0]))
            code_lines = QtWidgets.QTableWidgetItem(str(item[1]))
            comment_lines = QtWidgets.QTableWidgetItem(str(item[2]))
            empty_lines = QtWidgets.QTableWidgetItem(str(item[3]))
            rate = QtWidgets.QTableWidgetItem(str(item[4]))

            self.file_table.setItem(row, 0, file_name)
            self.file_table.setItem(row, 1, file_path)
            self.file_table.setItem(row, 2, total_lines)
            self.file_table.setItem(row, 3, code_lines)
            self.file_table.setItem(row, 4, comment_lines)
            self.file_table.setItem(row, 5, empty_lines)
            self.file_table.setItem(row, 6, rate)

            self.sum_lines_lineEdit.setText(str(self.result['total_file_info'][0]))
            self.code_lines_lineEdit.setText(str(self.result['total_file_info'][1]))
            self.zhushi_lines_lineEdit.setText(str(self.result['total_file_info'][2]))
            self.emp_lines_lineEdit.setText(str(self.result['total_file_info'][3]))
            self.zhushilv_lineEdit.setText(str(self.result['total_file_info'][4]))

    def start(self):
        file_path = self.path_LineEdit.text()
        if self.get_result(file_path):
            self.show_result()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())