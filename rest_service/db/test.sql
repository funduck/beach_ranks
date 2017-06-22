delete from beach_ranks.players;
delete from beach_ranks.ratings;
delete from beach_ranks.ratings_defs;
delete from beach_ranks.games;
delete from beach_ranks.game_players;
delete from beach_ranks.game_ratings;
delete from beach_ranks.log;

select * from beach_ranks.log

insert into beach_ranks.log(object_type, object_id, what, who, date) 
      values ('game_ratings', 1||' '||2, 'insert '||' asdasd'||' '||' some', 'who', now());

select date '2017-04-23T22:33:08.141243'

select * from beach_ranks.players

select player_id, status, nick, phone from beach_ranks.players where phone = '79161234567'

select * from beach_ranks.ratings

select * from beach_ranks.ratings_defs

select * from beach_ranks.games g, beach_ranks.game_players p
where g.game_id = p.game_id

select * from beach_ranks.save_game(1, 'active', '2017-04-23T22:33:08.141243' ,0 , 0)

select * from beach_ranks.save_player(1, 'active', 'nick', '79161234567')

select * from beach_ranks.save_game_player(45, 106, True)


select * from beach_ranks.save_rating('trueskil', 104, 2, 3)


insert into beach_ranks.players(player_id, status, nick, phone) values (0, active, "nick", "79161234567")


select * from beach_ranks.test

select max(coalesce(rat_id, -1)) from (
    select rating_id as rat_id from beach_ranks.ratings_defs
    union
    select -1 as rat_id
    ) a