import os
import time
from pathlib import Path
from PIL import ImageGrab, Image
import tkinter as tk

# Thư mục tạm để lưu ảnh chụp màn hình
TMP_DIR = Path(__file__).resolve().parent.parent / "data" / "tmp"

def _ensure_tmp_dir() -> None:
    """Tạo thư mục tạm nếu chưa tồn tại."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)

def _save_temp_image(img: Image.Image) -> str:
    """Lưu ảnh tạm thời và trả về đường dẫn file.

    Args:
        img: Pillow Image object.
    Returns:
        Đường dẫn tuyệt đối tới file PNG đã lưu.
    """
    _ensure_tmp_dir()
    timestamp = int(time.time() * 1000)
    filename = f"screenshot_{timestamp}.png"
    path = TMP_DIR / filename
    img.save(path, format="PNG")
    return str(path)

def paste_from_clipboard() -> str | None:
    """Lấy ảnh từ clipboard (Ctrl+V).
    Trả về đường dẫn file tạm nếu có ảnh; ngược lại ``None``.
    """
    img = ImageGrab.grabclipboard()
    if isinstance(img, Image.Image):
        return _save_temp_image(img)
    return None

def capture_region() -> str | None:
    """Hiển thị overlay fullscreen, cho người dùng kéo chọn vùng màn hình.
    Sau khi người dùng thả chuột, ảnh được chụp và lưu thành file tạm.
    Returns
    -------
    str | None
        Đường dẫn tới file PNG nếu thành công, ``None`` nếu người dùng hủy.
    """
    # Tạo một cửa sổ Tk không hiển thị tiêu đề, fullscreen, đen mờ
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    canvas = tk.Canvas(root, cursor="cross", bg="gray85")
    canvas.pack(fill=tk.BOTH, expand=True)

    rect_id = None
    start_x = start_y = 0

    def on_button_press(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y,
                                          outline="red", width=2)

    def on_move(event):
        if rect_id:
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_button_release(event):
        # Khi thả chuột, dừng vòng lặp
        root.quit()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    root.mainloop()

    # Lấy tọa độ cuối cùng
    if not rect_id:
        return None
    x1, y1, x2, y2 = canvas.coords(rect_id)
    root.destroy()
    if x1 == x2 or y1 == y2:
        return None
    # Pillow expects (left, upper, right, lower) as ints
    bbox = (int(x1), int(y1), int(x2), int(y2))
    img = ImageGrab.grab(bbox=bbox)
    return _save_temp_image(img)

