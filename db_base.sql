CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150)
);

CREATE TABLE Boards (
    board_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_url TEXT NOT NULL,
    image_type TEXT,
    dominant_color TEXT,
    resolution TEXT,
    width INTEGER,
    height INTEGER
);

CREATE TABLE IF NOT EXISTS Image_Resolutions (
    resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER,
    resolution TEXT NOT NULL,
    url TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    FOREIGN KEY (image_id) REFERENCES Images(image_id)
);

CREATE TABLE Board_Images (
    board_id INT,
    image_id INT,
    PRIMARY KEY (board_id, image_id),
    FOREIGN KEY (board_id) REFERENCES Boards(board_id),
    FOREIGN KEY (image_id) REFERENCES Images(image_id)
);

CREATE TABLE Searches (
    search_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    search_term VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
