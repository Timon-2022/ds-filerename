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

    @webview.expose()  # Expose the API function here
    def chooseDirectory():
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return None


def create_window_and_start(webview_ready_event):
    window = webview.create_window('Interactive File Renamer',
                                   'http://127.0.0.1:5000',
                                   width=800,
                                   height=600,
                                   resizable=True, background_color='#FFFFFF',
                                   text_select=True)  # Enable text selection
    def expose_api(): # Expose after webview.start()
        print("Exposing chooseDirectory API...")
        try:
            @window.expose
            def chooseDirectory():
                print("chooseDirectory called from JS!")  # Debug print
                result = window.create_file_dialog(webview.FOLDER_DIALOG)
                if result and len(result) > 0:
                    print(f"Selected directory: {result[0]}")  # Debug print
                    return result[0]
                print("No directory selected.")  # Debug print
                return None
        except Exception as e:
            print(f"Error exposing API: {e}")

    webview.start(func=expose_api)  #Start and then expose
    webview_ready_event.set()

    webview_ready_event.set()  # Signal that the webview window is ready (and expose is done)



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
