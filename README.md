# Python Game Project

## Requirements

- Python **3.10** recommended
- Pygame **2.6.1**

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Developer-Zaid19/PythonGames.git
cd PythonGames
```

### 2. Create Virtual Environment

```bash
py -3.10 -m venv venv
```

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Arcade Launcher

```bash
python main.py
```

You can also run each game directly:

```bash
python bird_game.py
python crashbreak_game.py
python snake_game.py
```

## Games

- **Sky Survivor**: A polished flappy-style survival game.
- **Crash Breaker**: A brick breaker game with powerups.
- **Neon Snake Rush**: A dark-theme Snake game with random food, self-collision game over, score tracking, and a red 5-second bonus worth +5 points without growing the snake.

## Snake Controls

- Move: Arrow keys or W/A/S/D
- Start: Space
- Pause: P
- Restart after game over: R
- Quit: Q

## Other Game Controls

- **Sky Survivor**: Space to start/flap, P to pause, R to restart after game over, Q to quit.
- **Crash Breaker**: Arrow keys or A/D to move, Space to start/launch, P to pause, R to restart after game over, Q to quit.

## Project Structure

```text
project/
|-- Assets/
|-- bird_game.py
|-- crashbreak_game.py
|-- snake_game.py
|-- main.py
|-- requirements.txt
|-- README.md
```

## Notes

- Make sure you are using Python 3.10 or newer.
- Always activate the virtual environment before running the project.
