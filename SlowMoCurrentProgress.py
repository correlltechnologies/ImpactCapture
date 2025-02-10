import pandas as pd
import matplotlib.pyplot as plt
import cv2
from tkinter import Tk, filedialog

# Global pause state
is_paused = True


def select_file(file_type):
    """Open a file dialog to select a file of the specified type."""
    Tk().withdraw()
    return filedialog.askopenfilename(filetypes=[(file_type, "*.*")])


def toggle_pause():
    """Toggle the pause state."""
    global is_paused
    is_paused = not is_paused


def read_displacement_vs_load_data(file_path):
    """Read displacement and load data from an Excel file."""
    try:
        df = pd.read_excel(file_path, sheet_name=0)  # Ensure correct sheet name
        print("Excel Columns:", df.columns)  # Debugging step

        displacement_col = df.columns[3] if len(df.columns) > 3 else df.columns[0]
        load_col = 'Load [N]'

        df_clean = df[[displacement_col, load_col]].dropna()
        df_clean.columns = ['Displacement (mm)', 'Load (N)']
        df_clean = df_clean.apply(pd.to_numeric, errors='coerce')
        return df_clean['Displacement (mm)'].values, df_clean['Load (N)'].values
    except Exception as e:
        print(f"Error reading data: {e}")
        return None, None


def show_graph(displacement_data, load_data):
    """Display the initial graph of load vs displacement."""
    plt.ion()
    fig, ax = plt.subplots()
    ax.plot(displacement_data, load_data, label='Load vs Displacement')

    # Create the red displacement line
    displacement_line, = ax.plot([displacement_data[0], displacement_data[0]],
                                 [min(load_data), max(load_data)], 'r--',
                                 label='Current Displacement')

    ax.set_title('Load vs Displacement')
    ax.set_xlabel('Displacement (mm)')
    ax.set_ylabel('Load (N)')
    ax.legend()
    ax.grid(True)

    plt.show(block=False)
    return fig, ax, displacement_line


def update_graph(displacement_line, current_displacement, fig, ax, load_data):
    """Update the graph with the current displacement."""
    displacement_line.set_xdata([current_displacement, current_displacement])  # Move the red line
    displacement_line.set_ydata([min(load_data), max(load_data)])  # Keep it spanning the full height

    ax.relim()
    ax.autoscale_view()

    fig.canvas.flush_events()  # Ensures it updates immediately
    fig.canvas.draw()
    plt.pause(0.001)


def on_trackbar(val, cap, displacement_line, displacement_data, load_data, fig, ax):
    """Handle trackbar movement to update the video frame and graph."""
    if not cap or not cap.isOpened():
        print("Warning: Video capture is not open!")
        return

    cap.set(cv2.CAP_PROP_POS_FRAMES, val)
    ret, frame = cap.read()

    if ret:
        frame_resized = cv2.resize(frame, (800, 600))
        cv2.imshow('Slow Motion Video', frame_resized)

    if 0 <= val < len(displacement_data):
        update_graph(displacement_line, displacement_data[val], fig, ax, load_data)  # Now passes load_data


def play_video_with_displacement_graph(video_path, displacement_data, load_data):
    """Play the video and display the corresponding displacement graph."""
    global is_paused
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video")
        return

    fig, ax, displacement_line = show_graph(displacement_data, load_data)
    max_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cv2.namedWindow('Slow Motion Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Slow Motion Video', 800, 600)

    def trackbar_callback(val):
        on_trackbar(val, cap, displacement_line, displacement_data, load_data, fig, ax)  # Added load_data

    cv2.createTrackbar('Frame', 'Slow Motion Video', 0, max_frames - 1, trackbar_callback)

    while True:
        key = cv2.waitKey(1) & 0xFF  # Process key events

        if key == ord('q'):  # Quit program
            break
        elif key == ord(' '):  # Toggle pause/play
            toggle_pause()

        if not is_paused:
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            if current_frame < max_frames - 1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame + 1)
                ret, frame = cap.read()

                if ret:
                    frame_resized = cv2.resize(frame, (800, 600))
                    cv2.imshow('Slow Motion Video', frame_resized)

                    # Update red line in sync
                    if 0 <= current_frame < len(displacement_data):
                        update_graph(displacement_line, displacement_data[current_frame], fig, ax, load_data)

                    cv2.setTrackbarPos('Frame', 'Slow Motion Video', current_frame)

    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function to run the application."""
    print("Select the Excel file with displacement vs load data:")
    excel_file_path = select_file("Excel Files (*.xlsx)")
    print("Select the slow-motion video file:")
    video_file_path = select_file("Video Files (*.mp4;*.avi;*.mov)")

    displacement_data, load_data = read_displacement_vs_load_data(excel_file_path)
    if displacement_data is not None and load_data is not None:
        play_video_with_displacement_graph(video_file_path, displacement_data, load_data)


if __name__ == "__main__":
    main()
