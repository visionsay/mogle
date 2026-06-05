#!/usr/bin/env python3
"""
make_bgm.py — 절차적 BGM 생성기 (100% 오리지널 / 상업적 이용 안전).

영상(index.html)의 GSAP 타임라인에서 '텍스트가 나타나는 순간'을 음악 히트포인트로
삼아, 경쾌한 4-on-the-floor 그루브 위에 그 순간마다 멜로디 액센트(스탭/플럭/임팩트)를
정확히 떨어뜨린다. 출력: assets/audio/bgm.wav  (이후 ffmpeg로 mp3 변환)

Deterministic: 고정 시드 사용. 동일 입력 → 동일 출력.
"""
import numpy as np
import wave, struct, os

SR = 44100
DUR = 36.0
N = int(SR * DUR)
master = np.zeros(N, dtype=np.float64)
rng = np.random.default_rng(7)  # fixed seed → deterministic noise

# ---------- helpers ----------
def midi(n):  # note name -> freq
    names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    p = names[n[:-1]] if n[1] != '#' else names[n[:2]]
    octv = int(n[-1])
    m = 12 * (octv + 1) + p
    return 440.0 * 2 ** ((m - 69) / 12)

def add(buf, start_t):
    i = int(start_t * SR)
    j = min(N, i + len(buf))
    if i < N and j > i:
        master[i:j] += buf[: j - i]

def env_exp(n, decay, attack=0.003):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    d = np.exp(-t / decay)
    return a * d

def pluck(freq, dur, gain=0.5, decay=None, detune=0.004):
    decay = decay or dur * 0.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = env_exp(n, decay)
    # fundamental + soft 2nd/3rd harmonic + slight detune → bright but warm
    s = (np.sin(2*np.pi*freq*t)
         + 0.5*np.sin(2*np.pi*freq*(1+detune)*t)
         + 0.28*np.sin(2*np.pi*2*freq*t)
         + 0.12*np.sin(2*np.pi*3*freq*t))
    return gain * e * s / 1.9

def stab(notes, dur, gain=0.5):
    out = np.zeros(int(dur*SR))
    for nm in notes:
        p = pluck(midi(nm), dur, gain=gain, decay=dur*0.45)
        out[:len(p)] += p[:len(out)]
    return out / max(1, len(notes)**0.5)

def kick(gain=0.9):
    dur = 0.30; n = int(dur*SR); t = np.arange(n)/SR
    f = 120*np.exp(-t/0.03) + 48          # pitch sweep 120->48 Hz
    ph = 2*np.pi*np.cumsum(f)/SR
    body = np.sin(ph) * np.exp(-t/0.18)
    click = (rng.standard_normal(n) * np.exp(-t/0.005)) * 0.3
    return gain*(body + click)

def snare(gain=0.5):
    dur=0.20; n=int(dur*SR); t=np.arange(n)/SR
    noise = rng.standard_normal(n)
    noise = np.diff(np.concatenate([[0],noise]))      # cheap high-pass
    tone = np.sin(2*np.pi*190*t)*0.5
    return gain*((noise*1.0 + tone)*np.exp(-t/0.10))

def hat(gain=0.22, dur=0.05):
    n=int(dur*SR); t=np.arange(n)/SR
    noise = rng.standard_normal(n)
    noise = np.diff(np.concatenate([[0],noise]))
    noise = np.diff(np.concatenate([[0],noise]))      # double diff → bright
    return gain*noise*np.exp(-t/0.012)

def bass(freq, dur, gain=0.5):
    n=int(dur*SR); t=np.arange(n)/SR
    e = (np.clip(t/0.01,0,1))*np.exp(-t/(dur*0.7))
    s = np.sin(2*np.pi*freq*t) + 0.3*np.sin(2*np.pi*2*freq*t)*np.exp(-t/0.05)
    return gain*e*s/1.3

def pad(notes, dur, gain=0.18):
    n=int(dur*SR); t=np.arange(n)/SR
    atk=min(0.6,dur*0.3); rel=min(1.2,dur*0.4)
    e=np.ones(n)
    e[:int(atk*SR)] = np.linspace(0,1,int(atk*SR))
    e[-int(rel*SR):] = np.linspace(1,0,int(rel*SR))
    vib = 1 + 0.004*np.sin(2*np.pi*5*t)
    out=np.zeros(n)
    for nm in notes:
        f=midi(nm)
        out += np.sin(2*np.pi*f*t*vib) + 0.4*np.sin(2*np.pi*2*f*t)
    return gain*e*out/ (len(notes)*1.4)

def impact(gain=0.7):
    dur=0.6; n=int(dur*SR); t=np.arange(n)/SR
    sub = np.sin(2*np.pi*(70*np.exp(-t/0.15)+40)*t)*np.exp(-t/0.2)
    swell = rng.standard_normal(n)*np.linspace(0,1,n)**2*np.exp(-(t-0.0)/0.4)*0.0  # (no pre-swell here)
    noise = rng.standard_normal(n)*np.exp(-t/0.12)*0.25
    return gain*(sub + noise)

# ---------- section drum programming ----------
def four_on_floor(start, end, kgain=0.9):
    t=start
    while t < end:
        add(kick(kgain), t); t += 0.5
def backbeat(start, end, sgain=0.5):
    t=start+0.5
    while t < end:
        add(snare(sgain), t); t += 1.0
def hats(start, end, step=0.25, hgain=0.22):
    t=start
    while t < end:
        add(hat(hgain*(1.0 if round((t-start)/step)%2==0 else 0.7)), t); t += step
