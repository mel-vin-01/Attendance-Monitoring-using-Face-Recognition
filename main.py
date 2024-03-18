import cv2
import eel
import sys
import base64
import mysql.connector
from backend import *

# MySQL Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'testdb'
}

# Initialize Eel
eel.init('web')


@eel.expose
def retrieve_data():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute SQL query to retrieve data
        cursor.execute("SELECT id, name, quantity, image FROM items")
        data = cursor.fetchall()

        # Convert image bytes to base64-encoded strings
        processed_data = []
        for row in data:
            if row[3]:  # If there's an image
                image_base64 = base64.b64encode(row[3]).decode('utf-8')
                processed_row = list(row)  # Convert the tuple to a list
                processed_row[3] = image_base64  # Update the image column with base64 string
                processed_data.append(
                    tuple(processed_row))  # Convert the list back to a tuple and add to processed_data
            else:
                processed_data.append(row)  # If no image, keep the row as it is
        return processed_data

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def read_image(filename):
    with open(filename, "rb") as img_file:
        return img_file.read()


@eel.expose
def add_item(name, quantity, image_file):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Convert image to bytes
        image_bytes = read_image(image_file)

        _, img_encoded = cv2.imencode('.jpeg', face_img)
        img_encoded = img_encoded.tobytes()

        # Execute SQL query to add data
        cursor.execute("INSERT INTO items (name, quantity, image) VALUES (%s, %s, %s)", (name, quantity, image_bytes))
        connection.commit()

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@eel.expose
def update_item(id, name, quantity):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute SQL query to update data
        cursor.execute("UPDATE items SET name = %s, quantity = %s WHERE id = %s", (name, quantity, id))
        connection.commit()

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@eel.expose
def delete_item(id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute SQL query to delete data
        cursor.execute("DELETE FROM items WHERE id = %s", (id,))
        connection.commit()

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def start_camera():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to access one of the cameras.")
            return
    except Exception as e:
        print("Error:", f"Unable to access one of the cameras. {str(e)}")

    def show_frame():
        try:
            ret, frame = cap.read()

            if ret:
                img = cv2.flip(frame, 1)
                height, width, _ = img.shape

                imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                facesCurFrame = face_recognition.face_locations(imgS)

                encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    facesDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                    matchIndex = np.argmin(facesDis)

                    top, right, bottom, left = faceLoc
                    center_x = int((left + right) / 2)
                    center_y = int((top + bottom) / 2)
                    box_width = int((right - left) / 2)
                    box_height = int((bottom - top) / 2)

                    if facesDis[matchIndex] > 0.4:
                        name = classNames[matchIndex]
                        identified = f"{name}"

                        cv2.rectangle(img, (center_x - box_width, center_y - box_height),
                                      (center_x + box_width, center_y + box_height), (0, 255, 0), 2)
                        cv2.putText(img, identified, (center_x - box_width + 6, center_y - box_height - 6),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 2)

                        face_img = img[top:bottom, left:right]

                        _, img_encoded = cv2.imencode('.jpeg', face_img)
                        img_encoded = img_encoded.tobytes()

                        self.save_recognized_face(name, img_encoded)
                    else:
                        cv2.rectangle(img, (center_x - box_width, center_y - box_height),
                                      (center_x + box_width, center_y + box_height), (0, 0, 255), 2)

                image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                resize = image.resize((1080, 900))
                photo = ImageTk.PhotoImage(image=resize)
                # Assuming you have an element with id 'camera_1' to display the camera feed
                eel.update_camera(photo)  # Send the image data to frontend for display

                # Update the camera feed after a delay
                eel.sleep(1000)
                show_frame()
        except:
            print("Error:", "Unable to access one of the cameras.")
            show_frame()


start_camera()


@eel.expose
def open_new_window():
    eel.spawn(open_window)


def open_window():
    try:
        eel.init('web')
        eel.start('attendance.html', mode='chrome', size=(1100, 580))
    except Exception as e:
        err_msg = 'Could not launch a local server'
        logging.error('{}\n{}'.format(err_msg, e.args))
        show_error(title='Failed to initialise server',
                   msg=err_msg)
        sys.exit()


def start_app():
    try:
        eel.init('Web')  # path to project folder
        eel.start('index.html', size=(1100, 580))
    except Exception as e:
        err_msg = 'Could not launch a local server'
        logging.error('{}\n{}'.format(err_msg, e.args))
        show_error(title='Failed to initialise server',
                   msg=err_msg)
        sys.exit()


if __name__ == "__main__":
    start_app()
