import asyncio, pygame, random, math

# Game constants
CELL_SIZE = 20
GRID_WIDTH = 22
GRID_HEIGHT = 22
MARGIN = 2  # Margin at the top of the screen 
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * (GRID_HEIGHT+ MARGIN)
BRICK_WIDTH = 50
BRICK_HEIGHT = 25
START_Y = CELL_SIZE * MARGIN 
score = 0
apple_number = 0
star_number = 0
is_paused = False
is_muted = False

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (30, 140, 30)
RED = (200, 0, 0)
LIGHT_RED = (255, 100, 100)
DARK_GRAY = (100, 100, 100)
GRAY = (150, 150, 150)
BLUE = (155, 255, 225)
YELLOW = (250, 255, 80)

async def main():
    pygame.init()
    # Set the game window icon
    icon_surface = pygame.image.load("assets/icon.png")
    pygame.display.set_icon(icon_surface)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    small_font = pygame.font.SysFont(None, 22)
    title_font = pygame.font.SysFont(None, 50, bold=True)
    instruction_font = pygame.font.SysFont(None, 18) 

    # Initialize pygame mixer and play background music
    pygame.mixer.init()
    pygame.mixer.music.load("assets/bgmusic.ogg")
    pygame.mixer.music.play(-1)

    # Draw the background
    def draw_background():
        for y in range(START_Y, SCREEN_HEIGHT, BRICK_HEIGHT):
            offset = 0 if (y // BRICK_HEIGHT) % 2 == 0 else BRICK_WIDTH // 2
            for x in range(-offset, SCREEN_WIDTH, BRICK_WIDTH):
                brick_rect = pygame.Rect(x, y, BRICK_WIDTH-2, BRICK_HEIGHT-2)
                pygame.draw.rect(screen, GRAY, brick_rect)

    # Function to draw the instruction screen
    def draw_instruction_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT):
        screen.fill(GRAY)
            
        # --- Decorative moving snakes at top and bottom ---
        # Animation: use time to move the snakes
        t = pygame.time.get_ticks() // 10  # speed factor

        # Snake parameters
        deco_snake_len = 22
        deco_snake_spacing = CELL_SIZE
        deco_snake_size = CELL_SIZE - 4

        # Top snake (moves right to left, wraps around, no head, just body)
        top_y = CELL_SIZE // 2 + 2
        for i in range(deco_snake_len):
            x = (SCREEN_WIDTH - ((t // 2) % (SCREEN_WIDTH + deco_snake_len * deco_snake_spacing)) - i * deco_snake_spacing + deco_snake_len * deco_snake_spacing // 2)
            x = x % SCREEN_WIDTH  # Wrap around
            center = (x, top_y)
            color = DARK_GREEN if i % 2 else GREEN
            pygame.draw.circle(screen, color, center, deco_snake_size // 2)

        # Bottom snake (moves left to right, wraps around, no head, just body)
        bottom_y = SCREEN_HEIGHT - CELL_SIZE // 2 - 2
        for i in range(deco_snake_len):
            x = ((t // 2) % (SCREEN_WIDTH + deco_snake_len * deco_snake_spacing)) + i * deco_snake_spacing - deco_snake_len * deco_snake_spacing // 2
            x = x % SCREEN_WIDTH  # Wrap around
            center = (x, bottom_y)
            color = DARK_GREEN if i % 2 else GREEN
            pygame.draw.circle(screen, color, center, deco_snake_size // 2)
                
        title = title_font.render("~~~Snake~~~", True, DARK_GREEN)
        instructions = [
            " How to Play",
            "   - You are the snake. Glide around the screen like a ninja.",
            "   - Gobble up apples to grow loooonger.",
            "   - Don't crash into walls or your own tail—it's an instant KO!",
            "   - Watch out for bombs! Touch one and it's lights out.",
            "   - Spot a star and eat it to shrink your body!",
            "   - Use the arrow keys to glide: Up, Down, Left, Right.",
            "   - The more you munch, the speedier you get!", 
            "   - Survive and chase that high score."
        ]
        y = SCREEN_HEIGHT // 6
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(title, title_rect)
        y += 60

        for line in instructions:
            text = instruction_font.render(line, True, BLACK)
            text_rect = text.get_rect()
            text_rect.topleft = (20, y)
            screen.blit(text, text_rect)
            y += 25

        # Draw Play button with rounded corners
        play_rect = pygame.Rect((SCREEN_WIDTH - 120) // 2, y + 25, 120, 35)
        pygame.draw.rect(screen, DARK_GRAY, play_rect, border_radius=8)
        play_text = small_font.render("Play", True, BLUE)
        play_text_rect = play_text.get_rect(center=play_rect.center)
        screen.blit(play_text, play_text_rect)
        return play_rect

    # Function to draw the mute button
    def draw_mute_button(surface, rect, is_muted):
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=8)
        cx, cy = rect.center
        if is_muted:
            # Draw muted icon (speaker with X)
            pygame.draw.polygon(surface, BLUE, [
                (cx - 6, cy - 4), (cx - 1, cy - 4), (cx + 3, cy - 8),
                (cx + 3, cy + 8), (cx - 1, cy + 4), (cx - 6, cy + 4)
            ])
            pygame.draw.line(surface, RED, (cx + 4, cy - 6), (cx + 10, cy + 6), 2)
            pygame.draw.line(surface, RED, (cx + 4, cy + 6), (cx + 10, cy - 6), 2)
        else:
            # Draw speaker icon
            pygame.draw.polygon(surface, BLUE, [
                (cx - 6, cy - 4), (cx - 1, cy - 4), (cx + 3, cy - 8),
                (cx + 3, cy + 8), (cx - 1, cy + 4), (cx - 6, cy + 4)
            ])
            # Sound waves: 3 straight lines
            pygame.draw.line(surface, BLUE, (cx + 6, cy - 6), (cx + 12, cy - 10), 1)
            pygame.draw.line(surface, BLUE, (cx + 7, cy), (cx + 13, cy), 1)
            pygame.draw.line(surface, BLUE, (cx + 6, cy + 6), (cx + 12, cy + 10), 1)

    # Function to draw the pause/play button
    def draw_pause_button(surface, rect, is_paused):
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=8)
        # Draw pause or play icon
        cx, cy = rect.center
        if is_paused:
            # Draw play icon (triangle)
            points = [
                (cx - 4, cy - 7),
                (cx - 4, cy + 7),
                (cx + 6, cy)
            ]
            pygame.draw.polygon(surface, BLUE, points)
        else:
            # Draw pause icon (two rectangles)
            pygame.draw.rect(surface, BLUE, (cx - 5, cy - 7, 4, 14), border_radius=2)
            pygame.draw.rect(surface, BLUE, (cx + 1, cy - 7, 4, 14), border_radius=2)

    # Function to draw text on the screen
    def draw_text(text, font, color, surface, x, y):
        textobj = font.render(text, True, color)
        rect = textobj.get_rect()
        rect.center = (x, y)
        surface.blit(textobj, rect)

    async def random_item(snake, *others):
        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(MARGIN, GRID_HEIGHT + MARGIN - 1)
            )
            # Check not in snake and not in any other provided items
            conflict = pos in snake or any(pos == other for other in others if other is not None)
            if not conflict:
                return pos
            await asyncio.sleep(0)  # Yield control to event loop

    def draw_snake(snake, running):
        if not snake:
            return
        
        # Draw head (enlarged rounded rectangle with top corners rounded along movement direction)
        head = snake[0]
        # Enlarge the head by 1.15x
        head_scale = 1.15
        head_size = int(CELL_SIZE * head_scale)
        head_offset = (head_size - CELL_SIZE) // 2
        head_rect = pygame.Rect(
            head[0]*CELL_SIZE - head_offset,
            head[1]*CELL_SIZE - head_offset,
            head_size,
            head_size
        )
        # Determine direction for corner rounding and eyes
        if len(snake) > 1:
            dx = head[0] - snake[1][0]
            dy = head[1] - snake[1][1]
        else:
            dx, dy = 1, 0  # Default to right

        border_radius = 12
        pygame.draw.rect(screen, GREEN, head_rect)

        # Top corners along movement direction
        if dx == 1:  # moving right, round top-right and bottom-right
            pygame.draw.circle(screen, GREEN, (head_rect.right - border_radius, head_rect.top + border_radius), border_radius)
            pygame.draw.circle(screen, GREEN, (head_rect.right - border_radius, head_rect.bottom - border_radius), border_radius)
            pygame.draw.rect(screen, GREEN, (head_rect.left, head_rect.top, border_radius, head_size))
        elif dx == -1:  # moving left, round top-left and bottom-left
            pygame.draw.circle(screen, GREEN, (head_rect.left + border_radius, head_rect.top + border_radius), border_radius)
            pygame.draw.circle(screen, GREEN, (head_rect.left + border_radius, head_rect.bottom - border_radius), border_radius)
            pygame.draw.rect(screen, GREEN, (head_rect.right - border_radius, head_rect.top, border_radius, head_size))
        elif dy == 1:  # moving down, round bottom-left and bottom-right
            pygame.draw.circle(screen, GREEN, (head_rect.left + border_radius, head_rect.bottom - border_radius), border_radius)
            pygame.draw.circle(screen, GREEN, (head_rect.right - border_radius, head_rect.bottom - border_radius), border_radius)
            pygame.draw.rect(screen, GREEN, (head_rect.left, head_rect.top, head_size, border_radius))
        else:  # moving up, round top-left and top-right
            pygame.draw.circle(screen, GREEN, (head_rect.left + border_radius, head_rect.top + border_radius), border_radius)
            pygame.draw.circle(screen, GREEN, (head_rect.right - border_radius, head_rect.top + border_radius), border_radius)
            pygame.draw.rect(screen, GREEN, (head_rect.left, head_rect.bottom - border_radius, head_size, border_radius))

        # Draw eyes (adjusted for enlarged head)
        eye_radius = head_size // 3
        offset = head_size // 2
        center_x = head_rect.centerx
        center_y = head_rect.centery

        if dx == 1:  # right
            eye1 = (center_x + offset//2, center_y - offset//2)
            eye2 = (center_x + offset//2, center_y + offset//2)
        elif dx == -1:  # left
            eye1 = (center_x - offset//2, center_y - offset//2)
            eye2 = (center_x - offset//2, center_y + offset//2)
        elif dy == 1:  # down
            eye1 = (center_x - offset//2, center_y + offset//2)
            eye2 = (center_x + offset//2, center_y + offset//2)
        else:  # up
            eye1 = (center_x - offset//2, center_y - offset//2)
            eye2 = (center_x + offset//2, center_y - offset//2)

        pygame.draw.circle(screen, WHITE, eye1, eye_radius)
        pygame.draw.circle(screen, WHITE, eye2, eye_radius)
        
        # Pupils or Crosses
        pupil_radius = eye_radius // 2
        if running == True:
            pygame.draw.circle(screen, BLACK, eye1, pupil_radius)
            pygame.draw.circle(screen, BLACK, eye2, pupil_radius)
        else:
            # Draw a cross for each eye
            cross_size = pupil_radius
            for eye in [eye1, eye2]:
                ex, ey = eye
                pygame.draw.line(screen, BLACK, (ex - cross_size, ey - cross_size), (ex + cross_size, ey + cross_size), 2)
                pygame.draw.line(screen, BLACK, (ex - cross_size, ey + cross_size), (ex + cross_size, ey - cross_size), 2)

        # Draw body (rectangle)
        if len(snake) > 2:
            for segment in snake[1:-1]:
                rect = pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # Alternate body color between pale green and dark green
                green_shades = [GREEN, DARK_GREEN]       
                idx = snake[1:-1].index(segment)
                color = green_shades[idx % 2]
                pygame.draw.rect(screen, color, rect)
        elif len(snake) == 2:
            # Only one body segment
            segment = snake[1]
            rect = pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

        # Draw tail (triangle)
        if len(snake) > 1:
            tail = snake[-1]
            before_tail = snake[-2]
            dx = tail[0] - before_tail[0]
            dy = tail[1] - before_tail[1]
            cx = tail[0]*CELL_SIZE + CELL_SIZE//2
            cy = tail[1]*CELL_SIZE + CELL_SIZE//2
            if dx == 1:  # tail points right
                points = [
                    (tail[0]*CELL_SIZE + CELL_SIZE, cy),
                    (tail[0]*CELL_SIZE, tail[1]*CELL_SIZE),
                    (tail[0]*CELL_SIZE, tail[1]*CELL_SIZE + CELL_SIZE)
                ]
            elif dx == -1:  # tail points left
                points = [
                    (tail[0]*CELL_SIZE, cy),
                    (tail[0]*CELL_SIZE + CELL_SIZE, tail[1]*CELL_SIZE),
                    (tail[0]*CELL_SIZE + CELL_SIZE, tail[1]*CELL_SIZE + CELL_SIZE)
                ]
            elif dy == 1:  # tail points down
                points = [
                    (cx, tail[1]*CELL_SIZE + CELL_SIZE),
                    (tail[0]*CELL_SIZE, tail[1]*CELL_SIZE),
                    (tail[0]*CELL_SIZE + CELL_SIZE, tail[1]*CELL_SIZE)
                ]
            else:  # dy == -1, tail points up
                points = [
                    (cx, tail[1]*CELL_SIZE),
                    (tail[0]*CELL_SIZE, tail[1]*CELL_SIZE + CELL_SIZE),
                    (tail[0]*CELL_SIZE + CELL_SIZE, tail[1]*CELL_SIZE + CELL_SIZE)
                ]
            pygame.draw.polygon(screen, GREEN, points)

    def draw_food(food):
        # Draw apple body (red circle)
        center = (food[0]*CELL_SIZE + CELL_SIZE//2, food[1]*CELL_SIZE + CELL_SIZE//2)
        radius = CELL_SIZE//2 - 2
        pygame.draw.circle(screen, RED, center, radius)

        # Draw apple highlight (small ellipse)
        highlight_rect = pygame.Rect(
            center[0] - radius//2, center[1] - radius//2, radius, radius//2)
        pygame.draw.ellipse(screen, LIGHT_RED, highlight_rect)

        # Draw apple stem (brown rectangle)
        stem_width = CELL_SIZE // 6
        stem_height = CELL_SIZE // 3
        stem_rect = pygame.Rect(
            center[0] - stem_width//2, center[1] - radius - stem_height//2, stem_width, stem_height)
        pygame.draw.rect(screen, (139, 69, 19), stem_rect)

        # Draw apple leaf (green ellipse)
        leaf_width = CELL_SIZE // 3
        leaf_height = CELL_SIZE // 6
        leaf_rect = pygame.Rect(
            center[0] + stem_width//2, center[1] - radius - stem_height, leaf_width, leaf_height)
        pygame.draw.ellipse(screen, (34, 139, 34), leaf_rect)

    def draw_bomb(bomb):
        # Draw bomb body (enlarged)
        bomb_scale = random.uniform(1.2, 2)
        radius = int((CELL_SIZE // 2 - 2) * bomb_scale)
        center = (bomb[0]*CELL_SIZE + CELL_SIZE//2, bomb[1]*CELL_SIZE + CELL_SIZE//2)
        pygame.draw.circle(screen, BLACK, center, radius)

        # Draw bomb highlight (small ellipse)
        highlight_rect = pygame.Rect(
            center[0] - radius//2, center[1] - radius//2, radius, radius//2)
        pygame.draw.ellipse(screen, DARK_GRAY, highlight_rect)

        # Draw key (black rectangle)
        key_width = CELL_SIZE // 6
        key_height = CELL_SIZE // 3
        key_rect = pygame.Rect(
            center[0] - key_width//2, center[1] - radius - key_height//2, key_width, key_height)
        pygame.draw.rect(screen, BLACK, key_rect)

        # Draw key ring (yellow ellipse)
        ring_width = CELL_SIZE // 3
        ring_height = CELL_SIZE // 6
        ring_rect = pygame.Rect(
            center[0] + key_width//2, center[1] - radius - key_height, ring_width, ring_height)
        pygame.draw.ellipse(screen, YELLOW, ring_rect)

    # Draw star (yellow circle with points)
    def draw_star(star):
        # Draw star body (yellow circle)
        star_scale = random.uniform(0.6, 0.8)
        center = (star[0]*CELL_SIZE + CELL_SIZE//2, star[1]*CELL_SIZE + CELL_SIZE//2)
        radius = int((CELL_SIZE//2 - 2) * star_scale)
        color = random.choice([YELLOW, WHITE]) # Randomly choose yellow or white
        pygame.draw.circle(screen, color, center, radius)

        # Draw 5-pointed star (sharp points)
        points = []
        num_points = 5
        angle_between = 360 / num_points
        outer_radius = int(radius * 2)
        inner_radius = int(radius * 1.2)
        for i in range(num_points * 2):
            angle_deg = -90 + i * (angle_between / 2)
            angle_rad = angle_deg * (3.1415 / 180)
            r = outer_radius if i % 2 == 0 else inner_radius
            x = center[0] + int(r * math.cos(angle_rad))
            y = center[1] + int(r * math.sin(angle_rad))
            points.append((x, y))   
        pygame.draw.polygon(screen, color, points)

    # Set the movement speed based on score
    def get_fps(score):
        return 7 + score // 3  # Increase speed as score increases

    async def play_game():
        # Initialize snake, food, etc.
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ]
        direction = (1, 0)
        food = await random_item(snake)
        bomb = None
        star = None
        star_active = False
        star_drawn_score = -1
        star_timer = 0
        score = 0
        apple_number = 0
        star_number = 0 
        cause = ""
        is_paused = False
        is_muted = False
        BUTTON_SIZE = 20
        pause_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_SIZE - 20, 10, BUTTON_SIZE, BUTTON_SIZE)
        mute_button_rect = pygame.Rect(pause_button_rect.left - BUTTON_SIZE - 30, 10, BUTTON_SIZE, BUTTON_SIZE)
        running = True

        if not is_muted:
            pygame.mixer.music.load("assets/gamemusic.ogg")
            pygame.mixer.music.play(-1)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return score, apple_number, star_number, cause
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mute_button_rect.collidepoint(event.pos):
                        is_muted = not is_muted
                        if is_muted:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                    if pause_button_rect.collidepoint(event.pos):
                        is_paused = not is_paused
                        if is_paused:
                            pygame.mixer.music.pause()
                        else:
                            if not is_muted:
                                pygame.mixer.music.unpause()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        direction = (1, 0)

            if not is_paused:
                new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

                # Check collisions
                if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                    new_head[1] < MARGIN or new_head[1] >= (GRID_HEIGHT+MARGIN) or
                    new_head in snake or
                    new_head == bomb):
                    running = False

                    if not is_muted:
                            pygame.mixer.music.stop()
                            pygame.mixer.Sound("assets/over.ogg").play()                
                    
                    if new_head == bomb:
                        cause = "Oops... 1 bomb got you!"
                    else:
                        cause = "But, you turned too fast. Boom — game over in a silly tangle."
                    
                    draw_snake(snake, running)
                    pygame.display.flip()

                    await asyncio.sleep(1)  # Pause to show the final state
                    break

                # Snake becomes longer if it eats food
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    apple_number += 1
                    if not is_muted:
                        eat_sound = pygame.mixer.Sound("assets/eat.ogg")
                        eat_sound.set_volume(1.0)
                        eat_sound.play()                
                    food = await random_item(snake)
                else:
                    snake.pop()

                # snake becomes shorter if it eats star
                if star_active and star is not None and new_head == star:
                    score += 3
                    star_number += 1
                    if not is_muted:
                        eat_sound = pygame.mixer.Sound("assets/star.ogg")
                        eat_sound.set_volume(1.0)
                        eat_sound.play()                
                    star_active = False
                    star = None
                    shorten_by = min(5, len(snake) - 3)
                    if shorten_by > 0:
                        snake = snake[:-shorten_by]
            await asyncio.sleep(0)

            # Draw everything
            screen.fill(DARK_GRAY, rect=pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))            
            draw_background()
            draw_pause_button(screen, pause_button_rect, is_paused)
            draw_mute_button(screen, mute_button_rect, is_muted)                      
            draw_snake(snake, running)
            draw_food(food)
            # Bomb logic: show bomb if score >= 5, destroy after 5 seconds and regenerate
            if score >= 5 and not is_paused:
                if bomb is None:
                    bomb = await random_item(snake, food, star)
                    bomb_timer = pygame.time.get_ticks()

                draw_bomb(bomb)

                if pygame.time.get_ticks() - bomb_timer > 5000:
                    # Explosion effect
                    explosion_center = (bomb[0]*CELL_SIZE + CELL_SIZE//2, bomb[1]*CELL_SIZE + CELL_SIZE//2)
                    for r in range(CELL_SIZE//2, CELL_SIZE*2, CELL_SIZE//2):
                        pygame.draw.circle(screen, (255, 200, 0), explosion_center, r, 4)
                    if not is_muted:
                        pygame.mixer.Sound("assets/bomb.ogg").play()                    
                    pygame.display.flip()
                    pygame.time.wait(1)

                    # Reset bomb and timer
                    bomb = await random_item(snake, food, star)
                    bomb_timer = pygame.time.get_ticks()
            else:
                bomb = None
                bomb_timer = None

            # Draw star if score is a multiple of 7 and destroy it after 5 seconds
            if score % 7 == 0 and score > 0 and not is_paused:
                if star_drawn_score != score:
                    star = await random_item(snake, food, bomb)
                    star_timer = pygame.time.get_ticks()
                    star_drawn_score = score
                    star_active = True

                if star_active:
                    draw_star(star)
                    if pygame.time.get_ticks() - star_timer > 5000:
                        star_active = False
                        star = None
            else:
                star_active = False
            
            draw_text(f"Score: {score}", small_font, BLUE, screen, 70, 20)
            FPS = get_fps(score)
            pygame.display.flip()
            clock.tick(FPS)
            await asyncio.sleep(0)
        return score, apple_number, star_number, cause

    async def game_over_screen(score, apple_number, star_number, cause):
             
        async def type_text(lines, font, color, surface, x, y, line_spacing=38):

            max_width = surface.get_width() - 40
            rendered_lines = []
            
            # Pre-render all lines and handle text wrapping
            for line in lines:
                words = line.split()
                current_line = ""
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font.render(test_line, True, color).get_width() > max_width:
                        rendered_lines.append(current_line)
                        current_line = word
                    else:
                        current_line = test_line
                rendered_lines.append(current_line)

            # Calculate the total height of the text block
            total_text_height = len(rendered_lines) * line_spacing
            
            # Calculate the number of lines to show before scrolling
            initial_lines_to_show = 4
            
            # The number of pixels to scroll
            scroll_amount = total_text_height - (initial_lines_to_show * line_spacing)

            # Draw all initial lines
            surface.fill(GRAY)
            for i in range(min(initial_lines_to_show, len(rendered_lines))):
                textobj = font.render(rendered_lines[i], True, color)
                text_rect = textobj.get_rect(topleft=(20, y + i * line_spacing))
                surface.blit(textobj, text_rect)
            pygame.display.flip()
            await asyncio.sleep(2) # Wait a moment before starting to scroll

            # Animate the scrolling
            if scroll_amount > 0:
                for offset in range(0, scroll_amount + 1):
                    surface.fill(GRAY)
                    for i, line in enumerate(rendered_lines):
                        textobj = font.render(line, True, color)
                        text_rect = textobj.get_rect(topleft=(20, y + i * line_spacing - offset))
                        surface.blit(textobj, text_rect)
                    
                    pygame.display.flip()
                    await asyncio.sleep(0.01) # Small delay for smooth animation
        
        lines = [
            f"Well done!",
            f"You gobbled {apple_number} apples ...",
            f"Found {star_number} stars ...",
            cause,
            f"Final Score: {score}",
            "",
            "Big win? Small win? Doesn't matter!",
            "You zipped around and made silly moves, got stuck, and laughed it off. You played with all your heart.",
            "",
            "This was your story. Your adventure. And it was awesome!!!",
            "Ready for your next journey?"        
        ]

        # Clear screen and type out the lines
        screen.fill(GRAY)
        pygame.mixer.music.load("assets/bgmusic.ogg")
        pygame.mixer.music.play(-1)
        await type_text(lines, small_font, (50,50,50), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, line_spacing=32)
        
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 40, 120, 50)
        pygame.draw.rect(screen, DARK_GRAY, button_rect, border_radius=8)
        draw_text("Play Again", small_font, BLUE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 65)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:                    
                        return
            await asyncio.sleep(0.1)

    showing_instructions = True  # Show instructions before game starts
    
    running = True
    
    while running:
        while showing_instructions:
            play_rect = draw_instruction_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN and play_rect.collidepoint(event.pos):
                    showing_instructions = False  # Start the game
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        showing_instructions = False  # Start the game
            await asyncio.sleep(0.1)
              
        # Play the game
        score, apple_number, star_number, cause = await play_game()

        # Show game over screen
        await game_over_screen(score, apple_number, star_number, cause)

        pygame.display.flip()
        await asyncio.sleep(0)
    
    pygame.quit()

asyncio.run(main())