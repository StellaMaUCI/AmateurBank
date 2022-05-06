-- create user account
DROP TABLE IF EXISTS user;
CREATE TABLE user (
  -- id INT PRIMARY KEY AUTO_INCREMENT错误，设置-方言选sqlite
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(50) NOT NULL,
  firstname VARCHAR(50) NOT NULL,
  lastname VARCHAR(50) NOT NULL,
  phone INT(10)
);

DROP TABLE IF EXISTS account;
CREATE TABLE account (
  -- id INT PRIMARY KEY AUTO_INCREMENT错误，设置-方言选sqlite
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  amount DECIMAL(16,2) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)

);