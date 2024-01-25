# - Krishna Chauhan: Cheese Run -
import pygame, math, random

#Pygame Global Variables
WIDTH, HEIGHT = (1280, 720) #size of the screen
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) #the surface that everything is drawn on
FPS = 60 #frames per second of the game

max_lvl = 4 # IMPORTANT: if you want to add or unlock more levels change the max level

# <- Initialization Section ->
def init():
    '''This function is used to initialize variables or objects before the game begins'''
    initImages() # Images I Used
    initFont() # Fonts I Used
    initAudio() # Colors I Used
    initGeneral() # Initialization of states and the menu

def initImages():
    global player_block, wall_block, floor, cheese_block, enemy_block, death_block, jail_block, goal_block, warp_block
    player_block, wall_block, floor, cheese_block, enemy_block, death_block, jail_block, goal_block, warp_block = [
        pygame.image.load('playerblock.png'), pygame.image.load('wallblock.png'), pygame.image.load('floortile.png'),
        pygame.image.load('cheese.png'), pygame.image.load('enemyblock.png'), pygame.image.load('deathblock.png'),
        pygame.image.load('jailblock.png'), pygame.image.load('checkeredblock.png'), pygame.image.load('warpblock.png')]

    global display_dict
    display_dict = {'x': wall_block, '_': floor, 'e': jail_block, 'w': warp_block}

    global bg_img, menu_img, game_win_img, lvl_complete_img, game_lose_img
    bg_img, menu_img, game_win_img, lvl_complete_img, game_lose_img = [
        pygame.image.load('bg.png'), pygame.image.load('menu.png'), pygame.image.load('win.png'),
        pygame.image.load('start.png'), pygame.image.load('lose.png')]

def initFont():
    global display_font, score_font, warp_font
    display_font = pygame.font.SysFont(None, 70)
    score_font = pygame.font.SysFont(None, 50)
    warp_font = pygame.font.SysFont(None, 30)

def initAudio():
    global lvl_sound, win_sound, lose_sound, goal_sound, move_sound, lesstime_sound
    lvl_sound, win_sound = pygame.mixer.Sound('complvl.wav'), pygame.mixer.Sound('compgame.wav')
    lose_sound, goal_sound = pygame.mixer.Sound('gameover.wav'), pygame.mixer.Sound('goal unlocked.wav')
    move_sound, lesstime_sound = pygame.mixer.Sound('playermove.wav'), pygame.mixer.Sound('lesstime.wav')
    global cheese_eat_p_sound, cheese_eat_e_sound, player_hit_sound, warp_sound
    cheese_eat_p_sound, cheese_eat_e_sound = pygame.mixer.Sound('cheeseeat.wav'),pygame.mixer.Sound('cheeseenemy.wav')
    player_hit_sound, warp_sound = pygame.mixer.Sound('playerhit.wav'), pygame.mixer.Sound('warp.wav')

def initGeneral():
    global gameState, menuState, startState, playState, winState, loseState, menu_choice
    gameState, menuState, startState, playState, winState, loseState, menu_choice = 0, 0, 1, 2, 3, 4, 1
# <- Initialization Section Ends->


#  <- Everything related to keys pressed ->
def keyPressed():
    global key, gameState, isRunning, level
    key = pygame.key.get_pressed()
    if gameState == menuState:
        menuKeys() # Handles Keys pressed on the menu
    elif gameState == startState:
        startLevel() # Mentioned in menu
    elif gameState == playState:
        playerMovement() # Handles arrow keys on the player
        warping() # Handles warping keys and moves player to them
    elif gameState == winState or gameState == loseState:
        global isRunning, level, score
        if key[pygame.K_q]:
            isRunning = False
        elif key[pygame.K_RETURN]:
            level = 0
            score = 0
            startLevel()

