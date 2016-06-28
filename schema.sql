drop table if exists users;
create table users (
    id integer primary key autoincrement,
    login text not null,
    password text not null,
    active integer default 1 not null
);

drop table if exists posts;
create table posts (
    id integer primary key autoincrement,
    'text' text not null,
    author integer,
    foreign key(author) references users(id)
);

drop table if exists comments;
create table comments (
    id integer primary key autoincrement,
    author integer not null,
    post integer not null,
    'text' text not null,
    foreign key(author) references users(id),
    foreign key(post) references posts(id)
);