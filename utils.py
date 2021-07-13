import socket

import qrcode
from PIL import Image
from sys import platform

from PySide2 import QtWidgets
from PySide2.QtCore import QBuffer, QIODevice, QPoint, QTimer, QRect, QSize
from PySide2.QtGui import QImage, QPixmap, Qt

import communication
from main import PlatformName


def clamp(n, minn, maxn):
    return n
    # return max(min(maxn, n), minn)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_computer_host_name():
    return socket.gethostname()


def get_platform_type():
    if platform == "linux" or platform == "linux2":
        return PlatformName.LINUX
    elif platform == "darwin":
        return PlatformName.MACOS
    elif platform == "win32":
        return PlatformName.WINDOW


def generate_qr_code(qr_content):
    # taking image which user wants
    # in the QR code center
    logo_link = 'app_icon_rgb.jpg'

    logo = Image.open(logo_link)

    # taking base width
    basewidth = 70

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    # taking url or text
    url = qr_content

    # addingg URL or text to QRcode
    QRcode.add_data(url)

    # generating QR code
    QRcode.make()

    # taking color name from user
    QRcolor = 'Black'

    # adding color to QR code
    QRimg = QRcode.make_image().convert('RGB')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
           (QRimg.size[1] - logo.size[1]) // 2)

    QRimg.paste(logo, pos)

    return QRimg


def pil2pixmap(im):
    if im.mode == "RGB":
        r, g, b = im.split()
        im = Image.merge("RGB", (b, g, r))
    elif im.mode == "RGBA":
        r, g, b, a = im.split()
        im = Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")

    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qim)
    return pixmap


def get_current_volume():
    result = osascript.osascript('get volume settings')
    volInfo = result[1].split(',')
    output_vol = volInfo[0].replace('output volume:', '')
    return output_vol


def show_volume_image(target_volume):
        pixmap = QPixmap(get_image_path_from_volume(target_volume))
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "png", quality=100)
        image = bytes(buffer.data().toBase64()).decode()
        html = '<img src="data:image/png;base64,{}">'.format(image)

        QtWidgets.QToolTip.showText(QPoint(communication.screenWidth / 2 - 100, communication.screenHeight - 200),
                                    html)


def get_image_path_from_volume(target_volume):
    if target_volume <= 0:
        return "volume_levelOFF.png"

    print("target volume: ", target_volume, (target_volume / 10) * 16)

    target_volume = (target_volume / 10) * 16
    if 0 < target_volume <= 10:
        return "volume_level1.png"
    elif 10 < target_volume <= 20:
        return "volume_level2.png"
    elif 20 < target_volume <= 30:
        return "volume_level3.png"
    elif 30 < target_volume <= 40:
        return "volume_level4.png"
    elif 40 < target_volume <= 50:
        return "volume_level5.png"
    elif 50 < target_volume <= 60:
        return "volume_level6.png"
    elif 60 < target_volume <= 70:
        return "volume_level7.png"
    elif 70 < target_volume <= 80:
        return "volume_level8.png"
    elif 80 < target_volume <= 90:
        return "volume_level9.png"
    elif 90 < target_volume <= 100:
        return "volume_level10.png"
    elif 100 < target_volume <= 110:
        return "volume_level11.png"
    elif 110 < target_volume <= 120:
        return "volume_level12.png"
    elif 120 < target_volume <= 130:
        return "volume_level13.png"
    elif 130 < target_volume <= 140:
        return "volume_level14.png"
    elif 140 < target_volume <= 150:
        return "volume_level15.png"
    elif target_volume > 150:
        return "volume_level16.png"


def hide_qtooltip():
    QtWidgets.QToolTip.hideText()