def menuKeys():
    global menu_choice, isRunning, score, level
    score = 0
    level = 0
    if key[pygame.K_UP] or key[pygame.K_DOWN]:
        menu_choice = -menu_choice
    if key[pygame.K_RETURN] and menu_choice == 1:
        startLevel() # Starts the new level
        cheese_eat_p_sound.play()
    elif key[pygame.K_RETURN] and menu_choice == -1:
        isRunning = False

def startLevel(): # Initializes each level
    global gameState, level, BLOCK_THICK
    gameState, BLOCK_THICK = playState, 30
    level += 1
    initGrid(f'level{level}.txt') # Makes grid, and finds all positions of entities
    initValues() # Uses grid to make basic values

def initGrid(filename): # note that this takes the moving entities off the grid
    global grid, playerX, playerY, verticalEnemies, horizontalEnemies, warpBlocks
    grid, verticalEnemies, horizontalEnemies, warpBlocks = [], [], [], []
    with open(filename) as level:
        y = 0
        for line in level:
            grid.append(line.strip())
            x = 0
            for letter in line.strip():
                if letter == 'p':
                    playerX, playerY = x, y
                    grid[y] = grid[y][:x] + '_' + grid[y][x + 1:]
                elif letter == '1':
                    horizontalEnemies.append([x, y, 1])
                    grid[y] = grid[y][:x] + '_' + grid[y][x + 1:]
                elif letter == '2':
                    verticalEnemies.append([x, y, 1])
                    grid[y] = grid[y][:x] + '_' + grid[y][x + 1:]
                x += 1
            y += 1

        for x in range(len(grid[0])):
            for y in range(len(grid)):
                if grid[y][x] == 'w':
                    warpBlocks.append((x, y))

def initValues():
    global timer, goal_unlocked, cheese_eaten, display_dict, goal_siren, block_startX, block_startY
    timer = math.ceil(len(grid[0]) * len(grid) * 0.15 * 60)
    goal_unlocked, cheese_eaten, display_dict['e'], goal_siren = False, 0, jail_block, True
    block_startX, block_startY = ((WIDTH - len(grid[0]) * BLOCK_THICK)/ 2, (HEIGHT + 100 - len(grid) * BLOCK_THICK)/ 2)
    global cheeseX, cheeseY
    cheeseX, cheeseY = 0,0

def playerMovement():
    global playerX, playerY
    if key[pygame.K_UP] and (grid[playerY-1][playerX] != 'x' and (grid[playerY-1][playerX] != 'e' or goal_unlocked)):
        playerY -= 1
        move_sound.play()
    if key[pygame.K_DOWN] and (grid[playerY+1][playerX] != 'x' and (grid[playerY+1][playerX] != 'e' or goal_unlocked)):
        playerY += 1
        move_sound.play()
    if key[pygame.K_LEFT] and (grid[playerY][playerX-1] != 'x' and (grid[playerY][playerX-1] != 'e' or goal_unlocked)):
        playerX -= 1
        move_sound.play()
    if key[pygame.K_RIGHT] and (grid[playerY][playerX+1] != 'x' and (grid[playerY][playerX+1] != 'e' or goal_unlocked)):
        playerX += 1
        move_sound.play()

def warping():
    global playerX, playerY
    if grid[playerY][playerX] == 'w':
        try:
            if key[pygame.K_1]:
                playerX, playerY = warpBlocks[0]
                warp_sound.play()
            if key[pygame.K_2]:
                playerX, playerY = warpBlocks[1]
                warp_sound.play()
            if key[pygame.K_3]:
                playerX, playerY = warpBlocks[2]
                warp_sound.play()
            if key[pygame.K_4]:
                playerX, playerY = warpBlocks[3]
                warp_sound.play()
            if key[pygame.K_5]:
                playerX, playerY = warpBlocks[4]
                warp_sound.play()
            if key[pygame.K_6]:
                playerX, playerY = warpBlocks[5]
                warp_sound.play()
            if key[pygame.K_7]:
                playerX, playerY = warpBlocks[6]
                warp_sound.play()
            if key[pygame.K_8]:
                playerX, playerY = warpBlocks[7]
                warp_sound.play()
            if key[pygame.K_9]:
                playerX, playerY = warpBlocks[8]
                warp_sound.play()
            if key[pygame.K_0]:
                playerX, playerY = warpBlocks[9]
                warp_sound.play()
        except: # This is so the player can easily go to the very last warp
            playerX, playerY = warpBlocks[-1]
            warp_sound.play()
