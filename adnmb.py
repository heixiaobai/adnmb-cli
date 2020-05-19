# -*- coding:utf-8 -*-
import config
import fun
import curses
import time

# conf: 从config获取来自默认或者用户定义的配置信息
conf = config.config_info
# cont: 在运行过程中保存关于运行状态以及用于控制的信息
cont = config.control_info

# 初始化curses
# stdscr = curses.initscr()
# stdscr.keypad(True)
# curses.noecho()
# curses.cbreak()
# curses.start_color()

# TODO: 配色方案


def main(stdscr):
    # 浏览区pad，所有串内容
    pad_browse = curses.newpad(cont['pad_browse_height'], curses.COLS)
    # 信息提示栏pad，各类信息提示，譬如报错或者loading
    pad_info = curses.newpad(cont['pad_info_height'], curses.COLS)
    # 控制区pad，捕获用户输入，提示当前所在位置
    pad_control = curses.newpad(cont['pad_control_height'], curses.COLS)
    # 配色方案颜色初始化
    fun.init_pair_color()
    # c = config.color_info[0]
    # for i in c.keys():
    #     curses.init_pair(int(i), c[i][0], c[i][1])

    fun.stdscr_pad(stdscr, pad_browse, pad_info, pad_control)
    fun.forum('-1')
    fun.pad_control_update()
    fun.cont['back_list'].append(fun.cont['location'][:])

    # pad_info.addstr(0,0,"test",2097153)
    # curses.init_pair(1, 1, 0)
    # curses.init_pair(100, 7, 0)
    p = curses.color_pair
    # fun.test()
    # a = str(p(2))
    # a = str(curses.COLOR_RED)
    c = config.color_info[1]
    x = p(c["admin_id"])
    pad_info.addstr(0, 0, "a", x + curses.A_BOLD)
    pad_info.refresh(0, 0, curses.LINES - 2, 0, curses.LINES - 2, curses.COLS - 1)

    # fun.pad_info_print("test")

    # 开始捕获用户输入
    while True:
        fun.cont['input_command_info'], fun.cont['input_command_char'] = "", []
        fun.pad_control_update()
        cc = pad_control.getch()

        if cc == curses.KEY_DOWN:
            # 向下浏览
            fun.page_down()
        elif cc == curses.KEY_UP:
            # 向上浏览
            fun.page_up()
        elif cc == ord('f'):
            # 输入串版块列表
            fun.cont['back_list'].append(fun.cont['location'][:])
            fun.print_forum_list()
            fun.cont['location_text'] = "版块列表"
            # 捕获用户输入，根据fid访问指定版块
            fun.control_visit("forum")
            fun.cont['back_list'].append(fun.cont['location'][:])
        elif cc == ord('t'):
            # 捕获用户输入，根据tid访问指定串
            fun.control_visit("thread")
            fun.cont['back_list'].append(fun.cont['location'][:])
        elif cc == ord('g'):
            # 捕获用户输入，根据序号访问指定串
            fun.go_thread()
            fun.cont['back_list'].append(fun.cont['location'][:])
        elif cc == ord('n'):
            # 浏览下一页
            fun.next_page()
        elif cc == ord('u'):
            # 浏览上一页
            fun.previous_page()
        elif cc == ord('h'):
            # 打印home(help)
            with open("./home.txt", "r") as f:
                fun.pad_browse_print(f.read())
        elif cc == ord('b'):
            # 返回上一层
            fun.back()
        elif cc == ord('q'):
            # 退出循环
            break


curses.wrapper(main)

# 退出程序
# fun.curses_end()

# TODO: 进度 - 配色方案
