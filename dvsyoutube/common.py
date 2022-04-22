from asyncore import read
import re
import os
import sys
import argparse
import datetime

class Dir :
    root = os.getcwd() # /dvs_youtube
    downloads = 'Downloads'
    url_lists = 'url_lists'
    log = 'Log'
#root = os.path.dirname(__file__) # /dvs_youtube/dvsyoutube
class Msg :
    not_valid =  'url tidak valid silahkan coba lagi'
    error = 'error'
    error_regex = 'error regex'
    nolist = 'Parameter Bukan list'
    nostr = 'Parameter Bukan string'
    nosrt = 'tidak ada list srt'


def make_dir(ls_dir:list=None):    
    if not isinstance(ls_dir, list):
        print(Msg.nolist)
        return False
    if not os.path.exists(os.path.join(Dir.root, *ls_dir)):
        os.makedirs(os.path.join(Dir.root, *ls_dir), exist_ok=True)
    return True

def get_video_id(url: str) -> str:
    """
    'https://www.youtube.com/watch?v=RPFSN32VzKA',
    'https://www.youtube.com/watch?v=4g9EGxFnjHY&list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G',
    'https://youtu.be/4g9EGxFnjHY',
    'https://www.youtube.com/embed/4g9EGxFnjHY',
    'watch=RPFSN32VzKA',
    'v=RPFSN32VzKA',
    'watch?v=4g9EGxFnjHY&list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G'
    """
    
    pattern = r"(?:v=|\/|watch=)([0-9A-Za-z_-]{9,11})"
    try :
        return re.search(pattern, url).group(1)
    except:
        print('in get_video_id : ' + Msg.error_regex)
        return None

def get_playlist_id(url: str) -> str:
    """
    'https://www.youtube.com/watch?v=4g9EGxFnjHY&list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G
    'https://www.youtube.com/playlist?list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G
    'https://youtu.be/4g9EGxFnjHY
    'https://www.youtube.com/embed/4g9EGxFnjHY
    'watch=RPFSN32VzKA
    'v=RPFSN32VzKA
    'watch?v=4g9EGxFnjHY&list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G
    'list=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G
    'playlist=PL-Ma8acvjwYARCtk0GEJlrfMa-O7Bf87G    
    """

    pattern = r"(?:list=)([0-9A-Za-z_-]{30,35})"
    try :
        return re.search(pattern, url).group(1)
    except:
        return None

def args_valid(arg:str)-> bool :
    pattern = r"^https|^watch|^v=|^list|^playlist"
    try :
        if re.search(pattern, arg) :
            return True
    except:
        print(Msg.error)
        return False

def get_input_url(in_cmd:str=None):
    if not args_valid(in_cmd):
        return None , None

    arg = in_cmd.split(' ')[0]
    if len(in_cmd.split(' ')) >= 2 :
        cmd = in_cmd.split(' ')[1]
    else :
        cmd = 'vs'
    return arg, cmd

def is_file_lists(dir_list:list=None):    
    filepath = os.path.join(Dir.root,*dir_list)
    if os.path.exists(filepath) :
        return True
    return False

def unpack_file_list(pathfile:list = None)->list:
    txt_ls = []    
    if os.path.isfile(os.path.join(Dir.root,*pathfile)):
        with open(os.path.join(Dir.root,*pathfile)) as f :
            txt = f.read().split('\n')
    
    for t in txt :
        if args_valid(t):
            txt_ls.append(t)    
    return txt_ls

def is_watch(url:str= None):
    pattern = r"watch|v=|youtu|embed"
    try :
        if re.search(pattern, url) :
            return True
    except:
        print(Msg.error)
        return False

        
def is_playlist(url:str=None):
    pattern = r"^list|^playlist|playlist"
    try :
        if re.search(pattern, url) :
            return True
    except:
        print(Msg.error)
        return False

def set_download_save(path_save:list):
    if not isinstance(path_save, list):
        print(Msg.nolist)
        return False
    make_dir([Dir.downloads]+path_save)
    return str(os.path.join(Dir.root,Dir.downloads, *path_save))

def save_srt(srt, filename, path_save:list):
    make_dir([Dir.downloads]+path_save)
    filepath = os.path.join(Dir.root,Dir.downloads,*path_save, filename)
    
    with open(filepath, "w") as f :# overwrite
        f.write(srt_format(srt))

    print('file sudah disimpan')

def srt_format(caption:list):
    # srt format :
    # =============================
    # 1                             <--- seq number
    # 00:00:00,000 --> 00:00:00,000 <--- format time hh:mm:ss,fff
    # Caption text                  <--- text subtitle
    #                               <--- blank
    # =============================
    if caption == [] :
        print(Msg.nosrt)
        return 'None'
    t = caption.fetch()
    #print(t)
    text = ''#'1\n'+time_srt(t[0]['start'],t[1]['start'])+'\n'+t[0]['text']
    for j in range(len(t)):
        #j += 1
        text += str(j+1)+'\n'
        if j < len(t)-1 :
            text += time_srt(t[j]['start'], t[j+1]['start']) + '\n'
            #continue
        else :
            text += time_srt(t[j]['start'], t[j]['duration'], True) + '\n'
        text += str(t[j]['text'])+ '\n\n'
    return text

def time_srt(sec, next, add = False) :
    if sec == 0.0 :
        start = '00:00:00,000'
    else:
        start = str(datetime.timedelta(seconds=sec))[:-3].replace('.', ',')

    if add :
        end = str(datetime.timedelta(seconds=(sec+next)))[:-3].replace('.', ',')
    else:
        end = str(datetime.timedelta(seconds=next))[:-3].replace('.', ',')
    return str(start + " --> "+ end)

def datetime_now():
    return str(datetime.datetime.now())

def set_url_yt(id:str=None):
        """https://www.youtube.com/watch?v=video-id__"""
        if not isinstance(id, str):
            return None
        url_yt = 'https://www.youtube.com/watch?v='
        return url_yt+id
