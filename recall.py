import os
import itchat
from itchat.content import *
import re
import time
import shutil

msg_dict={}
def ClearTimeOutMsg():
    if msg_dict.__len__()>0:
        for msgid in list(msg_dict):
            if time.time()-msg_dict.get(msgid,None)['msg_time']>130:
                item=msg_dict.pop(msgid)
                if item['type'] == "Picture" \
                        or item['type'] == "Recording" \
                        or item['type'] == "Video" \
                        or item['type'] == "Attachment":
                    print("要删除的文件：", item['msg_content'])
                    os.remove(item['msg_content'])

@itchat.msg_register([TEXT,PICTURE,MAP,CARD,SHARING,RECORDING,ATTACHMENT,VIDEO,FRIENDS])
def Revocation(msg):
    mytime=time.localtime()
    msg_time_touser=mytime.tm_year.__str__()+"/"+mytime.tm_mon.__str__()+"/"+mytime.tm_mday.__str__()+"/"+mytime.tm_hour.__str__()+":"+mytime.tm_min.__str__()+":"+mytime.tm_sec.__str__()
    msg_id=msg['MsgId']
    msg_time=msg['CreateTime']
    msg_from=itchat.search_friends(userName=msg['FromUserName'])['NickName']
    type=msg['Type']
    msg_content=None
    msg_url=None
    if msg['Type']=='Text':
        msg_content=msg['Text']
    elif msg['Type']=='Picture':
        msg_content=msg['FileName']
        msg['Text'](msg['FileName'])
    elif msg['Type']=='Card':
        msg_content=msg['Revommendinfo']['NickName']+'的名片'
    msg_dict.update(
        {msg_id:{"msg_from":msg_from,
                 "msg_time":msg_time,
                 "msg_time_touser":msg_time_touser,
                 "type":type,
                 "msg_content":msg_content,
                 "msg_url":msg_url}}
    )
    ClearTimeOutMsg()

@itchat.msg_register([NOTE])
def SaveMsg(msg):
    if not os.path.exists('./Revocation'):
        os.mkdir('./Revocation')
        if re.search(r"\<replacemsg\>\<\!\[CDATA\[.*撤回了一条消息\]\]\>\<\/replacemsg\>", msg['Content']) != None:
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
            old_msg=msg_dict.get(old_msg_id)
            # msg_send="您的的好友{}在{}撤回了一条信息{}，消息如下{}".format(old_msg.get('msg_from',None),old_msg.get('msg_touser',None)
            #                                          ,old_msg['type'],old_msg.get('msg_content',None))
            msg_send = r"您的好友：" \
                       + old_msg.get('msg_from', None) \
                       + r" 在 [" + old_msg.get('msg_time_touser',None) \
                       + r"], 撤回了一条 [" + old_msg[ 'msg_type'] + "] 消息, 内容如下:" \
                       + old_msg.get('msg_content', None)
            if old_msg['type']=='Shatring':
                msg_send="链接"+old_msg.get('msg_url',None)
            elif old_msg['type']=='Picture' or old_msg['type']=='Video' or old_msg['type']=='Attachment' or old_msg['type']=='Revording':
                msg_send+="存储在当前目录revocation中"
                shutil.move(old_msg['msg_content'],'/Revocation')
                itchat.send(msg_send,toUserName='filehelper')
            msg_dict.pop(old_msg_id)
            ClearTimeOutMsg()

if __name__=='__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()