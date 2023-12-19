#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 19:10:18 2023

@author: ryanrearden
"""

import numpy as np
import matplotlib.pyplot as plt

'''
When the program launches, click on the black rectangle to see the signal!
'''


class ToggleGrid:
    def __init__(self, x, y, grid_title="Monitor Display", x_label="x-coordinate pixels", y_label="y-coordinate pixels"):
        self.rows, self.cols = y, x
        self.grid_data = np.zeros((self.rows, self.cols), dtype=int)  # Initialize with zeros (black)

        self.fig, self.ax_grid = plt.subplots()
        self.ax_grid.imshow(self.grid_data, cmap='gray', vmin=0, vmax=1, origin='upper')

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.ax_grid.set_title(grid_title)
        self.ax_grid.set_xlabel(x_label)
        self.ax_grid.set_ylabel(y_label)
        
        # Define parameters
        self.t_b = 1/60  # Duration of pixel transmission
        self.f_v = 60  # Frame rate 
        self.t = np.linspace(0, (x*y)/1/60 + 1, 100000)  # Generate time vector

        # Define pixel shape function (for simplicity, using a rectangular shape)
        self.pixel_shape = lambda t: np.where((t >= 0) & (t <= self.t_b), 1, 0)

        # Plot the video signal and spectrum
        self.fig_video, self.ax_video = plt.subplots(2, 1, figsize=(12, 6))
        self.video_signal_line, = self.ax_video[0].plot(self.t*60, np.zeros_like(self.t))
        self.video_spectrum_line, = self.ax_video[1].plot(self.t, np.zeros_like(self.t))

        self.ax_video[0].set_title('Video Signal')
        self.ax_video[0].set_xlabel('Pixel Distribution')
        self.ax_video[0].set_ylabel('Pixel Intensity')

        self.ax_video[1].set_title('Video Spectrum')
        self.ax_video[1].set_xlabel('Relative Frequency (MHz)')
        self.ax_video[1].set_ylabel('Power (dB)')

        self.update_video()

    def on_click(self, event):
        if event.inaxes == self.ax_grid:
            row, col = int(event.ydata + 0.5), int(event.xdata + 0.5)
            self.grid_data[row, col] = 1 - self.grid_data[row, col]
            self.ax_grid.imshow(self.grid_data, cmap='gray', vmin=0, vmax=1, origin='upper')
            plt.draw()

            # Print the grid state after toggling
            print("Toggled Grid State:")
            print(self.get_grid_state())

            self.update_video()

    def get_grid_state(self):
        return self.grid_data.tolist()

    def update_video(self):
        # Generate pixel intensity values
        arr = np.array(self.get_grid_state())
        v_i = np.array(arr.flatten())
    
        # Construct the video signal
        video_signal = np.sum(v_i[i] * np.roll(self.pixel_shape(self.t - i * self.t_b), int(i * self.t_b * self.f_v)) for i in range(len(v_i)))
    
        # Compute the Fourier transform of the video signal
        video_spectrum = np.fft.fft(video_signal)
        freq = np.fft.fftfreq(len(self.t), d=self.t[1] - self.t[0])
    
        # Update the video signal and spectrum plots
        self.video_signal_line.set_ydata(video_signal)
        self.video_spectrum_line.set_xdata(freq)
        self.video_spectrum_line.set_ydata(np.abs(video_spectrum))
    
        self.ax_video[0].relim()
        self.ax_video[0].autoscale_view()
    
        f_max = x  # Set your desired maximum frequency here
        f_min = -x
        self.ax_video[1].set_xlim([f_min, f_max])
        self.ax_video[1].relim()
        self.ax_video[1].autoscale_view()
    
        self.fig_video.canvas.draw_idle()


if __name__ == "__main__":
    x, y = 40, 30   # Set your desired width (x) and height (y)
    grid = ToggleGrid(x, y)

    plt.show()

