from enum import Enum

class DataType(Enum):
    image_s_to_c=0
    image_c_to_s=3
    audio_s_to_c=1
    audio_c_to_s=4
    login_s_to_c=2
    login_c_to_s=5
    meetingid_s_to_c=6
    meetingid_c_to_s=7
    meetinfo_s_to_c=8
    meetinfo_c_to_s=9
    videorequest_s_to_c=10
    videorequest_c_to_s=11
    add_member_s_to_c=12
    del_member_s_to_c=13
    msg_s_to_c=14
    msg_c_to_s=15
    diff_image_c_to_s=16
    diff_image_s_to_c=17
    quitmeet_c_to_s=18
    memberquit_s_to_c=19
    endmeet_c_to_s=20
    endmeet_s_to_c=21
    membercamera_c_to_s=22
    membercamera_s_to_c=23
    membermicrophone_c_to_s=24
    membermicrophone_s_to_c=25
    allmute_c_to_s=26
    allmute_s_to_c=27
    unallmute_c_to_s=28
    unallmute_s_to_c=29
    register_c_to_s=30
    register_s_to_c=31
    existMeeting_c_to_s=32
    existMeeting_s_to_c=33
    changename_c_to_s=34
    changename_s_to_c=35
    changepwd_c_to_s=36
    changepwd_s_to_c=37
    handup_c_to_s=38
    handdown_c_to_s=39
    handuplist_s_to_c=40


