import re
import curses
import config
import time
import api
# 自定义的所有函数

# conf: 从config获取来自默认或者用户定义的配置信息
conf = config.config_info
# cont: 在运行过程中保存关于运行状态以及用于控制的信息
cont = config.control_info
# 全局使用，当前所访问版块的全部内容
thread_list = {}
# 全局使用，当前所访问的串的全部内容
post_list = {}
# TODO:注释
cont['browse_now_list'] = 0
# TODO: 需要把自定义版块，目前为直接获取
forum_list = api.get_forum_list('adnmb')

ss = pad_b = pad_i = pad_c = None


def curses_end():
    ss.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


def stdscr_pad(stdscr: object, pad_browse: object, pad_info: object, pad_control: object):
    """
    传入stdscr和3个pad对象，供所有函数操作
    """
    global ss, pad_b, pad_i, pad_c
    ss = stdscr
    pad_b = pad_browse
    pad_i = pad_info
    pad_c = pad_control


def pad_browse_print(text: str):
    """
    向浏览区pad输出内容
    :param text: 文本内容
    """
    pad_b.clear()
    pad_b.addstr(0, 0, text)
    pad_b.refresh(0, 0, 0, 0, curses.LINES - 3, curses.COLS - 1)


def pad_info_print(text: str):
    """
    向信息提示栏输出内容
    :param text: 文本内容，显示长度应不大于终端宽度
    """
    pad_i.clear()
    pad_i.addstr(0, 0, text)
    y = curses.LINES - 2
    pad_i.refresh(0, 0, y, 0, y, curses.COLS - 1)


def init_pair_color():
    """
    根据配色方案定义的颜色初始化颜色，需要在终端初始化之后再运行
    """
    c = config.color_info[0]
    for i in c.keys():
        curses.init_pair(int(i), c[i][0], c[i][1])


def id_color(admin: str, user_id: str = None, po_id: str = None) -> int:
    """
    从配色方案定义id的颜色标识(curses颜色标识通过bit位组合)
    :param admin: 是否红名标识符
    :param user_id: post的用户id
    :param po_id: po主的id
    :return: curses的颜色标识符
    """
    # TODO: Po id的颜色定义
    c0 = config.color_info[0]
    c1 = config.color_info[1]
    color_code = 0
    if admin == '1':
        color_code = curses.color_pair(c1["admin_id"]) + c0[str(c1["admin_id"])][2]
        if user_id == po_id:
            color_code = curses.color_pair(c1["admin_po_id"]) + c0[str(c1["admin_po_id"])][2]
    elif user_id == po_id:
        color_code = curses.color_pair(c1["po_id"]) + c0[str(c1["po_id"])][2]
    return color_code


def show_time(post_time: str) -> str:
    """
    把从Api获取到的时间格式转为自定义的格式
    :param post_time: 从api的json获取到的原时间
    :return: 自定义事件格式
    """
    timestamp_int = int(
        time.mktime(time.strptime(re.sub(r"\(.*\)", " ", post_time), "%Y-%m-%d %H:%M:%S")))
    return time.strftime(conf['time_format'], time.localtime(timestamp_int))


def content_process(text: str) -> str:
    """
    简单处理掉一些不必要的内容
    <br />, \r
    :param text:
    :return:
    """
    text = re.sub(r"<br />|\r", "", text)
    # data = ""
    # n = 0
    # for i in text:
    #     if i == "\n":
    #         n += 1
    #     if n == config_info['thread_content_line']:
    #         break
    #     data += i
    return text


def forum_data_process(data: list, page: int):
    """
    处理从API获取到的版块串列表，以page为key存储到thread_list中
    :param data: 从api获取的json
    :param page: 页数
    """
    global thread_list
    thread_list[str(page)] = []
    """
    数据说明：
    id: 串号
    userid: po的饼干
    f_name: 版块名 
    now: 自定义格式化之后的事件
    content: 串内容
    rC: 串回复数量
    """
    for i in range(len(data)):
        d = data[i]
        thread_list[str(page)].append(
            {
                'id': [d['id'], 0],
                'userid': [d['userid'], id_color(d['userid'], d['admin'])],
                'f_name': ['', 0],
                'now': [show_time(d['now']), 0],
                'content': [content_process(d['content']), 0],
                'rC': [d['replyCount'], 0]
            }
        )
    if 'fid' in data[1].keys():
        for i in range(len(data)):
            thread_list[str(page)][i]['f_name'] = [forum_list[data[i]['fid']], 0]