# <- Keys Ends - >

# <- Update Section - >
def update():
    '''This function is used to modify the data portions of things shown on screen'''
    global timer, display_dict, goal_unlocked, goal_siren
    if gameState == playState:
        timer -= 1
        if cheese_eaten == 5 and goal_siren:
            goal_unlocked = True
            goal_sound.play()
            display_dict['e'] = goal_block
            goal_siren = False
        if timer == 180:
            lesstime_sound.play()
        enemyMovement() # Controls movement of the enemies
        cheeseEater()
        cheeseSpawner()

def enemyMovement():
    if timer % 20 == 0:
        for i in range(len(verticalEnemies)):
            verticalMovement(verticalEnemies[i][0], verticalEnemies[i][1], verticalEnemies[i][2], i)
    if timer % 30 == 0:
        for i in range(len(horizontalEnemies)):
            horizontalMovement(horizontalEnemies[i][0], horizontalEnemies[i][1], horizontalEnemies[i][2], i)

def verticalMovement(x, y, d, i):
    if grid[y + d][x] == 'x' or grid[y + d][x] == 'e':
        verticalEnemies[i][2] = -d
        d = -d
    if enemyCollision(x, y+d, horizontalEnemies):
        verticalEnemies[i][1] += verticalEnemies[i][2]

def enemyCollision(x, y, enemies):
    # This function checks the enemies list and sees if there is a collision
    # No collision returns True, while if there is a collision, it returns False
    no_collision = True
    for enemy in enemies:
        if enemy == [x, y, 1] or enemy == [x, y, -1]:
            no_collision = False
            return no_collision
    return no_collision

def horizontalMovement(x, y, d, i):
    if grid[y][x + d] == 'x' or grid[y][x + d] == 'e':
        horizontalEnemies[i][2] = -d
        d = -d
    if enemyCollision(x+d, y, verticalEnemies):
        horizontalEnemies[i][0] += horizontalEnemies[i][2]

def cheeseEater():
    global cheese_eaten, cheeseX, cheeseY, score
    if playerX == cheeseX and playerY == cheeseY:
        cheeseX, cheeseY = random.randint(0, len(grid[0]) - 1), random.randint(0, len(grid) - 1)
        cheese_eaten += 1
        score += 5*level
        cheese_eat_p_sound.play()

def cheeseSpawner():
    global cheeseX, cheeseY
    if grid[cheeseY][cheeseX] != '_' or not enemyCollision(cheeseX, cheeseY, horizontalEnemies + verticalEnemies):
        if not enemyCollision(cheeseX, cheeseY, horizontalEnemies + verticalEnemies):
            cheese_eat_e_sound.play()
        cheeseX, cheeseY = random.randint(0, len(grid[0]) - 1), random.randint(0, len(grid) - 1)
        cheeseSpawner()

# <- Update Section ends ->


# <- Draw Section ->
def draw():
    '''This function is used to draw things onto the screen'''
    if gameState == menuState:
        SCREEN.blit(menu_img, (0, 0))
        if menu_choice == 1:
            SCREEN.blit(cheese_block, (WIDTH / 2 - 125, HEIGHT / 2 - 70))
        else:
            SCREEN.blit(cheese_block, (WIDTH / 2 - 125, HEIGHT / 2))
    elif gameState == playState:
        drawPlay()
    elif gameState == startState:
        SCREEN.blit(lvl_complete_img, (0,0))
        scoreWord = score_font.render(f'Score: {score}', True, (255,255,255))
        SCREEN.blit(scoreWord, (50, 150))
    elif gameState == loseState:
        SCREEN.blit(game_lose_img, (0,0))
        SCREEN.blit(death_block, (block_startX + playerX * BLOCK_THICK, block_startY + playerY * BLOCK_THICK))
        scoreWord = score_font.render(f'Score: {score}', True, (255,255,255))
        SCREEN.blit(scoreWord, (50, 150))
    elif gameState == winState:
        SCREEN.blit(game_win_img, (0,0))
        scoreWord = score_font.render(f'Score: {score}', True, (255,255,255))
        SCREEN.blit(scoreWord, (WIDTH/2 - 120, HEIGHT/2 - 75))
    pygame.display.flip() #should always be the last line in this function

