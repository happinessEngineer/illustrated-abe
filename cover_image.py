from PIL import Image, ImageDraw, ImageFont
import random

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]  # right - left
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines

def create_cover_image(
    image_path,
    output_path,
    text,
    subtitle="A Modern Day Fable",
    title_font_path="Quicksand-VariableFont_wght.ttf",
    subtitle_font_path="Lora-Italic-VariableFont_wght.ttf",
    font_size=56,
    subtitle_font_size=40,
    banner_opacity=180,
    banner_color=(0,0,0),
    text_color=(255,255,255,255),
    text_margin=20,
    banner_padding=30,
    shadow_height=60
):
    # Load image and font
    base = Image.open(image_path).convert("RGBA")
    width, height = base.size
    try:
        title_font = ImageFont.truetype(title_font_path, size=font_size)
        title_font.set_variation_by_axes([700])  # Set weight to 700 (bold)
        subtitle_font = ImageFont.truetype(subtitle_font_path, size=subtitle_font_size)
        subtitle_font.set_variation_by_axes([600])
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Create golden gradient overlay
    gradient = Image.new('RGBA', (width, height), (0,0,0,0))
    gradient_draw = ImageDraw.Draw(gradient)
    golden_color = (255, 215, 0, 25)  # Reduced opacity from 40 to 25
    
    # Create a vertical gradient
    for y in range(height):
        # Calculate opacity based on position (more intense at the bottom)
        opacity = int(25 * (1 - y / height))  # Reduced max opacity from 40 to 25
        color = (*golden_color[:3], opacity)
        gradient_draw.line([(0, y), (width, y)], fill=color)

    # Apply gradient to base image
    base = Image.alpha_composite(base, gradient)

    # Add large, very transparent sparkle to base image
    sparkle_image_path = "star.png"
    try:
        sparkle_img = Image.open(sparkle_image_path).convert("RGBA")
        
        # Resize sparkle image to be about 1/8 of the width
        sparkle_size = width // 8
        sparkle_img = sparkle_img.resize((sparkle_size, sparkle_size), Image.Resampling.LANCZOS)
        
        # Make sparkle very transparent (25% opacity)
        alpha = sparkle_img.getchannel('A')
        alpha = alpha.point(lambda i: i * 0.25) # Adjust opacity (0.25 means 25% opacity)
        sparkle_img.putalpha(alpha)
        
        sparkle_w, sparkle_h = sparkle_img.size
        
        # Calculate position for the top right corner
        padding = 20 # Adjust padding from the edge as needed
        sparkle_x = width - sparkle_w - padding
        sparkle_y = padding
        
        # Paste sparkle onto the base image using itself as a mask for transparency
        base.paste(sparkle_img, (sparkle_x, sparkle_y), sparkle_img)

    except FileNotFoundError:
        print(f"Warning: Sparkle image not found at {sparkle_image_path}. Skipping large sparkle.")
    except Exception as e:
        print(f"An error occurred while processing the large sparkle image: {e}")

    overlay = Image.new('RGBA', base.size, (255,255,255,0))
    draw = ImageDraw.Draw(overlay)

    max_text_width = width - 2 * banner_padding - 2 * text_margin
    lines = wrap_text(text, title_font, max_text_width, draw)
    
    # Get line height using textbbox
    bbox = draw.textbbox((0, 0), "Ay", font=title_font)
    line_height = bbox[3] - bbox[1]  # bottom - top
    
    # Get subtitle height
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
    
    # Calculate total height including bottom padding
    total_text_height = len(lines) * line_height + (len(lines)-1) * 8 + subtitle_height + 32  # Increased spacing between title and subtitle
    banner_height = total_text_height + 2 * text_margin + text_margin  # Added extra text_margin for bottom padding

    # Position banner at bottom
    banner_bottom = height
    banner_top = banner_bottom - banner_height

    # Draw banner
    draw.rectangle([(0, banner_top), (width, banner_bottom)], fill=(*banner_color, banner_opacity))

    # Draw subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_h = subtitle_bbox[3] - subtitle_bbox[1] # Get subtitle height
    subtitle_x = (width - subtitle_w) // 2
    subtitle_y = banner_top + text_margin
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=text_color)

    # Add another slightly larger, very transparent sparkle on the left above the banner
    try:
        sparkle_image_path = "star.png"
        sparkle_img_left = Image.open(sparkle_image_path).convert("RGBA")
        
        # Resize sparkle image to be slightly larger (about 1/6 of the width)
        sparkle_size_left = width // 6
        sparkle_img_left = sparkle_img_left.resize((sparkle_size_left, sparkle_size_left), Image.Resampling.LANCZOS)
        
        # Make sparkle very transparent (25% opacity)
        alpha_left = sparkle_img_left.getchannel('A')
        alpha_left = alpha_left.point(lambda i: i * 0.35) # Adjust opacity (0.25 means 25% opacity)
        sparkle_img_left.putalpha(alpha_left)
        
        sparkle_w_left, sparkle_h_left = sparkle_img_left.size
        
        # Calculate position on the left, just above the banner
        padding_left = 30 # Adjust padding from the left edge as needed
        spacing_above_banner = 20 # Adjust spacing above the banner
        sparkle_x_left = padding_left
        sparkle_y_left = banner_top - sparkle_h_left - spacing_above_banner
        
        # Paste sparkle onto the base image using itself as a mask for transparency
        base.paste(sparkle_img_left, (sparkle_x_left, sparkle_y_left), sparkle_img_left)
        
    except FileNotFoundError:
        print(f"Warning: Sparkle image not found at {sparkle_image_path}. Skipping left sparkle.")
    except Exception as e:
        print(f"An error occurred while processing the left sparkle image: {e}")

    # Create glow effect for title
    glow_overlay = Image.new('RGBA', base.size, (0,0,0,0))
    glow_draw = ImageDraw.Draw(glow_overlay)
    glow_color = random.choice([
        (46, 196, 182, 255),   # Soft Aqua Blue
        (180, 151, 255, 255),  # Dreamy Lavender
        (235, 162, 113, 255),  # Sunset Peach/Coral
        (37, 56, 88, 255),     # Celestial Deep Blue
        (255, 111, 145, 255)   # Soft Rose Pink
    ])

    # Draw wrapped text with glow
    cur_y = subtitle_y + subtitle_height + 32  # Increased spacing after subtitle
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_w = bbox[2] - bbox[0]  # right - left
        text_x = (width - text_w) // 2
        
        # Draw glow effect (multiple passes with different offsets)
        offsets = [
            (0,0), (1,0), (-1,0), (0,1), (0,-1),
            (1,1), (-1,-1), (1,-1), (-1,1),
            (2,0), (-2,0), (0,2), (0,-2),
            (2,2), (-2,-2), (2,-2), (-2,2),
            (3,0), (-3,0), (0,3), (0,-3),
            (3,3), (-3,-3), (3,-3), (3,-3),
            (4,0), (-4,0), (0,4), (0,-4),
            (4,4), (-4,-4), (4,-4), (-4,4)
        ]
        for offset in offsets:
            glow_draw.text((text_x + offset[0], cur_y + offset[1]), line, font=title_font, fill=glow_color)
        
        # Draw main text
        draw.text((text_x, cur_y), line, font=title_font, fill=text_color)
        cur_y += line_height + 8

    # Combine all layers
    out = Image.alpha_composite(base, glow_overlay) # Start with base and glow
    out = Image.alpha_composite(out, overlay) # Add main text/banner layer
    out.convert("RGB").save(output_path)
    print("Saved:", output_path)


# from pathlib import Path
# image_path = Path("6") / "cover.png"
# output_path = Path("6") / "cover-with-text.jpg"

# create_cover_image(
#     image_path=image_path,
#     output_path=output_path,
#     text="Releasing Resistance: Butcher\u2019s 50-Year Path to Forgiveness"
# )