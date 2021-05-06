"""utils.py | drawgoodlib
Utility functions for visualizing images. From Lucas Tian, drawgood repository.

Original source: drawgood/experiments/utils.py
"""
# ==== plot all stimuli for a given subject
import json
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.image as mpimg
from matplotlib.patches import Circle

plot_orig_stim = True
use_actual_time = False

def process_stroke_data(raw_stroke_string):
    """Processes strokes data from the Raphael sketchpad.
    Expects a raw string.
    Author: Catherine Wong
    """
    raw_strokes = json.loads(raw_stroke_string)
    trial_stroke_trajs = []
    trial_strokes_orig = []
    trial_strokes_primitives = []
    trial_circle_params = []
    trial_times_actual = []
    for stroke in raw_strokes:
        path = stroke["path_nostring"]
        time = stroke["times"]
        primitive = stroke["primitive"]
        path_orig = stroke["pathorig"]
        circle_params = stroke["circle"]
        traj = [(p[1], -p[2], t) for p, t in zip(path, time)]
        trial_stroke_trajs.append(traj)
        trial_strokes_primitives.append(primitive)
        trial_circle_params.append(circle_params)
        trial_times_actual.append(time)
        trial_strokes_orig.append(path_orig)
    return {
        "trialstrokes": trial_stroke_trajs,
        "trial_strokes_orig":trial_strokes_orig,
        "trialprimitives": trial_strokes_primitives,
        "trialcircleparams": trial_circle_params,
    }

def plotDrawing(datflat_single, ax=[], addstrokelines=False):
    D = datflat_single
    if not ax:
        plt.figure()
        ax = plt.axes()
    ax.grid(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    ax.set_aspect("equal", "box")
    plotstimwrapper(ax, D["trialstrokes"], D["trialprimitives"], D["trialcircleparams"], 
                        [], False, False, False, addstrokelines=addstrokelines)

def saveDrawing(datflat_single, output_path, ax=[], addstrokelines=False):
    D = datflat_single
    if not ax:
        plt.figure()
        ax = plt.axes()
    ax.grid(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    ax.set_aspect("equal", "box")
    plotstimwrapper(ax, D["trialstrokes"], D["trialprimitives"], D["trialcircleparams"], 
                        [], False, False, False, addstrokelines=addstrokelines)
    plt.savefig(output_path)

def plotstimwrapper(ax, strokes, primitives=[], circle_params=[], times=[], 
    singleStrokes=False, use_snapped_lines=False, use_actual_time=False, 
    addstrokelines=False, addstrokelines_N = 20, color=[], markersize=[], 
    eachstroke_onecolor = False):
    if singleStrokes and use_snapped_lines:
        print("NOTE: not sure that y is correct oreintation")
        plotstim(ax, strokes, primitives, circle_params, times, noaxis=True)
    elif singleStrokes and not use_snapped_lines:
        print("problem - not coded yet, plotting single strokes without snapping")                                    
    elif not singleStrokes:
        if addstrokelines:
            # markersize = 12
            x = []
            y = []
            t_strokenum = []

            for snum, stroke in enumerate(strokes):
                xx = [s[0] for s in stroke]
                yy = [s[1] for s in stroke]
                # --- interpolate if there are too few dots
                if len(xx)<addstrokelines_N:
                    N = len(xx)
                    xx = np.interp(np.linspace(0,N-1, num=addstrokelines_N), np.arange(0, N), xx)
                    yy = np.interp(np.linspace(0,N-1, num=addstrokelines_N), np.arange(0, N), yy)
                    # xx = np.linspace(xx[0], xx[-1], 20)
                    # yy = np.linspace(yy[0], yy[-1], 20)
                x.append(xx)
                y.append(yy)
                t_strokenum.extend([snum for _ in range(len(xx))])
                # plt.plot(x,y, '-', color=[0.6, 0.6, 0.6])
            ons = [(xx[0], yy[0]) for xx, yy in zip(x,y)]
            offs = [(xx[-1], yy[-1]) for xx, yy in zip(x,y)]

            x = [xxx for xx in x for xxx in xx]
            y = [yyy for yy in y for yyy in yy]
            use_actual_time=False
        else:
            x = [s[0] for stroke in strokes for s in stroke]
            y = [s[1] for stroke in strokes for s in stroke]

        if not times or not use_actual_time:
            t = np.linspace(1, len(x), len(x))
        else:
            t = [tt for t in times for tt in t]


        if eachstroke_onecolor==True:
            t = t_strokenum

#         if not use_actual_time:
#             # then use order of points, easier to see order.
#             t = np.linspace(1, len(t), len(t))
        if not markersize:
            markersize=8
        # print(t)
        # print(x)
        # print(y)
        if color:
            plt.scatter(x,y, s=markersize, c=color)    
        else:
            plt.scatter(x,y, c=t, cmap="plasma", s=markersize)
        if eachstroke_onecolor==True:
            # add indication of the starting and ending dot
            for i, (on, off) in enumerate(zip(ons, offs)):
                # plt.plot(off[0], off[1], 'ok')
                # plt.plot(on[0], on[1], 'o', markerfacecolor='w', markeredgecolor='k',
                # markersize=13)
                # plt.text(on[0]-9, on[1]-8, f"{i+1}", color='k')
                plt.plot(on[0], on[1], 'o', color=[0.7, 0.7, 0.7], markersize=11)
                plt.text(on[0]-8, on[1]-7, f"{i+1}", color='k', fontsize=12)
            # for i, (on, off) in enumerate(zip(ons, offs)):
            #     plt.plot(on[0], on[1], 'o', markerfacecolor='w', markeredgecolor='k')
            #     plt.plot(off[0], off[1], 'r')
            #     plt.text(on[0]+2, on[1]+2, f"{i+1}", color='k')

