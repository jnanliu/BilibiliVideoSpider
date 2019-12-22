# -*- coding: utf-8 -*-
import os
from moviepy.editor import *
import natsort

def VideoCat(dirname, SavePath) :

    '''
    combine videos
    '''
    files = os.listdir(dirname)
    files = natsort.natsorted(files)
    videos, videoPaths = [], []
    for file in files :

        videoPaths.append(os.path.join(dirname, file))
        video = VideoFileClip(os.path.join(dirname, file))
        videos.append(video)

    finall_video = concatenate_videoclips(videos)
    finall_video.to_videofile(SavePath, fps=24, remove_temp=True, progress_bar=False)
    for path in videoPaths :
        try :
            os.remove(path)
        except :
            pass