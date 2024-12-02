import logging
import sys

import webview
from api import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)


def start_server():
    app = create_app()
    app.run(port=5000, debug=True, use_reloader=False)


def create_window_and_start(webview_ready_event):
    window = webview.create_window('Interactive File Renamer',
                                   'http://127.0.0.1:5000',
                                   width=800,
                                   height=600,
                                   resizable=True, background_color='#FFFFFF',
                                   text_select=True)  # Enable text selection
    webview_ready_event.set()  # Signal that the webview window is ready
    webview.start()


if __name__ == "__main__":
    # Start Flask server in a separate process
    import multiprocessing

    webview_ready_event = multiprocessing.Event()
    flask_process = multiprocessing.Process(target=start_server, daemon=True)
    webview_process = multiprocessing.Process(target=create_window_and_start, args=(webview_ready_event,), daemon=True)

    flask_process.start()
    webview_process.start()

    webview_ready_event.wait()  # Wait for the window to be created

    # The window is now accessible via webview.windows[0], but interaction should happen via a thread
    # or from the function that is executed after webview.start()

    try:
        webview_process.join()  # Make main process wait for webview_process finish
    except KeyboardInterrupt:
        flask_process.terminate()
        webview_process.terminate()
        print('\nOperation interrupted by user.')
