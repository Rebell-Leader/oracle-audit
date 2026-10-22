"""Build the corrected charts and a 2:30 silent video with a real app capture."""
import asyncio
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "package"))
from oracle_audit import depth_test

BG = "#101b25"
FG = "#f1f4f6"
COLORS = ["#49c7ad", "#ffb76c", "#83aefe"]


def charts():
    df = pd.read_csv(ROOT / 'package/oracle_audit_scores_wide.csv')
    pos = df[df.cohort == 'ref_MarLys_AMPs']
    neg = df[df.cohort == 'ref_shuffled_decoys']
    models = ['ampeppy', 'amplify', 'broad-classifier']
    names = ['amPEPpy', 'AMPlify', 'OmegAMP broad']
    plt.rcParams.update({'font.size': 20, 'text.color': FG, 'axes.labelcolor': FG,
                         'xtick.color': FG, 'ytick.color': FG, 'axes.edgecolor': '#647581',
                         'axes.facecolor': BG, 'figure.facecolor': BG,
                         'font.family': 'DejaVu Sans'})
    fig, ax = plt.subplots(figsize=(15.2, 5.5), dpi=120)
    x = np.arange(3)
    for i, (cohort, label, color, offset) in enumerate([
        (pos, 'Known AMPs', COLORS[0], -.18), (neg, 'Separate shuffle cohort', COLORS[1], .18)]):
        rates = [(cohort[m] >= .5).mean() * 100 for m in models]
        bars = ax.bar(x+offset, rates, .32, color=color, label=label)
        for bar, value in zip(bars, rates):
            ax.text(bar.get_x()+bar.get_width()/2, value+2, f'{value:.2f}%',
                    ha='center', fontsize=23, color=color)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 108)
    ax.set_ylabel('Positive calls at score ≥ 0.5 (%)')
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper center', bbox_to_anchor=(.5,1.17), ncols=2, frameon=False,
              labelcolor=FG, fontsize=22)
    fig.tight_layout()
    fig.savefig(ROOT/'media/rates.png', facecolor=BG)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(15.2, 5.5), dpi=120)
    for model, name, color in zip(models, names, COLORS):
        d = depth_test(pos[model], neg[model])
        k = d['k_first_below']
        ax.plot(d['k'], d['precision'], color=color, lw=3,
                label=f'{name}: first below 75% at {k}')
        ax.scatter([k], [d['precision'][k-1]], c=[color], s=80, zorder=5)
    ax.axhline(.75, color='#c8d1d8', linestyle='--', lw=1.5)
    ax.axhline(.5, color='#546774', lw=1)
    ax.set(xlim=(0,1200), ylim=(.4,1.04), xlabel='Number of top-ranked sequences selected (k)',
           ylabel='Fraction of known AMPs')
    ax.spines[['top','right']].set_visible(False)
    ax.legend(frameon=False, fontsize=18, labelcolor=FG, loc='lower left')
    fig.tight_layout()
    fig.savefig(ROOT/'media/depth.png', facecolor=BG)
    plt.close(fig)

    # Replace the superseded submission figure, including its package copy.
    from PIL import Image, ImageDraw, ImageFont
    canvas = Image.new('RGB',(1920,1580),BG)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
    draw.text((60,25), 'Oracle Audit: exploratory comparisons of separate reference cohorts', font=font, fill=FG)
    for path, y in [('rates.png',100),('depth.png',800)]:
        im = Image.open(ROOT/'media'/path).convert('RGB')
        canvas.paste(im,((1920-im.width)//2,y))
    draw.text((60,1490),'Unpaired cohorts; shuffles unassayed. Depth values use seed-0 ties and k ≥ 20.',font=font,fill=FG)
    canvas.save(ROOT/'oracle_audit_figure.png')
    shutil.copyfile(ROOT/'oracle_audit_figure.png',ROOT/'package/oracle_audit_figure.png')


def slides_html():
    pages = [
        ('01 / THE QUESTION', 'Check the score<br>before choosing peptides.',
         '<p>Design tools generate candidates.<br>A prediction model helps choose what to test.</p>'
         '<p class="accent">What does that score respond to?</p>',
         'Oracle Audit · OSI Hackathon 2026'),
        ('02 / THE OBSERVATION', 'More shuffles pass the cutoff.',
         '<img src="rates.png">',
         '2,000 sequences per cohort · Separately sampled, not paired · Shuffles unassayed'),
        ('03 / SELECTION DEPTH', 'Look beyond the top 100.',
         '<img src="depth.png">',
         'First precision < 75%, checking from k=20 · Fixed random ties, seed 0 · Not experimental hit rate'),
        ('05 / USE THE AUDIT', 'Inspect the metric.<br>Then validate the biology.',
         '<div class="tiles"><div><b>14,977</b><span>sequences</span></div><div><b>16</b><span>scoring models</span></div>'
         '<div><b>2</b><span>reusable checks</span></div></div>'
         '<p class="small">Only 87 / 2,000 compositions overlap: the cohorts are not paired.<br>'
         '45 sequences have conflicting AMP/non-AMP cohort labels.<br>'
         'Next: reconcile labels, build paired controls and check training overlap.</p>'
         '<p class="links">github.com/Rebell-Leader/oracle-audit<br>huggingface.co/spaces/avaliev/oracle-audit</p>',
         'AMPredictor predicts MIC: lower is better · Surrogate scores are not activity measurements')
    ]
    css = f'''*{{box-sizing:border-box}}body{{margin:0;background:{BG};color:{FG};font-family:Arial,sans-serif}}
    section{{width:1920px;height:1080px;padding:75px 100px;position:relative;overflow:hidden}}
    .kicker{{font-size:24px;color:#49c7ad;letter-spacing:3px;margin-bottom:38px}}
    h1{{font-size:82px;line-height:1.12;letter-spacing:-2px;margin:0 0 30px;font-weight:650}}
    p{{font-size:44px;line-height:1.45;margin:24px 0}}.accent{{color:#49c7ad;font-size:54px}}
    img{{display:block;width:1720px;height:622px;object-fit:contain;margin-left:-6px}}
    footer{{position:absolute;bottom:42px;left:100px;font-size:25px;color:#aabac5}}
    .tiles{{display:flex;gap:90px;margin:45px 0 32px}}.tiles b{{font-size:88px;font-weight:500;color:#49c7ad}}
    .tiles span{{display:block;font-size:29px;margin-top:10px;color:#d2dbe1}}
    .small{{font-size:32px}}.links{{font-size:29px;line-height:1.65;color:#83aefe}}'''
    content = '<!doctype html><meta charset="utf-8"><style>'+css+'</style>'
    for i,(kicker,title,body,foot) in enumerate(pages):
        content += f'<section id="s{i}"><div class="kicker">{kicker}</div><h1>{title}</h1>{body}<footer>{foot}</footer></section>'
    (ROOT/'media/overview.html').write_text(content)


async def render_slides():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,
                                         args=['--no-sandbox','--disable-dev-shm-usage'])
        page = await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        await page.goto((ROOT/'media/overview.html').as_uri())
        await page.evaluate('document.fonts.ready')
        for i in range(4):
            await page.locator(f'#s{i}').screenshot(path=str(ROOT/f'media/overview_{i}.png'))
        await browser.close()


def encode():
    paths=[]
    for i,duration in enumerate([20,25,20,25]):
        dst=ROOT/f'media/overview_{i}.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-i',str(ROOT/f'media/overview_{i}.png'),
                        '-t',str(duration),'-r','25','-c:v','libx264','-preset','fast','-crf','18',
                        '-pix_fmt','yuv420p','-an',str(dst)],check=True)
        paths.append(dst)
    order=paths[:3]+[ROOT/'media/oracle_audit_app_capture.mp4']+paths[3:]
    concat=ROOT/'media/revised_concat.txt'
    concat.write_text(''.join(f"file '{x}'\n" for x in order))
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),
                    '-c','copy','-movflags','+faststart',str(ROOT/'media/oracle_audit_video_revised.mp4')],check=True)
    print('Created oracle_audit_video_revised.mp4 (150 seconds, silent)',flush=True)


if __name__=='__main__':
    charts()
    slides_html()
    asyncio.run(render_slides())
    encode()