def drawPlay():
    SCREEN.blit(bg_img, (0, 0))
    drawGrid()
    drawEntities()
    drawScore()
    drawWarp()

def drawGrid():
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            SCREEN.blit(display_dict[grid[y][x]], (block_startX + x*BLOCK_THICK, block_startY + y*BLOCK_THICK))

def drawEntities():
    for enemies in verticalEnemies:
        x = enemies[0]
        y = enemies[1]
        SCREEN.blit(enemy_block, (block_startX + x*BLOCK_THICK, block_startY + y*BLOCK_THICK))
    for enemies in horizontalEnemies:
        x = enemies[0]
        y = enemies[1]
        SCREEN.blit(enemy_block, (block_startX + x*BLOCK_THICK, block_startY + y*BLOCK_THICK))
    SCREEN.blit(player_block, (block_startX + playerX * BLOCK_THICK, block_startY + playerY * BLOCK_THICK))
    SCREEN.blit(cheese_block, (block_startX + cheeseX * BLOCK_THICK, block_startY + cheeseY * BLOCK_THICK))

def drawScore():
    if timer//60 <= 10:
        timer_word = display_font.render(f'Time: {round(timer / 60)}', True, (255,0,0))
    else:
        timer_word = display_font.render(f'Time: {round(timer / 60)}', True, (255,255,255))
    SCREEN.blit(timer_word, (125, 40))
    level_word = display_font.render(f'Level: {level}', True, (255,255,255))
    SCREEN.blit(level_word, (400, 40))
    cheese_word = display_font.render(f'Cheese: {cheese_eaten}', True, (255,255,255))
    SCREEN.blit(cheese_word, (650, 40))
    score_word = display_font.render(f'Score: {score}', True, (255,255,255))
    SCREEN.blit(score_word, (WIDTH - 300, 40))

def drawWarp():
    if grid[playerY][playerX] == 'w':
        for warp in range(len(warpBlocks)):
            display = warp_font.render(str(warp+1), True, (255,255,255))
            SCREEN.blit(display, (block_startX + warpBlocks[warp][0] * BLOCK_THICK+10, block_startY + len(grid) * BLOCK_THICK+4))

# <- Draw Section end ->


# <- Game End Section ->
def gameEnd():
    # Generally this should go in update, but since the keyboard function changes player placement,
    # The order was messed up, so I must run this check at the end of the loop
    # This basically checks it the game player won or died each time
    global gameState, score
    if gameState == playState:
        if goal_unlocked and grid[playerY][playerX] == 'e':
            score += timer // 60
            if level == max_lvl:
                gameState = winState
                win_sound.play()
            else:
                gameState = startState
                lvl_sound.play()
        if not (enemyCollision(playerX, playerY, horizontalEnemies + verticalEnemies)) or timer <= 0:
            if not enemyCollision(playerX, playerY, horizontalEnemies + verticalEnemies):
                player_hit_sound.play()
            lose_sound.play()
            gameState = loseState
# <- Game End Section ends->


def main():
    global gameState, isRunning
    pygame.init()
    init()
    isRunning = True #this variable controls whether the game runs or not
    clock = pygame.time.Clock()

    while isRunning:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
            if event.type == pygame.KEYDOWN:
                keyPressed()

        update()
        draw()
        gameEnd()
    pygame.quit()
if __name__ == "__main__":
    main()