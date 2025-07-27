from PIL import Image, ImageDraw, ImageFont

# Create a 32x32 image with white background
img = Image.new('RGBA', (32, 32), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

# Try to use a default font
try:
    font = ImageFont.truetype('arial.ttf', 14)
except IOError:
    font = ImageFont.load_default()

# Center the text 'VDA' using draw.textbbox for compatibility
text = 'VDA'
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
position = ((32 - text_width) // 2, (32 - text_height) // 2)
draw.text(position, text, fill=(0, 0, 0), font=font)

# Save as .ico
img.save('icon_placeholder.ico')

# Small test block
if __name__ == '__main__':
    print('icon_placeholder.ico created with "VDA" text.') 