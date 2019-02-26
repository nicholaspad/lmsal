import warnings
warnings.filterwarnings("ignore", message = "divide by zero encountered in log")
warnings.filterwarnings("ignore", message = "From scipy 0.13.0, the output shape of")
warnings.filterwarnings("ignore", message = "invalid value encountered in greater")
warnings.filterwarnings("ignore", message = "invalid value encountered in less")
warnings.filterwarnings("ignore", message = "invalid value encountered in log")
warnings.filterwarnings("ignore", message = "invalid value encountered in multiply")
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")

from IPython.core import debugger; debug = debugger.Pdb().set_trace
from matplotlib.colors import LogNorm
from matplotlib.path import Path
from os import listdir
from os.path import isfile, join
from recorder import Recorder
from scipy import ndimage
from skimage import feature
from skimage import measure
from sunpy.map import Map
from timeit import default_timer as timer
from tqdm import tqdm
import astropy.units as u
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import os

RECORDER = Recorder()
RECORDER.display_start_time("structure")

RECORDER.sys_text("Importing data directories")
SAVEPATH = "data/outputs/"
PATH94 = "data/AIA94/"
PATH131 = "data/AIA131/"
PATH171 = "data/AIA171/"
PATH193 = "data/AIA193/"
PATH211 = "data/AIA211/"
PATH304 = "data/AIA304/"
PATH335 = "data/AIA335/"

DIR94 = [f for f in listdir(PATH94) if isfile(join(PATH94, f))]; DIR94.sort(); DIR94 = DIR94[1:]
DIR131 = [f for f in listdir(PATH131) if isfile(join(PATH131, f))]; DIR131.sort(); DIR131 = DIR131[1:]
DIR171 = [f for f in listdir(PATH171) if isfile(join(PATH171, f))]; DIR171.sort(); DIR171 = DIR171[1:]
DIR193 = [f for f in listdir(PATH193) if isfile(join(PATH193, f))]; DIR193.sort(); DIR193 = DIR193[1:]
DIR211 = [f for f in listdir(PATH211) if isfile(join(PATH211, f))]; DIR211.sort(); DIR211 = DIR211[1:]
DIR304 = [f for f in listdir(PATH304) if isfile(join(PATH304, f))]; DIR304.sort(); DIR304 = DIR304[1:]
DIR335 = [f for f in listdir(PATH335) if isfile(join(PATH335, f))]; DIR335.sort(); DIR335 = DIR335[1:]

K94 = []; AVG94 = []
K131 = []; AVG131 = []
K171 = []; AVG171 = []
K193 = []; AVG193 = []
K211 = []; AVG211 = []
K304 = []; AVG304 = []
K335 = []; AVG335 = []

def save_images(type, imgs):
	pass

N = 30 #len(DIR94)

for K in tqdm(range(N), desc = "Importing data"):
	temp = Map(PATH94 + DIR94[K]); K94.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH131 + DIR131[K]); K131.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH171 + DIR171[K]); K171.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH193 + DIR193[K]); K193.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH211 + DIR211[K]); K211.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH304 + DIR304[K]); K304.append([temp.data, temp.exposure_time.value, temp.date])
	temp = Map(PATH335 + DIR335[K]); K335.append([temp.data, temp.exposure_time.value, temp.date])

for K in tqdm(range(N), desc = "Generating intensity distribution"):
	if K94[K][1] > 0:
		AVG94 = np.append(AVG94, np.mean(K94[K][0] / K94[K][1]))
	if K131[K][1] > 0:
		AVG131 = np.append(AVG131, np.mean(K131[K][0] / K131[K][1]))
	if K171[K][1] > 0:
		AVG171 = np.append(AVG171, np.mean(K171[K][0] / K171[K][1]))
	if K193[K][1] > 0:
		AVG193 = np.append(AVG193, np.mean(K193[K][0] / K193[K][1]))
	if K211[K][1] > 0:
		AVG211 = np.append(AVG211, np.mean(K211[K][0] / K211[K][1]))
	if K304[K][1] > 0:
		AVG304 = np.append(AVG304, np.mean(K304[K][0] / K304[K][1]))
	if K335[K][1] > 0:
		AVG335 = np.append(AVG335, np.mean(K335[K][0] / K335[K][1]))