def thread_data_process(data: dict, page: int = 1):
    """
    处理从API获取到的串回复列表，以page为key存储到post_list中
    """
    global post_list
    # 存储(串号，饼干等……)时为list，[内容，配色]
    c = config.color_info[1]
    p = curses.color_pair
    post_list[str(page)] = []

    # 将串基本信息对应id存储
    post_list['po_id'] = data['userid']
    post_list['tid'] = data['id']
    post_list['fid'] = data['fid']
    post_list['rC'] = data['replyCount']
    if page == 1:
        post_list[str(page)].append({
            'id': [data['id'], p(c["post_id"])],
            'userid': [data['userid'], id_color(data['admin'], data['userid'], data['userid'])],
            'now': [show_time(data['now']), p(c["time"])],
            'content': [data['content'], p(c["content"])]
        })
    data = data['replys']
    for i in range(len(data)):
        d = data[i]
        post_list[str(page)].append(
            {
                'id': [str(d['id']), p(c["post_id"])],
                'userid': [d['userid'], id_color(d['admin'], d['userid'], post_list['po_id'])],
                'now': [show_time(d['now']), p(c["time"])],
                'content': [d['content'], p(c["content"])]
            }
        )


def pad_browse_update(v_type: str, page: int):
    """
    从全局变量thread_list或post_list更新浏览区
    :param v_type: forum, thread
    :param page: 页数
    """
    pad_b.move(0, 0)
    data = None
    global thread_list, post_list, cont
    if v_type == 'forum':
        data = thread_list[str(page)]
    elif v_type == 'thread':
        data = post_list[str(page)]
    pad_b.clear()
    for i in range(len(data)):
        # 串信息：序号 串号 饼干 回复数 版块名
        y = pad_b.getyx()[0]
        pi = conf['theme']
        d = data[i]

        pad_b.addstr("[" + str(i) + "]")
        pad_b.move(y, pi[0])
        pad_b.addstr(d['userid'][0], d['userid'][1])
        pad_b.move(y, pi[1])
        pad_b.addstr("No." + d['id'][0], d['id'][1])
        if v_type == 'forum':
            pad_b.move(y, pi[2])
            pad_b.addstr("[" + d['rC'][0] + "]", d['rC'][1])
            pad_b.move(y, pi[3])
        pad_b.move(y + 1, 0)

        # 串内容
        pad_b.addstr(d['content'][0], d['content'][1])
        pad_b.move(pad_b.getyx()[0] + 1, 0)
        pad_b.addstr("-" * int(curses.COLS / 3), 0)
        pad_b.move(pad_b.getyx()[0] + 2, 0)
    cont['browse_now_line'] = 0
    cont['browse_end_line'] = pad_b.getyx()[0] - 2
    pad_b.refresh(0, 0, 0, 0, curses.LINES - 3, curses.COLS - 1)


def forum(fid: str, page: int = 1):
    """
    访问指定版块
    :param fid: 指定版块id
    :param page: 指定页数
    """
    global cont
    cont['now_page'] = page
    r = api.get_showf(fid, page)
    if type(r.json()) is list:
        cont['input_command_info'] = ""
        forum_data_process(r.json(), page)
        pad_browse_update('forum', page)
        t = 'location'
        cont[t][0], cont[t][1], cont[t][3], cont['location_text'] = \
            "forum", fid, page, forum_list[fid]
        # pad_info_print(cont['location'][1])
    else:
        pad_info_print(r.json())


def thread(tid: str, page: int = 1):
    """
    访问指定串
    :param tid: 指定串号
    :param page: 指定页数
    """
    global cont
    cont['now_page'] = page
    r = api.get_thread(tid, page)
    if type(r.json()) is not str:
        cont['input_command_info'] = ""
        thread_data_process(r.json(), page)
        pad_browse_update('thread', page)
        t = 'location'
        cont[t][0], cont[t][1], cont[t][2], cont[t][3], cont['location_text'] = \
            "thread", post_list['fid'], tid, page, forum_list[r.json()['fid']] + "/No." + tid
        # pad_info_print(cont['back_list'][-1][2])

    else:
        pad_info_print(r.json())


def pad_control_update():
    """
    根据cont的信息更新控制栏pad
    """
    icc = ""
    for i in cont['input_command_char']:
        icc += i
    pad_c.clear()
    pad_c.move(0, 0)
    pad_c.addstr(0, 0, conf['command_char'])
    pad_c.addstr(0, 20, cont['location_text'])
    pad_c.addstr(0, 2, cont['input_command_info'])
    pad_c.addstr(0, 8, icc)
    if cont['input_command_info'] == "" and icc == "":
        pad_c.move(0, 2)
    pad_c.refresh(0, 0, curses.LINES - 1, 0, curses.LINES - 1, curses.COLS - 1)


def print_forum_list():
    """
    打印版块列表
    """
    pad_b.clear()
    pad_b.move(0, 0)
    cols_count = 0
    cont['location'][0] = "forum_list"
    for i in forum_list.keys():
        pad_b.addstr(i + (5 - len(i)) * " " + forum_list[i], 0)
        cols_count += 18
        if (curses.COLS - cols_count) > 18:
            pad_b.move(pad_b.getyx()[0], cols_count)
            pad_b.addstr("|")
        else:
            pad_b.move(pad_b.getyx()[0] + 1, 0)
            cols_count = 0
    pad_b.refresh(0, 0, 0, 0, curses.LINES - 3, curses.COLS - 1)


