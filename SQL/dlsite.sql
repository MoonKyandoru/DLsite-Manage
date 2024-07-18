-- 设置字符集为 UTF-8
CREATE DATABASE IF NOT EXISTS dlsite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 cv 表, 保存声优相关的信息
CREATE TABLE IF NOT EXISTS dlsite.cv (
    ID VARCHAR(15) NOT NULL,
    cv VARCHAR(32) NOT NULL,
    PRIMARY KEY (ID)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 tag 表, 用来存储作品的 tag
CREATE TABLE IF NOT EXISTS dlsite.tag (
    ID VARCHAR(15) NOT NULL,
    tag VARCHAR(32) NOT NULL,
    PRIMARY KEY (ID)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 dlsite 表, 用来存储作品的相关信息
CREATE TABLE IF NOT EXISTS dlsite.dlsite (
    ID VARCHAR(15) NOT NULL PRIMARY KEY,
    Name VARCHAR(256),
    URL VARCHAR(128),
    Societies VARCHAR(128),
    SellDay DATE,
    SeriesName VARCHAR(128),
    Author VARCHAR(64),
    Scenario VARCHAR(64),
    Illustration VARCHAR(64),
    Music VARCHAR(64),
    AgeSpecification ENUM('r18', 'all', 'r15', 'unknown'),
    WorkFormat VARCHAR(64),
    FileCapacity FLOAT,
    Status BOOL DEFAULT FALSE,
    Point TINYINT,
    FOREIGN KEY (ID) REFERENCES cv(ID),
    FOREIGN KEY (ID) REFERENCES tag(ID)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;