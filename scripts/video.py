#!/usr/bin/env python3
import pathlib,subprocess,shutil,os,sys
imgdir=pathlib.Path('media/screenshots')
shots=[imgdir/f'{n}.png' for n in ('login','mountains','earth-3d')]
for x in shots:
    if not x.exists(): raise SystemExit('Missing screenshot: '+str(x))
voice=pathlib.Path('media/tmp/narration.mp3');voice.parent.mkdir(parents=True,exist_ok=True)
text=pathlib.Path('scripts/narration.txt').read_text().strip()
# Microsoft Edge neural TTS, if available. Network required; audio remains local.
if shutil.which('edge-tts'):
    subprocess.run(['edge-tts','--voice',os.getenv('WORLDFORGE_VOICE','en-US-GuyNeural'),'--rate=-8%','--text',text,'--write-media',str(voice)],check=True)
elif shutil.which('piper') and os.getenv('PIPER_MODEL'):
    voice=pathlib.Path('media/tmp/narration.wav')
    with voice.open('wb') as f: subprocess.run(['piper','--model',os.environ['PIPER_MODEL'],'--output_file',str(voice)],input=text,text=True,check=True,stdout=subprocess.DEVNULL)
elif shutil.which('espeak-ng'):
    voice=pathlib.Path('media/tmp/narration.wav')
    subprocess.run(['espeak-ng','-s','145','-w',str(voice),text],check=True)
else:
    print('No voice synthesizer installed; producing silent video.',file=sys.stderr)
    voice=None
if not shutil.which('ffmpeg'):raise SystemExit('Install ffmpeg first')
video=pathlib.Path('media/demo.mp4');video.parent.mkdir(exist_ok=True)
# Reliable slideshow encoder: 14-second clips, 1280x720, H.264, yuv420p.
clips=[]
for i,shot in enumerate(shots):
    clip=pathlib.Path(f'media/tmp/part{i}.mp4');clips.append(clip)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-i',str(shot),'-t','14','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p','-r','24','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(clip)],check=True)
concat=pathlib.Path('media/tmp/concat.txt');concat.write_text(''.join(f"file '{p.resolve()}'\n" for p in clips))
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat)]
if voice:cmd+=['-i',str(voice),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k','-shortest']
else:cmd+=['-an']
cmd+=['-c:v','copy','-movflags','+faststart',str(video)]
subprocess.run(cmd,check=True)
print('Demo created:',video, 'bytes:',video.stat().st_size)
