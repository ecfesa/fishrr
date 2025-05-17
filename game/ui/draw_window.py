import pygame
import game.assets as assets
import game.globals as g
from game.state import GAME_STATE_INSTANCE

# Animation state for the bulb
_is_bulb_animating = False
_bulb_animation_alpha = 255 # Current alpha value for the animation
BULB_FADE_RATE = 15         # How much alpha decreases per frame (higher is faster fade)
_bulb_animation_start_time = None # Timestamp for when the animation should start after delay
_bulb_animation_pending = False   # True if a flash is requested and delay is active
BULB_ANIMATION_DELAY = 500     # Delay in milliseconds (1 second)

# --- New: Variables for bordered bulb ---
_MODIFIED_BULB_IMAGE = None
_bordered_bulb_created = False
_original_bulb_rect_for_pos = None # To store original bulb dimensions for consistent positioning reference

# --- New: Variables for "New thought" text box animation ---
_is_text_box_animating = False
_text_box_alpha = 0
_text_box_appearance_time = None  # When the text box fully appeared (pop-in)
_text_box_fade_start_time = None  # When fade-out should begin
_trigger_text_box = False         # Flag to initiate text box sequence

TEXT_BOX_STAY_DURATION = 4000    # 4 seconds
TEXT_BOX_FADE_OUT_DURATION = 1000 # 1 second
TEXT_BOX_PADDING = 10
TEXT_BOX_BORDER_THICKNESS = 2
TEXT_BOX_FONT = None # Will be initialized with assets.TERMINAL_FONT

def _ensure_bordered_bulb_created():
    global _MODIFIED_BULB_IMAGE, _bordered_bulb_created, _original_bulb_rect_for_pos, TEXT_BOX_FONT
    if not _bordered_bulb_created:
        if not assets.BULB_IMAGE:
            return False # Asset not ready

        # Initialize font for text box here too, as assets are available
        if TEXT_BOX_FONT is None and assets.TERMINAL_FONT:
            TEXT_BOX_FONT = assets.TERMINAL_FONT

        padding = 5
        border_thickness = 2

        _original_bulb_rect_for_pos = assets.BULB_IMAGE.get_rect() # Store original for positioning logic
        
        padded_width = _original_bulb_rect_for_pos.width + 2 * padding
        padded_height = _original_bulb_rect_for_pos.height + 2 * padding

        total_width = padded_width + 2 * border_thickness
        total_height = padded_height + 2 * border_thickness

        final_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        final_surface.fill((0,0,0,0)) # Start with a fully transparent surface

        # 1. Draw the white border rectangle (outermost)
        pygame.draw.rect(final_surface, g.WHITE, final_surface.get_rect(), border_thickness)

        # 2. Draw the black background rectangle (inside the white border)
        black_bg_rect = pygame.Rect(border_thickness, border_thickness, padded_width, padded_height)
        pygame.draw.rect(final_surface, g.BLACK, black_bg_rect)
        
        # 3. Blit the original bulb image onto the black background
        bulb_blit_x = border_thickness + padding
        bulb_blit_y = border_thickness + padding
        final_surface.blit(assets.BULB_IMAGE, (bulb_blit_x, bulb_blit_y))
        
        _MODIFIED_BULB_IMAGE = final_surface
        _bordered_bulb_created = True
    return _bordered_bulb_created

def draw_logo():
    g.WIN.blit(assets.LOGO_TRANSPARENT_64PX, (g.WIN.get_width() - (64+g.PADDING), g.PADDING))

def draw_terminal():
    buffer = g.SYSTEM.get_buffer()
    font = assets.TERMINAL_FONT  # Assuming you have a font in assets
    y_offset = g.PADDING  # Starting Y position for the text
    line_height = font.get_linesize()

    for i, chars in enumerate(buffer):
        line = "".join(chars)
        text_surface = font.render(line, True, g.WHITE)  # Assuming g.WHITE is defined
        g.WIN.blit(text_surface, (g.PADDING, y_offset + i * line_height))

