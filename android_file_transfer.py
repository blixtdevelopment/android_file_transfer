from subprocess import PIPE, Popen
import PySimpleGUI as sg
import os
import errno
import shutil
import queue
import threading
import time
import pathlib

'''
USE ADB to pull push files/directories

# PULL FROM PHONE TO PC
adb pull --sync -a sdcard/DCIM/ C:\afcTemp
\|/
will create C:\afcTemp\DCIM\ on PC

# PUSH FROM PC TO PHONE
adb push --sync C:\afcTemp\gg /sdcard/DCIM/
\|/
Will create a folder called 'gg' in /sdcard/DCIM/ 

'''

class device_info():
    def __init__(self, device_serial):
        # get manufactur
        self.serial = device_serial
        self.brand = self.get_info_with_cmd("adb -s " + str(self.serial) + " shell getprop ro.product.manufacturer")
        self.model = self.get_info_with_cmd("adb -s " + str(self.serial) + " shell getprop ro.product.model")
        self.source_device = False

    def __str__(self):
        return str(self.brand + " " + self.model + " " + self.serial)

    def get_info_with_cmd(self, command):
        msg = os.popen(command).read()
        return msg.strip('\n')


def get_available_devices():
    devices = os.popen("adb devices").read().split('\n')[1:]
    for i, s in enumerate(devices):
        devices[i] = s.split("\t", 1)[0]
    devices = list(filter(None, devices))

    return devices


def get_layout():
    new_layout_v1 = [[sg.Text('From device:', key="_AT_SOURCE_", size=(15, 1), font=(None, 18)),
                      sg.Text('Connect', justification="r", key="_AT_SOURCE_HEAD_", size=(23, 1), font=(None, 18), text_color="blue")],
                     [sg.Text("", size=(68, 1), key="_DEVICE_1_", justification="r")],
                     [sg.Text('To device:', key="_AT_DEST_", size=(15, 1), font=(None, 18)),
                      sg.Text('', justification="r", key="_AT_DEST_HEAD_", size=(23, 1), font=(None, 18))],
                     [sg.Text("", size=(68, 1), key="_DEVICE_2_", justification="r")],
                     [sg.Text("Connect the source device...", size=(54, 1), font=(None, 12, "bold"), key="_USER_PROMT_", justification="center")],
                     [sg.Radio('Complete DCIM!', "RADIO1", key="_DCIM_"),
                      sg.Radio('Only DCIM/Camera!', "RADIO1", default=True)],
                     [sg.Checkbox('Delete source files', key="_CH_DELETE_SOURCE_", default=True),
                      sg.Checkbox('Enable debugging output', enable_events=True, key="_CH_ENABLE_DEBUG_")],
                     [sg.Output(size=(76, 10), key="_DEBUG_OUTPUT_", visible=False)],
                     [sg.OK(button_text="Start", bind_return_key=False), sg.Cancel()]]
    return new_layout_v1


def update_promt(msg):
    window.Element('_USER_PROMT_').Update(msg)


def clean_folders(path, pc=True):
    if not pc:
        print("Removeing copied files with command: ")
        command = "adb shell rm -rf " + path + "*"
        print("Removeing copied files with command: " + command)
        msg = os.popen(command).read()
        print(msg)
    else:
        print("Removing temp files on pc, on path: " + path)
        shutil.rmtree(path, ignore_errors=True)
        print("Operation finished")


def temp_folder(current_folder='C:/afcTemp'):
    if not os.path.isdir(current_folder):
        try:
            print("Temp folder does not exist, creating...")
            os.mkdir(current_folder)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                print("Error happened when creating folder:" + exc.strerror)
                raise
            pass

    return current_folder


def copy_files(command, que, android_path, delete_temp, is_on_pc):
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

    print("Copying files, this might take a while...")
    while process.poll() is None:
        sg.PopupAnimated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='green', transparent_color='green')
        time.sleep(0.1)
    sg.PopupAnimated(image_source=None)

    out_put = process.stdout.read().decode()
    print(out_put)
    if "error" in out_put:
        print("WARNING: Error happened while pulling/pushing files! See error above.")
        que.put("error")
        return
    print("Copying files finished!")
    if delete_temp:
        clean_folders(android_path, pc=is_on_pc)
    que.put('done')


