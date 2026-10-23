"""Add vector English labels over archived charts, preserving embedded source images.

Only tight, declared text masks are changed. Pixel identity outside these masks
is checked for every output. Native-resolution PNGs are the canonical outputs;
self-contained SVGs embed the original and the same raster text patches.
"""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont, ImageChops
from io import BytesIO
from collections import Counter
import math
import sys
from functools import lru_cache
import base64
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/english'
# Coordinates refer to the inspected display width, with aspect ratio preserved.
# Each label is (x,y,width,height,text,font_size,rotation,bold,background).
def label(x,y,w,h,text,size,rotate=0,bold=False,bg='white'):
    return [x,y,w,h,text,size,rotate,bold,bg]
SPECS={
'model-scores':(2048,[label(0,0,2048,60,'Model score comparison',29),label(12,230,43,260,'GPT judge score',24,-90)]),
'model-power':(2048,[label(0,0,2048,60,'Resource usage comparison',29),label(12,260,43,220,'Power (mW)',24,-90)]),
'model-latency':(1930,[label(0,0,1930,65,'Model latency comparison',36,bold=True),label(600,68,1050,38,'Model latency comparison',28),label(680,1230,900,45,'Mean latency (ms)',24)]),
'quality-latency':(1754,[label(0,0,1754,68,'Model performance vs latency',42,bold=True),label(230,76,950,74,'Model performance vs latency\n(Bubble size proportional to model size)',29),label(5,430,48,620,'Mean GPT score (0-10) → Higher is better',24,-90),label(300,1357,1000,47,'Mean latency (ms) → Lower is better',25)]),
'model-radar':(810,[label(0,0,810,35,'Mobile performance radar',21,bold=True),label(150,40,350,45,'Mobile performance radar\n(Outer edge = better)',16,bold=True),label(255,104,130,32,'Latency\n(3621-37785 ms)',12,bold=True),label(0,325,118,39,'Model size\n(1.9-4.5 GB)',12,bold=True),label(525,325,90,39,'GPT score\n(0-10)',12,bold=True),label(210,549,220,35,'Energy efficiency\n(343-3958 mW)',12,bold=True)]),
'mobile-performance':(1400,[label(370,108,800,34,'Model latency comparison (Lower is better)',21),label(1,378,35,236,'Latency (ms)',17,-90),label(300,1015,950,29,'Throughput vs latency (Bubble size proportional to model size)',20),label(34,1220,33,340,'Throughput (tokens per second)',17,-90),label(500,1755,520,36,'Mean latency (ms)',18)]),
'quantization-scores':(1139,[label(125,0,1000,83,'LLM judge score distribution',43,bold=True),label(69,170,34,285,'LLM judge score (%)',16,-90,True)]),
'quantization-rounds':(1135,[label(0,0,1135,83,'Latency across conversation rounds',42,bold=True),label(78,170,32,210,'Latency (ms)',19,-90,True),label(405,490,240,35,'Round',20,bold=True),label(100,596,990,47,'Latency heatmap by model and round (ms)',30,bold=True),label(973,730,35,194,'Latency (ms)',18,-90,True)]),
'all-configurations':(1984,[label(0,0,1984,54,'Runtime configuration comparison',38,bold=True),label(260,105,520,40,'Total latency',23,bold=True),label(250,740,520,43,'Throughput',23,bold=True),label(1220,289,550,44,'Latency breakdown',25,bold=True),label(0,305,27,160,'Time (ms)',15,-90,True),label(42,910,30,240,'Tokens per second',15,-90,True),label(946,535,32,180,'Time (ms)',17,-90,True)]),
'improved-configurations':(1021,[label(0,0,1021,76,'Selected higher-performing configurations',37,bold=True),label(168,125,210,25,'Latency',13,bold=True),label(160,411,210,25,'Throughput',13,bold=True),label(623,248,220,24,'Latency breakdown',13,bold=True),label(21,218,13,100,'Time (ms)',8,-90,True),label(34,485,11,110,'Tokens per second',8,-90,True),label(470,342,10,95,'Time (ms)',8,-90,True)]),
'resource-health':(1471,[label(7,175,33,220,'RAM usage (GB)',17,-90),label(1243,104,210,28,'RAM usage',17),label(300,571,900,40,'Memory pressure: SWAP / SSD',23,bold=True),label(4,746,49,220,'SWAP usage (GB)',17,-90),label(1220,618,235,88,'Warning (1 GB)\nHigh load (2 GB)\nCritical load (4 GB)\nSWAP (virtual memory)',16),label(250,1143,1000,38,'CPU stability (No throttling = 100%)',23,bold=True),label(5,1260,35,300,'% of maximum frequency',17,-90),label(1187,1189,268,73,'Nominal frequency (100%)\nClock at start\nClock at end',16)]),
'single-turn-metrics':(684,[label(0,0,684,20,'LLM metrics analysis: single turn',13),label(0,20,684,17,'Model: llama3.2:3b-instruct-q4_K_M | Agent: constant_data_en | Round: 4',12),label(34,265,18,145,'Score (0-1)',11,-90),label(0,762,684,270,'METRICS LEGEND\n\njson_validity: checks whether the response contains parseable JSON\ntool_args_values: direct comparison of argument values (case-insensitive)\nlevenshtein_similarity: edit similarity between response texts\np_bert: BERTScore precision; a semantic comparison measure\nr_bert: BERTScore recall; reference-content coverage\nbleu: BLEU score for output text quality\nrouge: ROUGE-L, the longest common subsequence with the reference\nmeteor: METEOR, using synonyms and word stems\ngpt_judge: mean of all GPT Judge rubric scores\nrequired_fields: checks the presence of required response fields\njaccard_similarity: Jaccard similarity over shared tokens\ngpt_context_relevance: GPT Judge assessment of contextual relevance\ngpt_question_naturalness: GPT Judge assessment of question naturalness\ngpt_reasoning_logic: GPT Judge assessment of written reasoning logic\ngpt_tool_call_correctness: GPT Judge assessment of tool-call correctness',10.5,bg='#baddE9')]),
}
models={
'granite32-timeline':'granite3.2:2b-instruct-q8_0',
'granite-micro-timeline':'granite4:micro',
'llama-timeline':'llama3.2:3b-instruct-q4_K_M',
'nemotron-q5-timeline':'nemotron-mini:4b-instruct-q5_K_M',
'nemotron-q8-timeline':'nemotron-mini:4b-instruct-q8_0',
'qwen-timeline':'qwen2.5:3b-instruct-q4_K_M'}
for name,model in models.items():
 SPECS[name]=(1440,[label(0,0,1440,43,'Resource timeline: '+model,24,bold=True),label(8,173,36,260,'Memory usage (GB)',20,-90),label(420,581,690,35,'CPU stability (thermal throttling)',21),label(3,713,37,295,'% of maximum frequency',20,-90),label(520,1126,470,37,'GPU utilization',21),label(580,1684,350,39,'Round number',20)])
