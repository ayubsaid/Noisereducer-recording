import pyaudio
import wave
import os
import time
import threading
import tkinter as tk
import noisereduce as nr
from scipy.io import wavfile
from playsound import playsound


class VoiceRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.button = tk.Button(text="🔦", font=('Arial', 200, 'bold'), command=self.click_handler)
        self.button.pack()

        self.recording = False
        self.label = tk.Label(text='00:00:00')
        self.label.pack()

        self.root.mainloop()

    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.config(fg="black")
        else:
            self.recording = True
            self.button.config(fg='red')
            threading.Thread(target=self.record).start()

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                            input=True, frames_per_buffer=1024)
        frames = []
        start = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)
            passed = time.time() - start

            secs = passed % 60
            mins = passed // 60
            hours = mins // 60
            self.label.config(text=f'{int(hours):02d}:{int(mins):02d}:{int(secs):02d}')

        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True
        i = 1
        while exists:
            if os.path.exists(f'recording{i}.wav'):
                i += 1
            else:
                exists = False

        # Save the recording without noise reduction
        sound_file = wave.open(f'recording{i}.wav', 'wb')
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()



   # until here we create a function for recording voice with button,
   # after here we started to write the code for noise reducing


        # Perform noise reduction
        input_filename = f'recording{i}.wav'
        output_filename = f'recording{i}_reduced.wav'
        rate, data = wavfile.read(input_filename)
        # This is for increasing and decreasing rate for reducing noise
        reduced_noise = nr.reduce_noise(
                        y=data,
                        sr=rate,
                        stationary=True,  # It's for make a noise-reducer function better, and we can do it 'True' and 'False' depend on the place !!
                        y_noise=None,
                        prop_decrease=1.0,
                        time_constant_s=2.0,
                        freq_mask_smooth_hz=500,
                        time_mask_smooth_ms=50,
                        thresh_n_mult_nonstationary=2,
                        sigmoid_slope_nonstationary=10,
                        n_std_thresh_stationary=1.5,
                        tmp_folder=None,
                        chunk_size=600000,
                        padding=30000,
                        n_fft=1024,
                        win_length=None,
                        hop_length=None,
                        clip_noise_stationary=True,
                        use_tqdm=False,
                        n_jobs=1,
                )

        # Save the noise-reduced audio as a new WAV file
        wavfile.write(output_filename, rate, reduced_noise.astype(data.dtype))

        # Play the noise-reduced audio
        playsound(output_filename)


VoiceRecorder()
