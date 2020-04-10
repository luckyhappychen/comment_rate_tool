#encoding=utf-8

from tkinter import *
from tkinter.filedialog import askdirectory
import tkinter.messagebox as tm
from tkinter import ttk
import caculate_1 as Ca


summary_str = ['总行数','代码行数','注释行数','空白行数','注释率']
      
class UI(object):
    def __init__(self):
        self.root = Tk()
        self.root.title('AnnotationRateTool')
        self.file_types = ['c', 'h', 'v']
        #self.root.resizable(width = False,height = False)

#######################选择文件路径#################################
    def select_path_func(self):
        self.file_path_var.set(askdirectory())

    def select_path(self):
        self.path_frame = Frame(self.root)
        self.path_frame.pack(fill = X, padx = 10, pady = 5)
        Button(self.path_frame, text = '选择路径', command = self.select_path_func).pack(side = LEFT, padx = 10)
    
        self.file_path_var = StringVar()
        Entry(self.path_frame, textvariable = self.file_path_var, width = 40).pack(side = LEFT, padx = 3, pady = 3)


#######################选择代码类型#################################
    def initial(self):
        mCa.file_type = []    
        
        nodes = self.file_excel.get_children("")
        for node in nodes:
            self.file_excel.delete(node)
        
        self.summary_entry_var['注释率'].set('0')
        
    def start_btn_clicked(self):
        print('button clicked')

        self.initial()
                      
        for item in mUi.file_types:
            if mUi.file_type_var[item].get():
                mCa.file_type.append(item)
        print(mCa.file_type)
            
        dir_path = self.file_path_var.get()
        
        if(dir_path == '' or len(mCa.file_type) == 0):
            tm.showwarning('',"文件路径或文件类型为空")
        
        mCa.CountDirLines(dir_path)
        
        i = 0
        
        for info in mCa.detailCountInfo:
            print(info)
            i = i + 1
            if(len(info) != 0 and (info[1][1] + info[1][2]) != 0):
                self.file_excel.insert("",'end',values = (i,info[0],info[1][0],info[1][1],info[1][2],info[1][3],'{:.2f}%'.format(info[1][1]/(info[1][1] + info[1][2]) * 100)))
         
        for i in range(0,len(summary_str) - 1):
            self.summary_entry_var[summary_str[i]].set(mCa.rawCountInfo[i])
        
        if(len(mCa.rawCountInfo)!= 0 and (mCa.rawCountInfo[1] + mCa.rawCountInfo[2]) != 0):
            self.summary_entry_var['注释率'].set('{:.2f}%'.format(mCa.rawCountInfo[1]/(mCa.rawCountInfo[1] + mCa.rawCountInfo[2]) * 100))
            
        print(mCa.rawCountInfo)
        return
        
    def select_file_type(self):
        self.file_type_frame = Frame(self.root)
        self.file_type_frame.pack(fill = X, padx = 20, pady = 5)
        
        Label(self.file_type_frame, text = '选择文件类型',).pack(side = LEFT)

        self.file_type_var = {}
        self.file_type_cb = {} 

        for file_type in self.file_types:
            self.file_type_var[file_type] = IntVar()
            self.file_type_cb[file_type] = Checkbutton(self.file_type_frame, text = file_type, variable = self.file_type_var[file_type])
            self.file_type_cb[file_type].pack(side = LEFT)
            
        self.start_btn = Button(self.file_type_frame, text = '开始', command = self.start_btn_clicked)
        self.start_btn.pack(side = LEFT, padx = 10)
   
   
#######################文件详细信息#################################
    '''
    def get_detail(self):
        print('button clicked')
        dir_path = mUi.file_path_var.get()
        mCa.CountDirLines(dir_path)

        
    def show_detail(self):
        nodes = self.file_excel.get_children()
        if node in nodes:
            self.file_excel.delete(node)
        
        for info in mCa.detailCountInfo:
            print(info)
            #self.file_excel.insert("",'end',)
        return
'''

    def file_detail(self):
        #head_str = ['序号','文件名','总行数','代码行数','注释行数','空白行数','注释率']
        self.show_detail_frame = Frame(self.root)
        self.show_detail_frame.pack(fill = X, padx = 10, pady = 10)
        mScrollbar = Scrollbar(self.show_detail_frame)
        mScrollbar.pack(side = RIGHT, fill = Y)
        self.file_excel = ttk.Treeview(self.show_detail_frame, show = 'headings', yscrollcommand = mScrollbar.set)
        mScrollbar['command'] = self.file_excel.yview
        self.file_excel["columns"] = ('序号','文件名','总行数','代码行数','注释行数','空白行数','注释率')
        #self.file_excel.bind('<ButtonRelease-1>',self.get_detail)
        #self.file_excel.bind('<3>',self.show_detail)
        
        
        
        self.file_excel.column('序号',width=50,anchor='center')
        self.file_excel.column('文件名',width=500,anchor='center')
        self.file_excel.column('总行数',width=80,anchor='center')
        self.file_excel.column('代码行数',width=80,anchor='center')
        self.file_excel.column('注释行数',width=80,anchor='center')
        self.file_excel.column('空白行数',width=80,anchor='center')
        self.file_excel.column('注释率',width=80,anchor='center')
        
        self.file_excel.heading('序号',text='序号')
        self.file_excel.heading('文件名',text='文件名')
        self.file_excel.heading('总行数',text='总行数')
        self.file_excel.heading('代码行数',text='代码行数')
        self.file_excel.heading('注释行数',text='注释行数')
        self.file_excel.heading('空白行数',text='空白行数')
        self.file_excel.heading('注释率',text='注释率')

        
        #for item in head_str:
            #self.file_excel.column(item, width = 100)
           # self.file_excel.heading(item, text = item)
        self.file_excel.pack()


#######################结果统计#################################
    def show_summary(self):
        self.summary_frame = Frame(self.root)
        self.summary_frame.pack(fill = X, padx = 10, pady = 5)
        
        
        self.summary_entry_var = {}
        self.summary_entry = {}
        for item in summary_str:
            Label(self.summary_frame, text = item,).pack(side = LEFT)
            self.summary_entry_var[item] = StringVar()
            self.summary_entry[item] = Entry(self.summary_frame, textvariable = self.summary_entry_var[item], width = 10)
            self.summary_entry[item].pack(side = LEFT, padx = 3, pady = 3)

   
    def launch(self):
        self.select_path()
        self.select_file_type()
        self.file_detail()
        self.show_summary()
        self.root.mainloop()


if __name__ == '__main__':
    mCa = Ca.Cacu()
    mUi = UI()
    mUi.launch()
    

    


    
    
    
    
    