def draw_window():
    global _is_bulb_animating, _bulb_animation_alpha, _bulb_animation_start_time, _bulb_animation_pending
    global _is_text_box_animating, _text_box_alpha, _text_box_appearance_time, _text_box_fade_start_time, _trigger_text_box

    # Ensure bordered bulb is created (and text box font is set)
    if not _bordered_bulb_created:
        if not _ensure_bordered_bulb_created():
            # Fallback or wait if assets not ready, though typically they should be by draw time
            pass # For now, proceed, original bulb might be used if creation failed

    current_display_bulb_surface = _MODIFIED_BULB_IMAGE if _MODIFIED_BULB_IMAGE else assets.BULB_IMAGE
    
    g.WIN.fill(g.BLACK)
    draw_logo()
    draw_terminal() # Call the function to draw the terminal

    # Check if a new bulb flash is requested
    if GAME_STATE_INSTANCE.show_bulb and not _is_bulb_animating and not _bulb_animation_pending:
        _bulb_animation_pending = True
        _bulb_animation_start_time = pygame.time.get_ticks() + BULB_ANIMATION_DELAY
        GAME_STATE_INSTANCE.show_bulb = False # Reset trigger, delay has started

    # Check if a pending animation is ready to start after delay
    if _bulb_animation_pending and pygame.time.get_ticks() >= _bulb_animation_start_time:
        pygame.mixer.Sound.play(assets.NEW_TIP_SOUND)
        _is_bulb_animating = True
        _bulb_animation_alpha = 255  # Pop in: Start at full opacity
        _bulb_animation_pending = False
        _bulb_animation_start_time = None # Clear the start time

    # Handle active bulb animation (drawing and fading)
    if _is_bulb_animating:
        if current_display_bulb_surface: # Check if surface is available
            temp_bulb_surface = current_display_bulb_surface.copy()
            temp_bulb_surface.set_alpha(_bulb_animation_alpha)
            
            # Original positioning logic for bulb
            # This used '64' which was likely assumed width of original bulb image or a reference.
            # To keep the visual placement consistent for the *content* of the bulb,
            # we adjust the position for the new larger bordered surface.
            # Original top-left if bulb was 64px wide:
            ref_bulb_x = g.WIN.get_width() - (64 + g.PADDING) 
            ref_bulb_y = g.WIN.get_height() - 100 - g.PADDING 

            # If original_bulb_rect_for_pos is available, use it for more precise adjustment
            # This ensures the *content* of the bulb stays roughly where a 64px bulb would have been top-left aligned.
            actual_bulb_content_width = _original_bulb_rect_for_pos.width if _original_bulb_rect_for_pos else 64
            
            # Calculate blit position for the new (potentially larger) surface
            # so its content aligns with the reference point.
            blit_x = ref_bulb_x - (current_display_bulb_surface.get_width() - actual_bulb_content_width) / 2
            # A similar adjustment for Y if 100 was assumed height (let's assume 100 related to a fixed point, not bulb height)
            # For simplicity, let's stick to original ref_bulb_y for top of new surface if it's simpler, or adjust.
            # The original '100' is a bit magical. If it represented bulb height for bottom alignment:
            # ref_bulb_y = g.WIN.get_height() - (current_display_bulb_surface.get_height()) - g.PADDING
            # For now, let's use the original Y as the top of the drawn surface:
            blit_y = ref_bulb_y

            g.WIN.blit(temp_bulb_surface, (blit_x, blit_y))

            _bulb_animation_alpha -= BULB_FADE_RATE
            if _bulb_animation_alpha <= 0:
                _bulb_animation_alpha = 0
                _is_bulb_animating = False
                if not _is_text_box_animating and _text_box_alpha == 0: # Only trigger if not already running/visible
                    _trigger_text_box = True
        else: # Fallback if bulb surface somehow not ready
            _is_bulb_animating = False # Avoid infinite loop

    # --- New: Handle Text Box Animation ---
    current_time = pygame.time.get_ticks()

    if _trigger_text_box:
        _is_text_box_animating = True
        _text_box_alpha = 255  # Pop in
        _text_box_appearance_time = current_time
        _text_box_fade_start_time = current_time + TEXT_BOX_STAY_DURATION
        _trigger_text_box = False # Reset trigger

    if _is_text_box_animating and TEXT_BOX_FONT:
        # Prepare text surfaces
        line1_surface = TEXT_BOX_FONT.render("New", True, g.WHITE)
        line2_surface = TEXT_BOX_FONT.render("thought", True, g.WHITE)
        
        # Calculate dimensions for the text box
        text_lines_height = line1_surface.get_height() + line2_surface.get_height() # Simple sum for two lines
        text_max_width = max(line1_surface.get_width(), line2_surface.get_width())

        box_inner_width = text_max_width + 2 * TEXT_BOX_PADDING
        box_inner_height = text_lines_height + 2 * TEXT_BOX_PADDING 
        
        box_outer_width = box_inner_width + 2 * TEXT_BOX_BORDER_THICKNESS
        box_outer_height = box_inner_height + 2 * TEXT_BOX_BORDER_THICKNESS

        # Create the text box surface for alpha blending
        text_box_base_surface = pygame.Surface((box_outer_width, box_outer_height), pygame.SRCALPHA)
        text_box_base_surface.fill((0,0,0,0)) # Fully transparent

        # Draw border (white)
        pygame.draw.rect(text_box_base_surface, g.WHITE, text_box_base_surface.get_rect(), TEXT_BOX_BORDER_THICKNESS)
        # Draw background (black)
        pygame.draw.rect(text_box_base_surface, g.BLACK, 
                         (TEXT_BOX_BORDER_THICKNESS, TEXT_BOX_BORDER_THICKNESS, box_inner_width, box_inner_height))

        # Blit text lines onto the text_box_base_surface
        line1_x = TEXT_BOX_BORDER_THICKNESS + TEXT_BOX_PADDING
        line1_y = TEXT_BOX_BORDER_THICKNESS + TEXT_BOX_PADDING
        text_box_base_surface.blit(line1_surface, (line1_x, line1_y))
        
        line2_y = line1_y + line1_surface.get_height() # Position second line below first
        text_box_base_surface.blit(line2_surface, (line1_x, line2_y))

        # Determine position for the text box to be centered on where the bulb was
        # Use the same surface that was displayed for the bulb (bordered or original)
        bulb_displayed_surface = _MODIFIED_BULB_IMAGE if _MODIFIED_BULB_IMAGE else assets.BULB_IMAGE

        if bulb_displayed_surface:
            # Reference X for the bulb's content area (based on a 64px logical space)
            bulb_content_area_ref_x = g.WIN.get_width() - (64 + g.PADDING)
            # Reference Y for the top of the bulb surface
            bulb_content_area_ref_y = g.WIN.get_height() - 100 - g.PADDING

            # Actual width of the bulb's core content (e.g., the image part, not border/padding)
            # This matches the logic used when drawing the bulb.
            actual_core_bulb_width = _original_bulb_rect_for_pos.width if _original_bulb_rect_for_pos else 64
            
            # Top-left X where the bulb_displayed_surface was drawn
            # This calculation ensures the 'actual_core_bulb_width' part is positioned correctly
            # relative to bulb_content_area_ref_x, accommodating the full surface width.
            drawn_bulb_tl_x = bulb_content_area_ref_x - (bulb_displayed_surface.get_width() - actual_core_bulb_width) / 2
            
            # Top-left Y where the bulb_displayed_surface was drawn
            drawn_bulb_tl_y = bulb_content_area_ref_y

            # Center of the drawn bulb_displayed_surface
            drawn_bulb_center_x = drawn_bulb_tl_x + bulb_displayed_surface.get_width() / 2
            drawn_bulb_center_y = drawn_bulb_tl_y + bulb_displayed_surface.get_height() / 2

            # Position the text box so its center aligns with the bulb's center
            text_box_final_x = drawn_bulb_center_x - box_outer_width / 2
            text_box_final_y = drawn_bulb_center_y - box_outer_height / 2
        else:
            # Fallback: if no bulb surface info, center text box on screen (should ideally not happen)
            text_box_final_x = (g.WIN.get_width() - box_outer_width) / 2
            text_box_final_y = (g.WIN.get_height() - box_outer_height) / 2

        # Update alpha for fade out
        if current_time >= _text_box_fade_start_time:
            elapsed_fade_time = current_time - _text_box_fade_start_time
            if elapsed_fade_time >= TEXT_BOX_FADE_OUT_DURATION:
                _text_box_alpha = 0
            else:
                _text_box_alpha = 255 * (1 - (elapsed_fade_time / TEXT_BOX_FADE_OUT_DURATION))
        
        _text_box_alpha = max(0, min(255, int(_text_box_alpha)))

        if _text_box_alpha > 0:
            text_box_base_surface.set_alpha(_text_box_alpha)
            g.WIN.blit(text_box_base_surface, (text_box_final_x, text_box_final_y))
        else: # Animation finished
            _is_text_box_animating = False
            # Clear times for potential re-trigger, though current logic prevents immediate re-trigger
            _text_box_appearance_time = None 
            _text_box_fade_start_time = None


    pygame.display.update()