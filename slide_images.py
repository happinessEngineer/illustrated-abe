import nltk
from nltk.tokenize import sent_tokenize
import random
from PIL import Image, ImageDraw, ImageFont
import os

def split_story_into_sentences(story):
    """
    Split a story into an array of sentences using NLTK's sentence tokenizer.
    
    Args:
        story (str): The story text to split
        
    Returns:
        list: Array of sentences from the story
    """
    # Download required NLTK data if not already present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        
    # Use NLTK's sentence tokenizer
    sentences = sent_tokenize(story)
    
    return sentences

def join_sentences_under_length(sentences, max_length=280):
    """
    Join sentences together into groups that are under a specified character length.
    
    Args:
        sentences (list): Array of sentences to join
        max_length (int): Maximum character length for each group (default 280)
        
    Returns:
        list: Array of joined sentence groups
    """
    result = []
    current_group = []
    current_length = 0
    
    for sentence in sentences:
        # Add 1 for the space between sentences
        sentence_length = len(sentence) + (1 if current_group else 0)
        
        if current_length + sentence_length <= max_length:
            current_group.append(sentence)
            current_length += sentence_length
        else:
            if current_group:
                result.append(' '.join(current_group))
            current_group = [sentence]
            current_length = len(sentence)
    
    # Add the last group if it exists
    if current_group:
        result.append(' '.join(current_group))
        
    return result