def control_visit(v_type: str):
    """
    访问版块或串号，调用后从pad_c捕获用户键盘输入
    :param v_type: forum/thread
    """
    global cont
    cont['input_command_char'] = []
    if v_type == 'forum':
        cont['input_command_info'] = "版号："
        char_max_len = 4
        char_ord_list = [45] + list(range(48, 58))
    elif v_type == "thread":
        cont['input_command_info'] = "串号："
        char_max_len = 8
        char_ord_list = list(range(48, 58))

    pad_control_update()
    while True:
        cc = pad_c.getch()
        if cc in char_ord_list and len(cont['input_command_char']) <= char_max_len:
            # 符合限制规则且已输入内容不超过最大长度
            cont['input_command_char'].append(chr(cc))
            pad_control_update()
        elif (cc == 127 or cc == 263) and cont['input_command_char']:
            # Backspace/退格键
            cont['input_command_char'].pop()
            pad_control_update()
        elif cc == 10 and cont['input_command_char']:
            # Enter/回车键
            tmp = ""
            for i in cont['input_command_char']:
                tmp += i
            if v_type == "forum":
                forum(tmp)
            elif v_type == "thread":
                thread(tmp)
            break
        elif cc == ord('q'):
            break


def go_thread():
    """
    访问指定串，根据pad_browse_update()提示的序号
    """
    global cont
    cont['input_command_char'] = []
    cont['input_command_info'] = "序号: "
    pad_control_update()

    while True:
        cc = pad_c.getch()
        if cc in list(range(45, 58)) and len(cont['input_command_char']) <= 2:
            # 符合限制规则且长度不大于2
            cont['input_command_char'].append(chr(cc))
            pad_control_update()
        elif (cc == 127 or cc == 263) and cont['input_command_char']:
            # Backspace/退格键
            cont['input_command_char'].pop()
            pad_control_update()
        elif cc == 10 and cont['input_command_char']:
            # Enter/回车键
            tmp = ""
            for i in cont['input_command_char']:
                tmp += i
            tmp = thread_list[str(cont['now_page'])][int(tmp)]['id'][0]
            thread(tmp)
            break
        elif cc == ord('q'):
            curses_end()


def page_down():
    """
    使pad_b向下翻页，一次翻10行
    TODO: 后期加入自定义行数或者翻页半屏/全屏
    """
    global cont
    i = cont['browse_end_line'] - (curses.LINES - 3)
    j = i - cont['browse_now_line']
    if j >= 10:
        cont['browse_now_line'] += 10
    elif j > 0:
        cont['browse_now_line'] += j
    pad_b.refresh(cont['browse_now_line'], 0, 0, 0, curses.LINES - 3, curses.COLS - 1)


def page_up():
    """
    使pad_b向上翻页，一次10行
    TODO: 后期尝试将page_down和page_up合并
    """
    global cont
    i = cont['browse_now_line']
    if i >= 10:
        cont['browse_now_line'] -= 10
    elif 0 < i < 10:
        cont['browse_now_line'] -= i
    pad_b.refresh(cont['browse_now_line'], 0, 0, 0, curses.LINES - 3, curses.COLS - 1)


def next_page():
    """
    访问版块的下一页
    """
    global cont
    if cont['location'][0] == "forum":
        cont['now_page'] += 1
        forum(cont['location'][1], cont['now_page'])
    elif cont['location'][0] == "thread":
        # 判断访问的页数是否大于串页数，从串回复数量计算
        x = int(post_list['rC'])
        n = (int(x / 18) if (x % 18 == 0) else int(x / 18) + 1)
        if cont['now_page'] < n:
            cont['now_page'] += 1
            thread(cont['location'][2], cont['now_page'])


def previous_page():
    """
    访问版块或串的上一页
    """
    global cont
    if cont['location'][0] == "forum" and cont['now_page'] > 0:
        cont['now_page'] -= 1
        forum(cont['location'][1], cont['now_page'])
    elif cont['location'][0] == "thread" and cont['now_page'] > 0:
        cont['now_page'] -= 1
        thread(cont['location'][2], cont['now_page'])


def back():
    bl = cont['back_list']
    if len(bl) > 1:
        if bl[-2][0] is not None:
            # pad_info_print(str(bl[-1][2]))
            if bl[-2][0] == "forum":
                # pad_info_print("a")
                forum(bl[-2][1])
                cont['back_list'].pop()
            elif bl[-2][0] == "thread":
                # pad_info_print("b")
                thread(bl[-2][2])
                cont['back_list'].pop()

            elif bl[-2][0] == "forum_list":
                print_forum_list()

