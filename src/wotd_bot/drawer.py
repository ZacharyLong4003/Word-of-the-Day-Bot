from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# image_path="C:\\Users\\zane1\\Desktop\\Don Cheadle Bot\\the_don.png"

def draw_text_on_image(text, image_path,
                       font_size=60, fixed_font_size=60, font_color="white", outline_color="black",
                       output_path="output.jpg", outline_width=2):
    try:
        image = Image.open(image_path)
    except OSError:
        raise OSError(f"Could not open image file: {image_path}")

    try:
        font_path = Path(__file__).resolve().parents[2] / "impact.ttf"
        font = ImageFont.truetype(str(font_path), font_size)
        fixed_font = ImageFont.truetype(str(font_path), fixed_font_size)
    except OSError:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
            fixed_font = ImageFont.truetype("arialbd.ttf", fixed_font_size)
        except OSError:
            raise OSError("Could not load font. Please install a bold font or provide the path to 'impact.ttf'.")

    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    def text_dimensions(value, selected_font):
        left, top, right, bottom = draw.textbbox((0, 0), value, font=selected_font)
        return right - left, bottom - top

    fixed_text_lines = ["Don Cheadle Word", "of the Day"]
    fixed_text_height = 0
    for line in fixed_text_lines:
        fixed_text_width, line_height = text_dimensions(line, fixed_font)
        fixed_text_height += line_height
    fixed_text_height += len(fixed_text_lines) - 1
    fixed_y_pos = 10

    y_offset = fixed_y_pos
    for line in fixed_text_lines:
        fixed_text_width, line_height = text_dimensions(line, fixed_font)
        fixed_x_pos = (image_width - fixed_text_width) // 2
        draw.text((fixed_x_pos - outline_width, y_offset), line, fill=outline_color, font=fixed_font)
        draw.text((fixed_x_pos + outline_width, y_offset), line, fill=outline_color, font=fixed_font)
        draw.text((fixed_x_pos, y_offset - outline_width), line, fill=outline_color, font=fixed_font)
        draw.text((fixed_x_pos, y_offset + outline_width), line, fill=outline_color, font=fixed_font)
        draw.text((fixed_x_pos, y_offset), line, fill=font_color, font=fixed_font)
        y_offset += line_height + 1

    text_spacing = 4
    text_left, text_top, text_right, text_bottom = draw.multiline_textbbox(
        (0, 0), text, font=font, spacing=text_spacing, align="center"
    )
    text_width = text_right - text_left
    text_height = text_bottom - text_top
    x_pos = (image_width - text_width) // 2 - text_left
    y_pos = image_height - text_height - 20 - text_top

    draw.multiline_text(
        (x_pos, y_pos),
        text,
        fill=font_color,
        font=font,
        spacing=text_spacing,
        align="center",
        stroke_width=outline_width,
        stroke_fill=outline_color,
    )

    try:
        image.save(output_path)
    except OSError:
        raise OSError(f"Could not save image to: {output_path}")

    print(f"Text with outline added to image. Saved as: {output_path}")

