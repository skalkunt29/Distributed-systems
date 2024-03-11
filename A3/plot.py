import argparse
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


def plot(args):
    
    name = "CSCI 5673 DS NTP stats"

    file_path = "./ntp_stats_public_server.csv"

    line_width = 0.5

    frame = pd.read_csv(file_path, index_col=None, header=0)

    print(file_path, frame.shape)
    
    figure, axis = plt.subplots(2, 1)

    min_burst_pairs = frame['burst_pairs'][frame['delays'] == frame['min_delay']]
    min_offset = frame['min_offset'][frame['delays'] == frame['min_delay']]
    min_delay = frame['min_delay'][frame['delays'] == frame['min_delay']]

    axis[0].set_title("offsets")
    axis[0].scatter(min_burst_pairs, min_offset, marker="v", s=40)
    axis[0].plot(frame['burst_pairs'], frame['offsets'], marker=".", markersize=5, linewidth=line_width)
    axis[0].grid()

    axis[1].set_title("delays")
    axis[1].scatter(min_burst_pairs, min_delay, marker="v", s=40)
    axis[1].plot(frame['burst_pairs'], frame['delays'], marker=".", markersize=5, linewidth=line_width)
    # axis[1].plot(frame['burst_pairs'], frame['min_delay'], linewidth=line_width+0.2)
    axis[1].grid()

    plt.show()
    



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_file_name', type=str, default='m3dp')
    parser.add_argument('--log_dir', type=str, default='runs/')
    parser.add_argument('--x_key', type=str, default='num_updates')
    parser.add_argument('--y_key', type=str, default='loss')
    parser.add_argument('--smoothing_window', type=int, default=1)
    parser.add_argument("--plot_avg", action="store_true", default=False,
                    help="plot avg of all logs else plot separately")
    parser.add_argument("--save_fig", action="store_true", default=False,
                    help="save figure if true")

    args = parser.parse_args()

    plot(args)
