import argparse
import sys
from pytube import (
    YouTube,
    Playlist,
    helpers
) #versi 12.0.0
import traceback

from youtube_transcript_api import YouTubeTranscriptApi as subtitle
from .common import (
    Dir as dir,
    Msg as msg,
    make_dir,
    get_playlist_id,
    get_video_id,
    get_input_url,
    args_valid,
    is_watch,
    is_file_lists,
    unpack_file_list,
    is_playlist,
    set_download_save,
    save_srt,
    datetime_now,
    set_url_yt
)
class DVS:
    """Download Video dan Subtitle Youtube
    """
    def __init__(self) -> None:        
        self.dir_lists = [dir.downloads,
                     dir.url_lists
        ]
        for i in self.dir_lists :
            make_dir([i])        
        self.url_lists = []
    
    
    def start_input(self)-> None:
        """Masukan url seperti berikut :
        url : positional [v][s]
        positional arguments :
            url                url youtube /watch atau /playlist satu atau berulang
            end                untuk mengkahiri atau keluar dari input dan mendownload
            exit               keluar dari aplikasi tanpa download

        optional arguments :
           (default)          download video dan subtitle
            v                 download video saja
            s                 download subtitle saja            
        """
        print(str(self.__doc__))
        if len(sys.argv) > 1 :
            print(str(self.input_arg.__doc__) +'\n')
            self.input_arg()
        else:
            print(str(self.input_url.__doc__))
            self.input_url()    
    
    def input_arg(self)-> None :
        """$ python -m dvsyoutube ["url".. [v][s]] [file.list]"""
        cli = argparse.ArgumentParser(
                       prog='python -m ' + __name__.split('.')[0],                       
                       description=self.__doc__,
                       epilog='akhir')
        cli.add_argument(
            'url',
            nargs='*',
            type= str,
            help='url youtube /watch atau /playlist satu atau lebih'
        )
        args = cli.parse_args()
        print(args.url)   
        
        # Jika argument adalah file
        if is_file_lists([dir.url_lists, args.url[0]]):
            arg_cmd = unpack_file_list([self.dir_lists[1], args.url[0]])
            for url_cmd in arg_cmd :
                if is_playlist(url_cmd) :
                    watch_cmd = self._unpack_playlist(url_cmd)
                    for v_cmd in watch_cmd :
                        self._set_lists(v_cmd)
                    continue
                if is_watch(url_cmd) :                      
                    self._set_lists(url_cmd)
        else:
            # jika argument adalah input url
            cmd = args.url[-1]
            if cmd in ['v','s']:
                
                for url in args.url[:-1]:
                    url_cmd = url + ' ' + cmd
                    print(url_cmd)
                    if is_playlist(url_cmd) :
                        watch_cmd = self._unpack_playlist(url_cmd)
                        print(watch_cmd)
                        for v_cmd in watch_cmd :
                            self._set_lists(v_cmd)                
                    if is_watch(url_cmd) :                      
                        self._set_lists(url_cmd)
            else:
                for url in args.url:
                    url_cmd = url + ' vs'
                    if is_playlist(url_cmd) :
                        
                        watch_cmd = self._unpack_playlist(url_cmd)
                        for v_cmd in watch_cmd :
                            self._set_lists(v_cmd)                
                    if is_watch(url_cmd) :
                        
                        self._set_lists(url_cmd)
    
    # ini belum di test
    def input_url(self)->None :
        """Contoh :
        download video saja
        url : v=Video-id___ v
        url : list=playlist-id v
        url : https://www.youtube.com/watch?v=Video-id v
        url : https://www.youtube.com/watch?v=Video-id&list=playlist-id v
        url : https://www.youtube.com/playlist?list=playlist-id v

        selesai memasukan url ketik 'end' :
        url : end    
        """
        while True :
            in_cmd = input('url : ')            
            if in_cmd == "end" : break
            if in_cmd == "exit" : exit('ga di download')
            if in_cmd == '' :
                in_cmd = 'default.list'

            # Jika argument adalah file
            if is_file_lists([dir.url_lists, in_cmd]):
                arg_cmd = unpack_file_list([self.dir_lists[1], in_cmd])
                for url_cmd in arg_cmd :
                    if is_playlist(url_cmd) :
                        watch_cmd = self._unpack_playlist(url_cmd)
                        for v_cmd in watch_cmd :
                            self._set_lists(v_cmd)
                        continue
                    if is_watch(url_cmd) :                      
                        self._set_lists(url_cmd)                
                break


            #jika argument bukan file
            if len(in_cmd.split(' ')) == 1 :
                url = in_cmd
                cmd = 'vs'
            else:
                url, cmd = in_cmd.split(' ')
            
            if cmd in ['v','s']:                
                url_cmd = url + ' ' + cmd
                if is_playlist(url_cmd) :
                    watch_cmd = self._unpack_playlist(url_cmd)
                    for v_cmd in watch_cmd :
                        self._set_lists(v_cmd)                
                if is_watch(url_cmd) :                      
                    self._set_lists(url_cmd)
            else:                
                url_cmd = url + ' vs'
                if is_playlist(url_cmd) :                    
                    watch_cmd = self._unpack_playlist(url_cmd)
                    for v_cmd in watch_cmd :
                        self._set_lists(v_cmd)                
                if is_watch(url_cmd) :
                    
                    self._set_lists(url_cmd)   

    def _set_lists(self, ls_input:str=None, cmd:str='vs'):
        """List URL
        [
            {video_id:v_id, title:title, author:author, list_title:optional, cmd:"vs"}
        ]
        """
        if not args_valid(ls_input) :
            return None 
        if ls_input == None :
            return None        
        watch, cmd = get_input_url(ls_input)        
        self.url_lists.append({
            'video_id'   : get_video_id(watch),
            'title'      : self.video_title(watch),
            'author'     : self.author(watch),
            'list_title' : self.playlist_title(watch),
            'cmd'        : cmd
        })
    
    def video_title(self, url:str= None):
        if url == None :
            return None
        
        if get_video_id(url) ==  None:
            print(msg.error)
            return None
                
        url = 'https://www.youtube.com/watch?v='+get_video_id(url)
        try :
            return helpers.safe_filename(YouTube(url).title)
        except :            
            print(msg.error)
            return None

    def author(self, url:str= None):
        if url == None :
            return None
        url = 'https://www.youtube.com/watch?v='+str(get_video_id(url))
        try :
            return helpers.safe_filename(YouTube(url).author)
        except :
            return None

    def playlist_title(self,url:str=None):
        if url == None :
            return None
        
        try :
            return helpers.safe_filename(Playlist(str('https://www.youtube.com/playlist?list='+ get_playlist_id(url))).title)
        except:
            return None    

    def _unpack_playlist(self, url_cmd:str=None)-> list:
        """Unpack Playlist menjadi
        https://www.youtube.com/playlist?list=
        https://www.youtube.com/watch?v={v_id}&list={pl_id}
        """
        if not args_valid(url_cmd):
            return None
        if not is_playlist(url_cmd):
            return None
        urls, cmd = get_input_url(url_cmd)
        pl_id = get_playlist_id(urls)        
        pl = []
        print("Unpack playlist...")        
        urls = 'https://www.youtube.com/playlist?list='+ pl_id        
        for url in Playlist(urls).video_urls :            
            v_id = get_video_id(url)            
            if pl_id == None :                
                pl.append(f'https://www.youtube.com/watch?v={v_id} {cmd}')
            else:                
                pl.append(f'https://www.youtube.com/watch?v={v_id}&list={pl_id} {cmd}')
        return pl
    
    def download_video(self, video_id:str, video_title:str, list_title:str, author:str):
        url_video = set_url_yt(video_id)
        print(url_video)
        yt = YouTube(url=url_video)
        
        if list_title == None :
            path_save = set_download_save([author])
        else:
            path_save = set_download_save([author,list_title])        
                
        try :
            video = yt.streams.get_by_itag("22") # video format: 720
            if video is None :
                video = yt.streams.get_by_itag("18") # video format: 360
        except :
            print(traceback.format_exc())
            print(set_url_yt(video_id)+' '+ video_title +' '+path_save)      
    
        print("Video sedang di download...")
        #video.download(path_save)
        try :
            video.download(path_save)
            print('download video selesai')
        except:
            print(traceback.format_exc())
            print(set_url_yt(video_id) + ' '+video_title+' '+path_save)    
    
    def download_subtitle(self, video_id:str, video_title:str, list_title:str, author:str):
        fail_msg = ''
        fail_status = False
        en = []
        id = []       
        
        try :
            transcript_list = subtitle.list_transcripts(video_id)            
        except :
            if video_id == None :
                video_id = 'None'
            if video_title == None :
                video_title = 'None'
            fail_status = True
            fail_msg += str('\n' + datetime_now()+':'+str(video_id) +' : '+ str(video_title) + '\n')
            fail_msg += str(' '*(len(datetime_now())+1) + 'Subtitles are disabled for this video')
            return {'en':en, 'id': id, 'fail_saved':fail_msg, 'fail_status': fail_status}        
        
        try :
            en = transcript_list.find_manually_created_transcript(['en-GB'])            
            fail_status = False
        except:
            if video_id == None :
                video_id = 'None'
            if video_title == None :
                video_title = 'None'
            fail_status = True
            fail_msg += str('\n' + datetime_now()+':'+str(video_id) +' : '+ str(video_title) + '\n')
            fail_msg += str(' '*(len(datetime_now())+1) + "No transcripts were found for any of the requested language codes: ['en-GB']")
        
        try :
            if fail_status :
                en = transcript_list.find_generated_transcript(['en'])
            id = en.translate('id')
            fail_status = False
        except :
            fail_status = True
            fail_msg += str('\n' + datetime_now()+':'+video_id +' : '+ video_title + '\n')
            fail_msg += str(' '*(len(datetime_now())+1) + traceback.format_exc())
        
        
        for sub,f in [en, ' [en]'], [id , ' [id]'] :
            if list_title == None :
                save_srt(sub,video_title + f + '.srt', [author] )
            else:
                save_srt(sub,video_title + f + '.srt', [author, list_title] )

    def download(self):
        """List URL
        [
            {video_id:v_id, title:title, author:author, list_title:optional, cmd:"vs"}
        ]
        """
        for ls in self.url_lists :
            if ls['cmd'] == 'vs':
                self.download_subtitle(ls['video_id'], ls['title'], ls['list_title'], ls['author'])
                self.download_video(video_id=ls['video_id'],
                                    video_title=ls['title'],
                                    list_title=ls['list_title'],
                                    author=ls['author'])
            if ls['cmd'] == 'v' :                
                self.download_video(video_id=ls['video_id'],
                                    video_title=ls['title'],
                                    list_title=ls['list_title'],
                                    author=ls['author'])
            if ls['cmd'] == 's' :
                self.download_subtitle(ls['video_id'], ls['title'], ls['list_title'], ls['author'])

def main():
    vs = DVS()
    vs.start_input()
    for url in vs.url_lists:
        print(url)
    vs.download()