settings={
'hardware-settings':('Hardware optimization',930,[(58,78,350),(373,394,670),(692,710,984)]),
'combined-settings':('Three-parameter combinations',1037,[(57,74,359),(376,398,681),(697,721,1004)]),
'speculative-decoding':('Speculative decoding',950,[(57,74,354),(373,395,675),(692,715,987)]),
'cache-settings':('Cache optimization',927,[(57,74,354),(373,395,677),(694,716,989)]),
}
for name,(title,width,panels) in settings.items():
 plot_right={'hardware-settings':795,'combined-settings':586,'speculative-decoding':718,'cache-settings':668}[name]
 items=[label(90,12,width-105,29,'Performance comparison: '+title,19,bold=True)]
 for i,(title_y,top,bottom) in enumerate(panels):
  title=['Latency per round','Throughput per round','LLM judge score per round'][i]
  items.append(label(120,title_y if i != 2 or name != 'combined-settings' else 699,plot_right-130,18 if i == 0 and name == 'hardware-settings' else 14 if i == 0 else 19 if name == 'combined-settings' and i == 2 else 17,title,13))
  ylab=['Latency (ms)','Throughput (tokens/s)','Mean LLM judge score (%)'][i]
  x,wid = ((30,14) if name == 'combined-settings' else (24,12) if name == 'cache-settings' else (24,13)) if i == 0 else ((45,12) if name == 'hardware-settings' else (35,15)) if i == 1 else (38,15)
  items.append(label(24,181,11,80,ylab,9,-90) if name == 'cache-settings' and i == 0 else label(x,top+30,wid,bottom-top-60,ylab,9,-90))
  # X labels sit between panels or at the bottom, outside all ticks.
  x_y=[356,680,995][i] if name=='hardware-settings' else [360,682,1007][i] if name=='combined-settings' else [356,679,997][i] if name=='speculative-decoding' else [355,681,996][i]
  items.append(label((80+plot_right)/2-100,x_y,200,18,'Round',10))
 SPECS[name]=(width,items)


