import os
from datetime import datetime

import pytz

from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *


# load environment virables 从.env文件中载入环境变量
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p CST"

# Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app, rt = fast_app(
    # 为应用添加fav图标
    hdrs=(Link(rel="icon", type="assets/x-icon", href="/assets/favicon.png"),),)


def get_time():
    # cet_tz = pytz.timezone("CET") # CET 欧洲中部时间
    tz = pytz.timezone("Asia/Shanghai") # 上海时间
    return datetime.now(tz)


def add_message(name, message):
    timestamp = get_time().strftime(TIMESTAMP_FMT)
    supabase.table("MyGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def delete_message(id):
    supabase.table("MyGuestbook").delete().eq("id", id).execute()

def get_messages():
    # sort by 'id' in descending order to get the latest entries first
    response = supabase.table("MyGuestbook").select(
        "*").order("id", desc=True).execute()
    return response.data


def render_message(entry):
    return Article(
        Header(f"姓名:{entry['name']}",Button("➖",hx_delete=f"/delete-message/{entry['id']}",hx_target="#message-list",hx_swap="outerHTML",hx_confirm="确定要删除吗？")),
        P(entry['message']),
        Footer(Small(Em(f"时间:{entry['timestamp']}")))
    )


def render_message_list():
    # 测试数据
    # messages = [
    #     {"name": "Peter", "message": "Hi there", "timestamp": "now"},
    #     {"name": "Jack", "message": "Hi there", "timestamp": "yesterday"},
    #     {"name": "Jerry", "message": "Hi there", "timestamp": "5 min"},
    # ]
    messages = get_messages()
    return Div(
        *[render_message(entry) for entry in messages],
        id="message-list"
    )


def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxLength=MAX_NAME_CHAR
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxLength=MAX_MESSAGE_CHAR
            ),
            Button("➕", type="submit"),
            role="group"
        ),
        method="post", 
        hx_post="/submit-message", # POST 请求提交到 /submit-message 路由
        hx_target="#message-list", # 更新 message-list 元素
        hx_swap="outerHTML", # 使用 outerHTML 交换内容,替换整个元素
        hx_on__after_request="this.reset()" # 请求完成后重置表单
    )
    return Div(
        P(Em("写点什么吧！")), # Em 斜体，强调（emphasize）
        form,
        Div(
            "Made with 💖 by ",
            A("Jerry", href="https://youtube.com/@codingisfun", target="_blank")
        ),
        Hr(),
        render_message_list()
    )


@rt('/')
def get(): return Titled("我的留言本 😊", render_content())


@rt('/submit-message')
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()


@rt('/delete-message/{id}')
def delete(id: int):
    delete_message(id)
    return render_message_list()

serve()