if __name__ == "__main__":


    # create layout
    layout = get_layout()
    window = sg.Window('Android Camera Transfer', layout, resizable=True)
    gui_queue = queue.Queue()  # queue used to communicate between the gui and the threads
    t_folder_path = temp_folder()

    ### CHECK ADB FIRST ###
    adb_cmd = os.popen('adb').read()
    if "Android Debug Bridge" not in adb_cmd:
        print("ADB is not installed")
        adb_installed = False
    else:
        print("ADB is installed")
        adb_installed = True

    lock = False
    first_device = True
    device1 = None
    device2 = None

    while True:
        event, values = window.Read(timeout=100)

        # Terminate the application if the window is closed
        if event is None or event == 'Cancel':
            break
        elif not adb_installed:
            update_promt("ADB is not installed")
            continue

        # Check if thread has finished
        try:
            message = gui_queue.get_nowait()
        except queue.Empty:  # get_nowait() will get exception when Queue is empty
            message = None  # break from the loop if no more messages are queued up
        if message is not None:
            if message == "error":
                sg.PopupError("Error happened in adb operation. Please check if your files is save. "
                              "\nProgram will terminate after this popup...", title="Error")
                window.close()
                break
            if device2 is None:
                update_promt("Disconnect the device")
            else:
                update_promt("FINISHED! Close program")
            lock = False

        if device1 is not None:
            if len(get_available_devices()) < 1:
                window.Element('_AT_SOURCE_HEAD_').Update("Disconnected!", text_color="Red")
                window.Element('_AT_DEST_HEAD_').Update("Connect", text_color="blue")
                update_promt("Connect the destination device...")

        # Continue if operations is note done.
        if lock:
            continue

        available_device = get_available_devices()
        if len(available_device) > 1:
            print("Warning, more than 1 device is attached...")
            continue
        if available_device:
            if first_device:
                device1 = device_info(available_device[0])
                print("Device " + str(device1) + " connected!")
                window.Element('_AT_SOURCE_HEAD_').Update("Connected!", text_color="green")
                window.Element("_DEVICE_1_").Update(device1)
                update_promt("Press START when ready")
                print("Waiting for finished settings and start signal...")
                first_device = False
            elif device2 is None:
                if available_device[0] != device1.serial:
                    device2 = device_info(available_device[0])
                    print("Device " + str(device2) + " connected!")
                    window.Element('_AT_DEST_HEAD_').Update("Connected!", text_color="green")
                    window.Element("_DEVICE_2_").Update(device2)
                    update_promt("Press start to copy to device")

        if event == "_CH_ENABLE_DEBUG_":
            window.Element('_DEBUG_OUTPUT_').Update(visible=values["_CH_ENABLE_DEBUG_"])
            window.Element('_CH_ENABLE_DEBUG_').Update(visible=False)

        if event == "Start":
            print("Checking source and destination...")
            # CHECK FIRST STEP
            if device1 is not None and device2 is None:
                # Copy from first device
                update_promt("Please wait, processing")
                if values["_DCIM_"]:
                    android_path = "/sdcard/DCIM/"
                    cmd = "adb pull --sync -a sdcard/DCIM/ " + t_folder_path
                else:
                    android_path = "/sdcard/DCIM/Camera/"
                    cmd = "adb pull --sync -a sdcard/DCIM/Camera/ " + t_folder_path
                try:
                    threading.Thread(target=copy_files,
                                     args=(cmd, gui_queue, android_path, values["_CH_DELETE_SOURCE_"], False,), daemon=True).start() #  gui_queue,
                    lock = True
                except Exception as e:
                    print('Error starting work thread')

            # SECOND STEP
            if device1 is not None and device2 is not None:
                # pus to second device
                update_promt("Please wait, processing")
                if values["_DCIM_"]:
                    pc_path = t_folder_path + "/DCIM"
                    cmd = "adb push --sync " + t_folder_path + "/DCIM /sdcard/"
                else:
                    pc_path = t_folder_path + "/Camera"
                    cmd = "adb push --sync " + t_folder_path + "/Camera /sdcard/DCIM/"
                    print("CMD")
                    print(cmd)
                try:
                    threading.Thread(target=copy_files,
                                     args=(cmd, gui_queue, pc_path, values["_CH_DELETE_SOURCE_"], True, ), daemon=True).start()  # gui_queue,
                    lock = True
                except Exception as e:
                    print('Error starting work thread ' + e)
                continue

    window.Close()