def create_slide_images(story, output_dir):    
    sentences = split_story_into_sentences(story)
    slides = join_sentences_under_length(sentences)

    print(slides)
    for i, slide in enumerate(slides):
        print(f"Slide {i+1}: {len(slide)} characters")
    
    # Define background colors to cycle through
    bg_colors = [
        (46, 196, 182),   # Soft Aqua Blue
        (180, 151, 255),  # Dreamy Lavender
        (235, 162, 113),  # Sunset Peach/Coral
        (37, 56, 88),     # Celestial Deep Blue
        (255, 111, 145)   # Soft Rose Pink
    ]
    
    # Choose a random background color from the list for all slides
    single_bg_color = random.choice(bg_colors)
    
    # Image dimensions
    width = 1024
    height = 1024
    
    # Font settings
    font_size = 60 # Reduced font size slightly
    
    # Increased spacing between lines further
    line_spacing = 35 # Increased spacing between lines further
    
    # Sparkle icon settings
    sparkle_image_path = "star.png"
    sparkle_opacity = 0.25 # 25% opacity
    top_right_sparkle_size_multiplier = 0.125 # 1/8 of width
    bottom_left_sparkle_size_multiplier = 0.166 # About 1/6 of width
    edge_padding = 40 # Padding from the image edges
    
    font = ImageFont.truetype("Quicksand-VariableFont_wght.ttf", size=font_size)
    font.set_variation_by_axes([600])  # Set weight to 600 (semi-bold for main text)
    
    for i, text in enumerate(slides):
        # Create new image with background color
        img = Image.new('RGB', (width, height), single_bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add sparkle icons
        try:
            # Load, resize, and set transparency for the top-right sparkle
            sparkle_img_tr = Image.open(sparkle_image_path).convert("RGBA")
            sparkle_size_tr = int(width * top_right_sparkle_size_multiplier)
            sparkle_img_tr = sparkle_img_tr.resize((sparkle_size_tr, sparkle_size_tr), Image.Resampling.LANCZOS)
            alpha_tr = sparkle_img_tr.getchannel('A')
            alpha_tr = alpha_tr.point(lambda i: i * sparkle_opacity)
            sparkle_img_tr.putalpha(alpha_tr)

            # Load, resize, and set transparency for the bottom-left sparkle
            sparkle_img_bl = Image.open(sparkle_image_path).convert("RGBA")
            sparkle_size_bl = int(width * bottom_left_sparkle_size_multiplier)
            sparkle_img_bl = sparkle_img_bl.resize((sparkle_size_bl, sparkle_size_bl), Image.Resampling.LANCZOS)
            alpha_bl = sparkle_img_bl.getchannel('A')
            alpha_bl = alpha_bl.point(lambda i: i * sparkle_opacity)
            sparkle_img_bl.putalpha(alpha_bl)

            # Calculate positions
            sparkle_w_tr, sparkle_h_tr = sparkle_img_tr.size
            sparkle_x_tr = width - sparkle_w_tr - edge_padding
            sparkle_y_tr = edge_padding

            sparkle_w_bl, sparkle_h_bl = sparkle_img_bl.size
            sparkle_x_bl = edge_padding
            sparkle_y_bl = height - sparkle_h_bl - edge_padding

            # Paste sparkles onto the image
            img.paste(sparkle_img_tr, (sparkle_x_tr, sparkle_y_tr), sparkle_img_tr)
            img.paste(sparkle_img_bl, (sparkle_x_bl, sparkle_y_bl), sparkle_img_bl)

        except FileNotFoundError:
            print(f"Warning: Sparkle image not found at {sparkle_image_path}. Skipping sparkles.")
        except Exception as e:
            print(f"An error occurred while processing sparkle image: {e}. Skipping sparkles.")
        
        # Wrap text to fit width
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= width - 100:  # Leave 50px margin on each side
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total text height
        total_height = 0
        line_heights = []
        for line in lines:
            # Calculate line height based on the font that will be used for that segment
            # This is complex as it depends on which parts are quotes.
            # For simplicity, let's approximate using the regular font height for total block height calculation
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_height += line_height
        
        # Calculate starting y position to center text vertically (including line spacing)
        total_block_height = total_height + (len(lines) - 1) * line_spacing # Total height including spacing
        y = (height - total_block_height) // 2
        
        # Draw each line
        for line in lines:
            # Calculate the starting x position to center the line
            line_width_regular = draw.textbbox((0,0), line, font=font)[2] - draw.textbbox((0,0), line, font=font)[0] # Use regular font for overall centering
            start_x = (width - line_width_regular) // 2
            
            # Draw the entire line in white with the regular font first
            draw.text((start_x, y), line, font=font, fill=(255, 255, 255))
            
            # Move down for the next line
            # Use the approximate line height calculated earlier plus spacing
            current_line_index = lines.index(line) # Get index of current line
            y += line_heights[current_line_index] + line_spacing;
        
        # Save image
        output_path = os.path.join(output_dir, f"slide_{i+1:03d}.jpg")
        img.save(output_path)
        print(f"Created {output_path}")

    return len(slides)


# story = "Angela Martinez, a 35-year-old Project Manager at a bustling tech startup in Santa Monica, leans back in her kitchen chair one Tuesday evening and watches her seven-year-old daughter, Mia, fidget with crayons at the little table by the window. Mia is starting second grade next week at a new school in Echo Park, and tonight she\u2019s worrying about making friends. As a parent, Angela feels the tug of anxiety too\u2014but she remembers something she recently learned from Abraham-Hicks: \u201cTrust their natural well-being.\u201d\n\nAcross from her sits Daniel Carter, Angela\u2019s husband and a 36-year-old architect, quietly sipping his green tea. He smiles at Angela. \u201cYou know,\u201d he says, \u201cshe always figures things out.\u201d Angela takes a slow breath and nods. Instead of jumping in with solutions\u2014\u201cDon\u2019t worry, honey, you\u2019ll be fine\u201d\u2014she gently asks Mia, \u201cWhat\u2019s one exciting thing you\u2019d like about your new classroom?\u201d Mia\u2019s eyes brighten as she imagines a bright yellow reading corner and group art projects.\n\nOver the next few days, Angela practices focusing on her daughter\u2019s natural resilience rather than her fears. On the drive to school, she chats with Mia about her favorite storybooks and reminds herself that life inherently supports well-being. She lets go of the urge to control every detail\u2014the seating chart, recess buddy assignments, lunch menu\u2014and simply affirms, \u201cI trust that you\u2019re guided toward friends who love having you around.\u201d\n\nOn Mia\u2019s first morning, the little girl bounds off the bus with a grin that stretches ear to ear. She\u2019s made two new pals already\u2014one who loves dinosaurs as much as she does, another who shares her passion for mermaids. At the dinner table, Mia excitedly sketches a plan for tomorrow\u2019s art project. Angela catches Daniel\u2019s eye, and they share a satisfied glance. By trusting their daughter\u2019s natural well-being\u2014and releasing the need to micromanage\u2014they\u2019ve watched her thrive exactly as she was meant to."
# create_slide_images(story, "8")
