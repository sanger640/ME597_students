# You can use this file to plot the loged sensor data
# Note that you need to modify/adapt it to your own files
# Feel free to make any modifications/additions here

import matplotlib.pyplot as plt
from utilities import FileReader

def plot_errors(filename):
    
    headers, values=FileReader(filename).read_file() 
    time_list=[]
    first_stamp=values[0][-1]
    
    motions = ['circle', 'spiral', 'line']
    topicType = ['imu', 'odom', 'laser']
    motionType = ''
    dataType = ''

    for word in topicType:
        for move in motions:
            if word in filename:
                dataType = word
            if move in filename:
                motionType = move

    for val in values:
        time_list.append(val[-1] - first_stamp)

    if dataType == 'odom':
        for i in range(0, len(headers) - 1):
            if headers[i] == 'x':
                headers[i] = 'X-Position [m]'
            elif headers[i] =='y':
                headers[i] = 'Y-Position [m]'
            elif headers[i] == 'th':
                headers[i] = 'Angle [radians]'

            plt.plot(time_list, [lin[i] for lin in values], label= headers[i])
    elif dataType == 'imu':
        for i in range(0, len(headers) - 1):
            if headers[i] == 'acc_x':
                headers[i] = 'X-Acceleration [m/s^2]'
            elif headers[i] =='acc_y':
                headers[i] = 'Y-Acceleration [m/s^2]'
            elif headers[i] == 'angular_z':
                headers[i] = 'Z-Angular_Vel [radians/s]'

            plt.plot(time_list, [lin[i] for lin in values], label= headers[i])
    
    #plt.plot([lin[0] for lin in values], [lin[1] for lin in values])
    plt.legend()
    plt.grid()
    plt.xlabel('Time [nanoseconds]')
    plt.ylabel('Magnitude')
    plt.title(dataType + ' Data for ' + motionType + ' path')
    plt.savefig('plots/' + dataType + motionType + '.jpg')
    plt.show()
    
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    for filename in filenames:
        plot_errors(filename)
