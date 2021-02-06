#########################################
## 카카오톡pc 1~2 편 + 크롤링 + 스케줄러 ##
#########################################

import time, win32con, win32api, win32gui
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler


# # 카톡창 이름, (활성화 상태의 열려있는 창)
kakao_opentalk_name = '메모장'


# # 채팅방에 메시지 전송
def kakao_sendtext(chatroom_name, text):
    # # 핸들 _ 채팅방
    hwndMain = win32gui.FindWindow( None, chatroom_name)
    hwndEdit = win32gui.FindWindowEx( hwndMain, None, "RichEdit20W", None)

    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
    SendReturn(hwndEdit)


# # 엔터
def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)


# # 채팅방 열기
def open_chatroom(chatroom_name):
    # # # 채팅방 목록 검색하는 Edit (채팅방이 열려있지 않아도 전송 가능하기 위하여)
    hwndkakao = win32gui.FindWindow(None, "카카오톡")
    hwndkakao_edit1 = win32gui.FindWindowEx( hwndkakao, None, "EVA_ChildWindow", None)
    hwndkakao_edit2_1 = win32gui.FindWindowEx( hwndkakao_edit1, None, "EVA_Window", None)
    hwndkakao_edit2_2 = win32gui.FindWindowEx( hwndkakao_edit1, hwndkakao_edit2_1, "EVA_Window", None)
    hwndkakao_edit3 = win32gui.FindWindowEx( hwndkakao_edit2_2, None, "Edit", None)

    # # Edit에 검색 _ 입력되어있는 텍스트가 있어도 덮어쓰기됨
    win32api.SendMessage(hwndkakao_edit3, win32con.WM_SETTEXT, 0, chatroom_name)
    time.sleep(1)   # 안정성 위해 필요
    SendReturn(hwndkakao_edit3)
    time.sleep(1)


# # 네이버 실검 상위 20개, 리턴
def naver_realtimeList():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    url = 'https://datalab.naver.com/keyword/realtimeList.naver?where=main'
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.findAll('span','item_title')

    a = []
    for item in data:
        a.append(item.get_text())

    s = "\n".join(a)
    return s


# # 스케줄러 job_1
def job_1():
    p_time_ymd_hms = \
        f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday} / " \
        f"{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}"

    open_chatroom(kakao_opentalk_name)  # 채팅방 열기
    realtimeList = naver_realtimeList()  # 네이버 실시간 검색어 상위 20개
    kakao_sendtext(kakao_opentalk_name, f"{p_time_ymd_hms}\n{realtimeList}")  # 메시지 전송, time/실검



def main():
    sched = BackgroundScheduler()
    sched.start()

    # # 매 분 5초마다 job_1 실행
    sched.add_job(job_1, 'cron', second='*/5', id="test_1")

    count = 0
    while True:
        print("실행중.................")
        if count == 8:
            break
        time.sleep(1)


if __name__ == '__main__':
    main()