# Refined bounds: crop only each original label, then retain its visual centre.
# Label boxes describe search regions, not broad white replacement panels.
# English rendering is clipped to these safe label regions and never rescales data.
SPECS['quantization-performance']=(1065,[
 label(250,31,460,26,'Latency comparison (lower is better)',17),
 label(34,180,25,190,'Latency (ms)',15,-90),
 label(190,567,520,27,'Throughput vs total latency',17),
 label(34,660,25,248,'Throughput (tokens/s)',15,-90)])
SPECS['quantization-quality-latency']=(771,[
 label(250,3,335,27,'Performance vs latency',19,bold=True),
 label(120,32,420,22,'Model performance vs latency',17),
 label(110,53,420,21,'(Bubble size ∝ model size)',17),
 label(5,190,23,300,'Mean GPT score (%) → Higher is better',14,-90),
 label(150,623,350,25,'Mean latency (ms) → Lower is better',14)])
# These translations retain the source meaning without changing the chart title's role.
SPECS['improved-configurations'][1][0][4]='Improved configurations'
SPECS['all-configurations'][1][0][4]='Optimization comparison'
SPECS['all-configurations'][1][5][2]=24
SPECS['quantization-rounds'][1][0][4]='Latency across successive rounds'
SPECS['quantization-rounds'][1][3][4]='Latency heatmap by model and round (ms)'
# Accurate single-line regions prevent adjacent panel titles/ticks being captured.
for name in ['hardware-settings','combined-settings','speculative-decoding','cache-settings']:
 old=SPECS[name][1]
 old[0][0:4]=[90,12,SPECS[name][0]-105,29]
 for item in old:
  if item[4]=='Round':
   item[0]=100;item[2]=650;item[5]=9
# Polish cache y-label occupies x=27..35; tick digits start at x=40.
SPECS['cache-settings'][1][8][0:3]=[34,SPECS['cache-settings'][1][8][1],17]
SPECS['speculative-decoding'][1][8][0:3]=[34,SPECS['speculative-decoding'][1][8][1],17]
SPECS['cache-settings'][1][2]=label(24,181,12,80,'Latency (ms)',9,-90)
# All figure labels are independent, including the two-line subtitles and legends.
SPECS['quality-latency'][1][1:2]=[
 label(230,76,950,37,'Model performance vs latency',29),
 label(230,113,950,37,'(Bubble size ∝ model size)',29)]
SPECS['model-radar']=(810,[
 label(170,4,340,27,'Mobile performance radar',21,bold=True),
 label(180,41,300,19,'Mobile performance radar',16,bold=True),
 label(180,60,300,20,'(Outer edge = better)',16,bold=True),
 label(260,107,125,15,'Latency',12,bold=True),
 label(2,330,114,15,'Model size',12,bold=True),
 label(527,330,90,15,'GPT score',12,bold=True),
 label(230,553,200,15,'Energy efficiency',12,bold=True)])
SPECS['resource-health']=(1471,[
 label(10,175,35,220,'RAM usage (GB)',17,-90),
 label(1250,105,195,24,'RAM usage',17),
 label(300,577,900,33,'Memory pressure: SWAP / SSD',23,bold=True),
 label(27,746,27,220,'SWAP usage (GB)',17,-90),
 label(1225,621,223,21,'Warning (1GB)',16),
 label(1225,644,223,21,'High load (2GB)',16),
 label(1225,667,223,21,'Critical load (4GB)',16),
 label(1225,690,223,20,'SWAP (virtual memory)',16),
 label(250,1146,1000,32,'CPU stability (No throttling = 100%)',23,bold=True),
 label(5,1260,35,300,'% of maximum frequency',17,-90),
 label(1187,1193,260,21,'Nominal frequency (100%)',16),
 label(1187,1216,260,21,'Clock at start',16),
 label(1187,1239,260,21,'Clock at end',16)])
