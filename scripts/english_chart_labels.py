"""Add vector English labels over archived charts, preserving embedded source images.

Only the documented text regions are covered. Numeric marks, curves and bars remain
in the embedded, byte-identical PNG. Outputs are self-contained SVGs.
"""
from pathlib import Path
from html import escape
from PIL import Image
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
'single-turn-metrics':(684,[label(0,0,684,20,'LLM metrics analysis: single turn',13),label(0,20,684,17,'Model: llama3.2:3b-instruct-q4_K_M | Agent: constant_data_en | Round: 4',12),label(34,265,26,145,'Score (0-1)',11,-90),label(0,762,684,270,'METRICS LEGEND\n\njson_validity: checks whether the response contains parseable JSON\ntool_args_values: direct comparison of argument values (case-insensitive)\nlevenshtein_similarity: edit similarity between response texts\np_bert: BERTScore precision; a semantic comparison measure\nr_bert: BERTScore recall; reference-content coverage\nbleu: BLEU score for output text quality\nrouge: ROUGE-L, the longest common subsequence with the reference\nmeteor: METEOR, using synonyms and word stems\ngpt_judge: mean of all GPT Judge rubric scores\nrequired_fields: checks the presence of required response fields\njaccard_similarity: Jaccard similarity over shared tokens\ngpt_context_relevance: GPT Judge assessment of contextual relevance\ngpt_question_naturalness: GPT Judge assessment of question naturalness\ngpt_reasoning_logic: GPT Judge assessment of written reasoning logic\ngpt_tool_call_correctness: GPT Judge assessment of tool-call correctness',10.5,bg='#baddE9')]),
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

def build():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for name,(ref_width,labels) in SPECS.items():
  src=ROOT/'figures/original'/f'{name}.png'
  raw=src.read_bytes();w,h=Image.open(src).size
  ref_height=ref_width*h/w
  svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {ref_width} {ref_height}">',f'<title>{escape(name.replace("-"," "))}: English labels</title>',f'<desc>English text overlays. Embedded source image SHA-256: {hashlib.sha256(raw).hexdigest()}. Numeric plot content is retained.</desc>',f'<image width="{ref_width}" height="{ref_height}" xlink:href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>']
  for x,y,bw,bh,text,size,rotation,bold,bg in labels:
   assert x>=0 and y>=0 and x+bw<=ref_width+1 and y+bh<=ref_height+3,(name,(x,y,bw,bh),ref_height)
   svg.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{bg}"/>')
   cx=x+bw/2;cy=y+bh/2;lines=text.split('\n');lineheight=size*1.3
   available=(bh if rotation else bw)-8
   # Fit long translated labels into the source text area.
   size=min(size,available/(max(map(len,lines))*.55))
   lineheight=size*1.3
   attrs=f'transform="rotate({rotation} {cx} {cy})"' if rotation else ''
   svg.append(f'<text x="{cx}" y="{cy-(len(lines)-1)*lineheight/2+size*.33}" text-anchor="middle" fill="#111" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size:.3f}" font-weight="{700 if bold else 400}" {attrs}>')
   for i,line in enumerate(lines):svg.append(f'<tspan x="{cx}" dy="{lineheight if i else 0}">{escape(line)}</tspan>')
   svg.append('</text>')
  svg.append('</svg>');out=OUT/f'{name}.svg';out.write_text(''.join(svg))
  manifest.append({'file':str(out.relative_to(ROOT)),'source_file':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'transformation':'English vector text overlays; original plot image embedded unchanged','reference_width':ref_width,'labels':labels})
 (ROOT/'data/english-labels.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(f'Created {len(manifest)} English-labelled SVG charts; all original PNG bytes preserved.')

if __name__=='__main__':build()