def bassline(start, end, roots, step=0.5, bgain=0.5):
    # roots: list of note names cycled per 2s bar
    t=start; bar=0
    while t < end:
        root = roots[int((t-start)//2.0) % len(roots)]
        add(bass(midi(root), step*0.95, bgain), t)
        t += step

# =================================================================
#  ARRANGEMENT  (sections mirror the video scenes)
# =================================================================
ROOTS = ['C2','G2','A2','F2']   # I–V–vi–IV in C major → bright/cheerful

# --- A · intro 0–5 : pad + hero plucks + soft pulse ---
add(pad(['C4','E4','G4'], 5.2, gain=0.16), 0.0)
add(kick(0.45), 2.0); add(kick(0.45), 3.0); add(kick(0.55), 4.0)
add(hat(0.12), 3.0); add(hat(0.12), 3.5); add(hat(0.14), 4.0); add(hat(0.14), 4.5)

# --- B · build 5–11 : kick builds, hats, bass ---
add(pad(['C4','E4','G4'], 6.4, gain=0.15), 5.0)
t=5.0
while t<11.0:
    add(kick(0.7 if t>=8.0 else 0.55), t); t += (0.5 if t>=8.0 else 1.0)
hats(5.5, 11.0, step=0.5, hgain=0.16)
bassline(7.0, 11.0, ROOTS, step=0.5, bgain=0.42)
backbeat(8.0, 11.0, 0.42)

# --- C · main groove 11–25.5 : full kit + bass + light arp ---
add(pad(['C4','E4','G4','B4'], 14.6, gain=0.14), 11.0)
four_on_floor(11.0, 25.5, 0.9)
backbeat(11.0, 25.5, 0.5)
hats(11.0, 25.5, step=0.25, hgain=0.2)
bassline(11.0, 25.5, ROOTS, step=0.5, bgain=0.5)
# light offbeat pentatonic arp for movement (low gain)
arp = ['E5','G5','A5','G5']
t=15.9; k=0
while t<24.8:
    add(pluck(midi(arp[k%len(arp)]), 0.32, gain=0.16), t); t+=0.5; k+=1

# --- D · peak 25.5–30.5 : busy hats, fill, then drop ---
add(pad(['C4','E4','G4'], 5.0, gain=0.14), 25.5)
four_on_floor(25.5, 29.5, 0.92)
backbeat(25.5, 29.5, 0.52)
hats(25.5, 29.5, step=0.125, hgain=0.16)
bassline(25.5, 29.5, ['C2','C2','G2','G2'], step=0.5, bgain=0.5)
# snare fill 29.5–30.0
tf=29.5
for st in [0.0,0.125,0.25,0.375,0.5,0.625,0.6875,0.75,0.8125,0.875,0.9375]:
    add(snare(0.45+0.5*st), 29.5+st)
add(impact(0.8), 30.0)

# --- E · outro 30.5–36 : warm pad + chimes + resolve, fade ---
add(pad(['C4','E4','G4','C5'], 5.5, gain=0.22), 30.5)
add(bass(midi('C2'), 3.0, 0.45), 30.5)
add(pluck(midi('C6'), 1.6, gain=0.4, decay=0.9), 32.0)   # chime w/ shimmer 1
add(pluck(midi('G5'), 1.6, gain=0.3, decay=0.9), 32.0)
add(pluck(midi('E6'), 1.8, gain=0.34, decay=1.0), 34.7)  # chime w/ shimmer 2
add(pad(['C5','E5','G5'], 2.6, gain=0.12), 33.4)

# =================================================================
#  HITPOINTS — beats locked to text-reveal moments
# =================================================================
# hero (지식이 / 가장 빠른 길)
add(pluck(midi('C5'),0.6,0.42), 0.55)
add(pluck(midi('G5'),0.6,0.42), 0.78)
# statement (아이디어는 누구나)
add(pluck(midi('E5'),0.5,0.4), 5.25)
add(pluck(midi('C5'),0.5,0.3), 5.45)
# payoff (이제, 단 4주) — big stab + impact
add(stab(['C5','E5','G5'],0.7,0.5), 8.45); add(impact(0.5), 8.45)
# process title
add(pluck(midi('G4'),0.5,0.34), 11.2)
# 4 cards — ascending melodic run, locked to reveals 11.7/12.75/13.8/14.85
for tt,nn in [(11.7,'C5'),(12.75,'E5'),(13.8,'G5'),(14.85,'C6')]:
    add(pluck(midi(nn),0.6,0.46), tt)
    add(hat(0.18), tt)
# stats quick run 25.85/26.13/26.41
for tt,nn in [(25.85,'G5'),(26.13,'A5'),(26.41,'C6')]:
    add(pluck(midi(nn),0.45,0.42), tt)
# counters resolve
add(stab(['C5','E5','G5','C6'],0.8,0.34), 27.6)
# CTA (첫 문장을 시작하세요) — big stab
add(stab(['C5','E5','G5'],0.9,0.5), 30.85); add(impact(0.45), 30.85)
# brand lockup
add(pluck(midi('G5'),0.7,0.4), 31.5)

# ---------- master bus: fades, soft-clip, normalize ----------
# global fade in/out
fi=int(0.4*SR); master[:fi]*=np.linspace(0,1,fi)
fo=int(1.5*SR); master[-fo:]*=np.linspace(1,0,fo)
# gentle high-pass-ish DC removal
master -= np.mean(master)
# soft clip + normalize to -1 dBFS
peak=np.max(np.abs(master)) or 1.0
master = np.tanh(master/peak*1.1)*0.89

os.makedirs('assets/audio', exist_ok=True)
pcm = (master*32767).astype(np.int16)
with wave.open('assets/audio/bgm.wav','w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote assets/audio/bgm.wav  ({DUR}s, {SR}Hz mono)  peak={np.max(np.abs(master)):.3f} rms={np.sqrt(np.mean(master**2)):.3f}")