SPECS['single-turn-metrics'][1][:]=[
 label(190,2,315,19,'LLM metrics analysis - Single turn',13),
 label(100,19,510,18,'Model: llama3.2:3b-instruct-q4_K_M | Agent: constant_data_en | Round: 4',12),
 label(34,265,18,145,'Score (0-1)',11,-90)]
LEGEND=[
 '• json_validity: checks for valid JSON syntax without parsing errors',
 '• tool_args_values: direct, case-insensitive argument-value comparison',
 '• levenshtein_similarity: edit distance between response texts',
 '• p_bert: BERTScore precision; semantic similarity',
 '• r_bert: BERTScore recall; coverage relative to the reference',
 '• bleu: BLEU metric for evaluating machine-translation quality',
 '• rougeL: ROUGE-L; longest common subsequence for summary evaluation',
 '• meteor: METEOR includes synonyms and stemming in text comparison',
 '• gpt_judge: mean score across all GPT Judge criteria',
 '• required_fields: verifies all required fields in the response',
 '• jaccard_similarity: Jaccard similarity based on shared tokens',
 '• gpt_context_relevance: GPT Judge assessment of contextual relevance',
 '• gpt_question_naturalness: GPT Judge assessment of question naturalness',
 '• gpt_reasoning_logic: GPT Judge assessment of the response reasoning',
 '• gpt_tool_call_correctness: GPT Judge assessment of tool-call quality']
for i,text in enumerate(LEGEND):
 SPECS['single-turn-metrics'][1].append(label(0,793+i*15,684,15,text,12.5,bg='#baddE9'))

SPECS['resource-comparison']=(668,[
 label(100,18,500,17,'Resource timeline: llama3.2:3b-instruct-q4_K_M',11,bold=True),
 label(5,107,18,112,'Memory usage (GB)',8,-90),
 label(220,282,280,20,'CPU stability (Thermal Throttling)',9),
 label(100,305,500,17,'Resource timeline: granite4:micro',11,bold=True),
 label(8,399,18,107,'Memory usage (GB)',8,-90),
 label(220,573,280,20,'CPU stability (Thermal Throttling)',9),
 label(100,597,500,20,'Resource timeline: qwen2.5:3b-instruct-q4_K_M',11,bold=True),
 label(10,688,19,112,'Memory usage (GB)',8,-90),
 label(220,862,280,20,'CPU stability (Thermal Throttling)',9)])
FINAL_FIGURES={
 'single-turn-metrics','model-radar','quality-latency','mobile-performance',
 'resource-health','model-power','resource-comparison','quantization-performance',
 'quantization-quality-latency','quantization-scores','quantization-rounds',
 'hardware-settings','combined-settings','speculative-decoding','cache-settings',
 'all-configurations','improved-configurations'}

# Independently inspected plot, numeric-axis and model-legend rectangles.
PROTECTED_REGIONS={'all-configurations': [(28, 146, 930, 650),
                        (67, 789, 940, 1265),
                        (978, 334, 1984, 992)],
 'cache-settings': [(37, 74, 927, 355),
                    (51, 394, 927, 681),
                    (52, 716, 927, 996)],
 'combined-settings': [(45, 74, 1037, 360),
                       (51, 398, 1037, 682),
                       (54, 721, 1037, 1007)],
 'hardware-settings': [(38, 78, 930, 356),
                       (58, 394, 930, 680),
                       (54, 710, 930, 995)],
 'improved-configurations': [(35, 153, 450, 400),
                             (46, 443, 450, 666),
                             (483, 274, 1021, 600)],
 'mobile-performance': [(36, 142, 1400, 1015), (68, 1045, 1400, 1755)],
 'model-power': [(60, 60, 2048, 1024)],
 'model-radar': [(123, 147, 518, 542), (590, 147, 810, 265)],
 'quality-latency': [(54, 154, 1754, 1357)],
 'quantization-performance': [(60, 61, 1065, 567), (60, 596, 1065, 1029)],
 'quantization-quality-latency': [(28, 75, 771, 623)],
 'quantization-rounds': [(110, 85, 1135, 490),
                         (845, 490, 1135, 565),
                         (0, 646, 972, 1048)],
 'quantization-scores': [(105, 84, 1139, 743)],
 'resource-comparison': [(24, 49, 668, 282),
                         (27, 337, 668, 573),
                         (30, 629, 668, 862)],
 'resource-health': [(46, 40, 1471, 102),
                     (46, 133, 1471, 571),
                     (55, 611, 1178, 1140),
                     (1178, 717, 1471, 1140),
                     (40, 1182, 1139, 1717),
                     (1139, 1265, 1471, 1717)],
 'single-turn-metrics': [(52, 38, 684, 762)],
 'speculative-decoding': [(38, 74, 950, 356),
                          (51, 395, 950, 679),
                          (52, 715, 950, 997)]}

FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
# Files exported by matplotlib contain DejaVu Sans labels; keep that typeface.
def font_file(bold=False,mono=False):
 return str(FONT_DIR/('DejaVuSansMono.ttf' if mono else 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'))

@lru_cache(maxsize=512)
def getfont(size,bold=False,mono=False):
 return ImageFont.truetype(font_file(bold,mono),max(1,round(size)))

def text_height(text,size,bold=False,mono=False):
 box=getfont(size,bold,mono).getbbox(text);return box[3]-box[1]

def rendered_text(text, size, bold=False, mono=False, color=(0,0,0,255)):
 font=getfont(size,bold,mono)
 box=font.getbbox(text); width=max(1,box[2]-box[0]);height=max(1,box[3]-box[1])
 tile=Image.new('RGBA',(width,height));d=ImageDraw.Draw(tile)
 d.text((-box[0],-box[1]),text,font=font,fill=color)
 return tile

def tight_foreground_box(crop,background):
 rgb=crop.convert('RGB'); d=ImageChops.difference(rgb,Image.new('RGB',rgb.size,background))
 # Exclude only near-background anti-aliasing at < 3 / 255.
 mask=d.convert('L').point(lambda v: 255 if v>3 else 0)
 return mask.getbbox()

def png_data(im):
 b=BytesIO();im.save(b,format='PNG');return b.getvalue()

def build(names=None):
 OUT.mkdir(parents=True,exist_ok=True); manifest=[]
 manifest_path=ROOT/'data/english-labels.json'
 if names and manifest_path.exists():
  manifest=[m for m in json.loads(manifest_path.read_text()) if Path(m['source_file']).stem in FINAL_FIGURES and Path(m['source_file']).stem not in names]
 for name,(ref_width,labels) in SPECS.items():
  if name not in FINAL_FIGURES or (names and name not in names):continue
  src=ROOT/'figures/original'/f'{name}.png';raw=src.read_bytes()
  original=Image.open(src).convert('RGBA');output=original.copy();w,h=original.size;scale=w/ref_width
  masks=[];meta=[];svg_patches=[]
  for index,(x,y,bw,bh,text,size,rotation,bold,bg) in enumerate(labels):
   # Source labels must be isolated before rendering. This prevents a global redraw.
   region=(round(x*scale),round(y*scale),min(w,round((x+bw)*scale)),min(h,round((y+bh)*scale)))
   crop=original.crop(region)
   # Use the original patch's most common background, including the blue legend.
   colors=Counter(crop.convert('RGB').getdata()); background=colors.most_common(1)[0][0]
   ink=min(colors,key=lambda c:sum(c))+(255,)
   bounds=tight_foreground_box(crop,background)
   if bounds is None: raise AssertionError((name,index,'No source label found',region))
   left,top,right,bottom=bounds
   source_box=(region[0]+left,region[1]+top,region[0]+right,region[1]+bottom)
   mono=name=='single-turn-metrics' and index>=3
   # Match the original type size, using its visible glyph height. The input size
   # is only a safety upper bound, not an invitation to redesign the typography.
   glyph_height=(right-left) if rotation else (bottom-top)
   max_size=max(1,size*scale*1.25)
   sizes=range(1,max(2,round(max_size)+1))
   font_size=min(sizes,key=lambda z:abs(text_height(text,z,bold,mono)-glyph_height))
   legend=name=='resource-health' and index in {1,4,5,6,7,10,11,12}
   if legend:font_size=round(size*scale)
   # Keep long translations inside the reserved text area, away from plotted data.
   available=(region[3]-region[1]) if rotation else (region[2]-region[0])
   tile=rendered_text(text,font_size,bold,mono,ink)
   while tile.width>available and font_size>1:
    font_size-=1;tile=rendered_text(text,font_size,bold,mono,ink)
   if rotation:tile=tile.rotate(90,expand=True)
   cx=(source_box[0]+source_box[2])/2;cy=(source_box[1]+source_box[3])/2
   tx=round(cx-tile.width/2);ty=round(cy-tile.height/2)
   if mono: tx=0;ty=source_box[1]
   if legend:tx=source_box[0];ty=source_box[1]
   tx=max(region[0],min(tx,region[2]-tile.width));ty=max(region[1],min(ty,region[3]-tile.height))
   # Clear the exact source text rectangle, not the full search region. One native
   # pixel of padding erases anti-aliasing and is recorded in the proof manifest.
   erase=(max(region[0],source_box[0]-1),max(region[1],source_box[1]-1),min(region[2],source_box[2]+1),min(region[3],source_box[3]+1))
   ImageDraw.Draw(output).rectangle((erase[0],erase[1],erase[2]-1,erase[3]-1),fill=background+(255,))
   output.alpha_composite(tile,(tx,ty))
   text_box=(tx,ty,tx+tile.width,ty+tile.height)
   patch=(min(erase[0],text_box[0]),min(erase[1],text_box[1]),max(erase[2],text_box[2]),max(erase[3],text_box[3]))
   masks.extend([erase,text_box]);svg_patches.append(patch)
   meta.append({'text':text,'source_text_bounds_px':list(source_box),'erasure_bounds_px':list(erase),'english_text_bounds_px':list(text_box),'font':'DejaVu Sans Mono' if mono else 'DejaVu Sans','font_size_px':font_size,'bold':bold,'rotation_degrees':rotation,'background_rgb':background})
  diff=ImageChops.difference(original,output)
  channels=diff.split();maximum=channels[0]
  for channel in channels[1:]:maximum=ImageChops.lighter(maximum,channel)
  changed=maximum.point(lambda v:255 if v else 0)
  outside=changed.copy();od=ImageDraw.Draw(outside)
  for box in masks:od.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=0)
  assert outside.getbbox() is None,(name,'Pixels changed outside text masks')
  protected_boxes=[tuple(round(value*scale) for value in box) for box in PROTECTED_REGIONS[name]]
  for box in protected_boxes:
   assert maximum.crop(box).getbbox() is None,(name,'Protected plot/tick pixels changed',box)
  png=OUT/f'{name}.png';output.save(png,compress_level=3)
  # Render-safe SVG: untouched original plus the exact same, native-sized text
  # patches as the PNG. No browser fonts, resampling, or plot regeneration.
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<title>{escape(name.replace("-"," "))}: English label overlay</title>',f'<desc>Only translated text labels differ from the original. Source SHA-256: {hashlib.sha256(raw).hexdigest()}.</desc>',f'<image width="{w}" height="{h}" xlink:href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>']
  for box in svg_patches:
   tile=output.crop(box); encoded=base64.b64encode(png_data(tile)).decode()
   svg.append(f'<image x="{box[0]}" y="{box[1]}" width="{tile.width}" height="{tile.height}" xlink:href="data:image/png;base64,{encoded}"/>')
  svg.append('</svg>');svgfile=OUT/f'{name}.svg';svgfile.write_text(''.join(svg))
  manifest.append({'file':str(png.relative_to(ROOT)),'svg_file':str(svgfile.relative_to(ROOT)),'source_file':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'svg_sha256':hashlib.sha256(svgfile.read_bytes()).hexdigest(),'dimensions_px':[w,h],'transformation':'English text patches on original raster; no plotted data regenerated','validation':{'changed_pixels_outside_label_masks':0,'dimensions_unchanged':True,'original_file_unchanged':src.read_bytes()==raw,'protected_plot_and_tick_regions_unchanged':True,'protected_regions_px':protected_boxes,'channel_exact_comparison':'all RGBA channels, native-resolution decoded PNGs'},'label_masks_px':[list(b) for b in masks],'labels':meta})
  print(name,output.size,'PASS: zero changed pixels outside text masks',flush=True)
 (ROOT/'data/english-labels.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(f'Created {len(manifest)} PNGs and matching SVGs at original resolution.')

if __name__=='__main__':build(set(sys.argv[1:]) or None)
