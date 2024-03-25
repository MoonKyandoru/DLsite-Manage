create database dlsite;
use dlsite;
create table dlsite(
    ID					varchar(15)  							not null primary key,
    Name 				varchar(256),
    URL 				varchar(128),
    Societies           varchar(128),
    SellDay 			date,
    SeriesName 			varchar(128),
    Author				varchar(64),
    Scenario			varchar(64),
    Illustration		varchar(64),
    Music 				varchar(64),
    AgeSpecification 	enum("r18", "all", "r15", "unknown"),
    WorkFormat 			varchar(64),
    FileCapacity 		float,
    Status 				bool 									default false,
    Point 				tinyint
);
create table cv(	ID varchar(15),		cv 	varchar(32)	);
create table tag(	ID varchar(15), 	tag varchar(32)	);