MEAN94 = np.mean(AVG94); SDEV94 = np.std(AVG94)
MEAN131 = np.mean(AVG131); SDEV131 = np.std(AVG131)
MEAN171 = np.mean(AVG171); SDEV171 = np.std(AVG171)
MEAN193 = np.mean(AVG193); SDEV193 = np.std(AVG193)
MEAN211 = np.mean(AVG211); SDEV211 = np.std(AVG211)
MEAN304 = np.mean(AVG304); SDEV304 = np.std(AVG304)
MEAN335 = np.mean(AVG335); SDEV335 = np.std(AVG335)

"""
[ID]: [MEAN] [SDEV]
94: 7.011 9.992
131: 22.045 44.985
171: 270.758 32.219
193: 355.914 360.449
211: 147.661 23.465
304: 67.823 24.411
335: 16.386 6.197
"""

offset = 0
for K in tqdm(range(N), desc = "Processing dataset"):
	RECORDER.info_text("Current datetime - %s" % K94[K][2])

	RECORDER.info_text("Reading raw image data")

	corrected_D94 = K94[K][0] / K94[K][1]
	corrected_D131 = K131[K][0] / K131[K][1]
	corrected_D171 = K171[K][0] / K171[K][1]
	corrected_D193 = K193[K][0] / K193[K][1]
	corrected_D211 = K211[K][0] / K211[K][1]
	corrected_D304 = K304[K][0] / K304[K][1]
	corrected_D335 = K335[K][0] / K335[K][1]

	RECORDER.info_text("Checking for brightness")
	CRITVALUE = 3
	if np.abs(MEAN94 - np.average(corrected_D94)) > CRITVALUE * SDEV94 or np.abs(MEAN131 - np.average(corrected_D131)) > CRITVALUE * SDEV131 or np.abs(MEAN171 - np.average(corrected_D171)) > CRITVALUE * SDEV171 or np.abs(MEAN193 - np.average(corrected_D193)) > CRITVALUE * SDEV193 or np.abs(MEAN211 - np.average(corrected_D211)) > CRITVALUE * SDEV211 or np.abs(MEAN304 - np.average(corrected_D304)) > CRITVALUE * SDEV304 or np.abs(MEAN335 - np.average(corrected_D335)) > CRITVALUE * SDEV335:
		RECORDER.warn_text("Bright image %04d" % K)
		offset += 1
		continue

	RECORDER.info_text("Correcting raw image data")
	corrected_D94[corrected_D94 < 1] = 1
	corrected_D94 = np.log(corrected_D94)

	corrected_D131[corrected_D131 < 1] = 1
	corrected_D131 = np.log(corrected_D131)

	corrected_D171[corrected_D171 < 1] = 1
	corrected_D171 = np.log(corrected_D171)

	corrected_D193[corrected_D193 < 1] = 1
	corrected_D193 = np.log(corrected_D193)

	corrected_D211[corrected_D211 < 1] = 1
	corrected_D211 = np.log(corrected_D211)

	corrected_D304[corrected_D304 < 1] = 1
	corrected_D304 = np.log(corrected_D304)

	corrected_D335[corrected_D335 < 1] = 1
	corrected_D335 = np.log(corrected_D335)

	RECORDER.sys_text("Exporting corrected raw images")
	plt.imsave(SAVEPATH + "raw/AIA94/raw_%04d" % (K - offset), corrected_D94, origin = "lower", cmap = "sdoaia94", vmin = int(corrected_D94.min() + 0.5), vmax =  1.25 * int(corrected_D94.max()))
	plt.imsave(SAVEPATH + "raw/AIA131/raw_%04d" % (K - offset), corrected_D131, origin = "lower", cmap = "sdoaia131", vmin = int(corrected_D131.min() + 0.5), vmax =  1.25 * int(corrected_D131.max()))
	plt.imsave(SAVEPATH + "raw/AIA171/raw_%04d" % (K - offset), corrected_D171, origin = "lower", cmap = "sdoaia171", vmin = int(corrected_D171.min() + 0.5), vmax =  1.25 * int(corrected_D171.max()))
	plt.imsave(SAVEPATH + "raw/AIA193/raw_%04d" % (K - offset), corrected_D193, origin = "lower", cmap = "sdoaia193", vmin = int(corrected_D193.min() + 0.5), vmax =  1.25 * int(corrected_D193.max()))
	plt.imsave(SAVEPATH + "raw/AIA211/raw_%04d" % (K - offset), corrected_D211, origin = "lower", cmap = "sdoaia211", vmin = int(corrected_D211.min() + 0.5), vmax =  1.25 * int(corrected_D211.max()))
	plt.imsave(SAVEPATH + "raw/AIA304/raw_%04d" % (K - offset), corrected_D304, origin = "lower", cmap = "sdoaia304", vmin = int(corrected_D304.min() + 0.5), vmax =  1.25 * int(corrected_D304.max()))
	plt.imsave(SAVEPATH + "raw/AIA335/raw_%04d" % (K - offset), corrected_D335, origin = "lower", cmap = "sdoaia335", vmin = int(corrected_D335.min() + 0.5), vmax =  1.25 * int(corrected_D335.max()))

	RECORDER.info_text("Generating binary-masked images")
	threshold_94 = int(corrected_D94.max()) / 3.0
	threshold_131 = int(corrected_D131.max()) / 3.0
	threshold_171 = int(corrected_D171.max()) / 3.0
	threshold_193 = int(corrected_D193.max()) / 3.0
	threshold_211 = int(corrected_D211.max()) / 3.0
	threshold_304 = int(corrected_D304.max()) / 3.0
	threshold_335 = int(corrected_D335.max()) / 3.0

	b_mask94 = np.logical_and(corrected_D94 > threshold_94, corrected_D94 < np.inf).astype(np.uint8)
	corrected_B94 = corrected_D94 * b_mask94
	corrected_B94[np.isnan(corrected_B94)] = 0

	b_mask131 = np.logical_and(corrected_D131 > threshold_131, corrected_D131 < np.inf).astype(np.uint8)
	corrected_B131 = corrected_D131 * b_mask131
	corrected_B131[np.isnan(corrected_B131)] = 0

	b_mask171 = np.logical_and(corrected_D171 > threshold_171, corrected_D171 < np.inf).astype(np.uint8)
	corrected_B171 = corrected_D171 * b_mask171

	b_mask193 = np.logical_and(corrected_D193 > threshold_193, corrected_D193 < np.inf).astype(np.uint8)
	corrected_B193 = corrected_D193 * b_mask193

	b_mask211 = np.logical_and(corrected_D211 > threshold_211, corrected_D211 < np.inf).astype(np.uint8)
	corrected_B211 = corrected_D211 * b_mask211

	b_mask304 = np.logical_and(corrected_D304 > threshold_304, corrected_D304 < np.inf).astype(np.uint8)
	corrected_B304 = corrected_D304 * b_mask304

	b_mask335 = np.logical_and(corrected_D335 > threshold_335, corrected_D335 < np.inf).astype(np.uint8)
	corrected_B335 = corrected_D335 * b_mask335
	corrected_B335[np.isnan(corrected_B335)] = 0

	RECORDER.sys_text("Exporting corrected binary images")
	plt.imsave(SAVEPATH + "binary/AIA94/binary_%04d" % (K - offset), corrected_B94, origin = "lower", cmap = "sdoaia94", vmin = int(corrected_D94.min() + 0.5), vmax =  1.25 * int(corrected_D131.max()))
	plt.imsave(SAVEPATH + "binary/AIA131/binary_%04d" % (K - offset), corrected_B131, origin = "lower", cmap = "sdoaia131", vmin = int(corrected_D131.min() + 0.5), vmax =  1.25 * int(corrected_D131.max()))
	plt.imsave(SAVEPATH + "binary/AIA171/binary_%04d" % (K - offset), corrected_B171, origin = "lower", cmap = "sdoaia171", vmin = int(corrected_D171.min() + 0.5), vmax =  1.25 * int(corrected_D171.max()))
	plt.imsave(SAVEPATH + "binary/AIA193/binary_%04d" % (K - offset), corrected_B193, origin = "lower", cmap = "sdoaia193", vmin = int(corrected_D193.min() + 0.5), vmax =  1.25 * int(corrected_D193.max()))
	plt.imsave(SAVEPATH + "binary/AIA211/binary_%04d" % (K - offset), corrected_B211, origin = "lower", cmap = "sdoaia211", vmin = int(corrected_D211.min() + 0.5), vmax =  1.25 * int(corrected_D211.max()))
	plt.imsave(SAVEPATH + "binary/AIA304/binary_%04d" % (K - offset), corrected_B304, origin = "lower", cmap = "sdoaia304", vmin = int(corrected_D304.min() + 0.5), vmax =  1.25 * int(corrected_D304.max()))
	plt.imsave(SAVEPATH + "binary/AIA335/binary_%04d" % (K - offset), corrected_B335, origin = "lower", cmap = "sdoaia335", vmin = int(corrected_D335.min() + 0.5), vmax =  1.25 * int(corrected_D335.max()))

	RECORDER.info_text("Generating edge images")
	SIGMA = 20
	edge94 = feature.canny(corrected_D94, sigma = SIGMA)
	edge131 = feature.canny(corrected_D131, sigma = SIGMA)
	edge171 = feature.canny(corrected_D171, sigma = SIGMA)
	edge193 = feature.canny(corrected_D193, sigma = SIGMA)
	edge211 = feature.canny(corrected_D211, sigma = SIGMA)
	edge304 = feature.canny(corrected_D304, sigma = SIGMA)
	edge335 = feature.canny(corrected_D335, sigma = SIGMA)

	RECORDER.sys_text("Exporting edge images")
	plt.imsave(SAVEPATH + "edge/AIA94/edge_%04d" % (K - offset), edge94, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA131/edge_%04d" % (K - offset), edge131, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA171/edge_%04d" % (K - offset), edge171, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA193/edge_%04d" % (K - offset), edge193, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA211/edge_%04d" % (K - offset), edge211, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA304/edge_%04d" % (K - offset), edge304, origin = "lower", cmap = "gray")
	plt.imsave(SAVEPATH + "edge/AIA335/edge_%04d" % (K - offset), edge335, origin = "lower", cmap = "gray")

	RECORDER.info_text("********** Processing completed on image %04d **********" % K)

	"""
	1. Corrected raw images [X]
	2. Binary masked images [X]
	4. Structural images [WIP]
	"""

FPS = 15

RECORDER.sys_text("********** Generating raw videos **********")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA94/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA94_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA131/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA131_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA171/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA171_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA193/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA193_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA211/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA211_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA304/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA304_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sraw/AIA335/raw_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sraw/AIA335_raw.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sraw/AIA94_raw.mp4 -i %sraw/AIA131_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA171_raw.mp4 -i %sraw/AIA193_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/AIA211_raw.mp4 -i %sraw/AIA304_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp1.mp4 -i %sraw/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp3.mp4 -i %sraw/AIA335_raw.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp4.mp4 -i %sraw/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sraw/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sraw/COMBINED_raw.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sraw/temp1.mp4 %sraw/temp2.mp4 %sraw/temp3.mp4 %sraw/temp4.mp4 %sraw/temp5.mp4 %sraw/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("********** Generating binary-mask videos **********")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA94/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA94_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA131/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA131_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA171/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA171_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA193/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA193_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA211/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA211_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA304/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA304_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sbinary/AIA335/binary_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sbinary/AIA335_binary.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA94_binary.mp4 -i %sbinary/AIA131_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA171_binary.mp4 -i %sbinary/AIA193_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/AIA211_binary.mp4 -i %sbinary/AIA304_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp1.mp4 -i %sbinary/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp3.mp4 -i %sbinary/AIA335_binary.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp4.mp4 -i %sbinary/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sbinary/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sbinary/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sbinary/COMBINED_binary.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sbinary/temp1.mp4 %sbinary/temp2.mp4 %sbinary/temp3.mp4 %sbinary/temp4.mp4 %sbinary/temp5.mp4 %sbinary/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.sys_text("********** Generating edge videos **********")
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA94/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA94_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA131/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA131_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA171/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA171_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA193/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA193_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA211/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA211_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA304/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA304_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -f image2 -start_number 0 -framerate %d -i %sedge/AIA335/edge_%%04d.png -vframes %d -q:v 2 -vcodec mpeg4 -b:v 800k %sedge/AIA335_edge.mp4" % (FPS, SAVEPATH, N, SAVEPATH))

os.system("ffmpeg -loglevel panic -y -i %sedge/AIA94_edge.mp4 -i %sedge/AIA131_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp1.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/AIA171_edge.mp4 -i %sedge/AIA193_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp2.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/AIA211_edge.mp4 -i %sedge/AIA304_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp3.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp1.mp4 -i %sedge/temp2.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp4.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp3.mp4 -i %sedge/AIA335_edge.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp5.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp4.mp4 -i %sedge/temp5.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH))
os.system("ffmpeg -loglevel panic -y -i %sedge/temp6.mp4 -filter:v 'crop=4200:600:0:0' %sedge/COMBINED_edge.mp4" % (SAVEPATH, SAVEPATH))
os.system("rm %sedge/temp1.mp4 %sedge/temp2.mp4 %sedge/temp3.mp4 %sedge/temp4.mp4 %sedge/temp5.mp4 %sedge/temp6.mp4" % (SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH, SAVEPATH))

RECORDER.display_end_time("structure")
