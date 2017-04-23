
delete from beach_ranks.players;
delete from beach_ranks.ratings;
delete from beach_ranks.ratings_defs;
delete from beach_ranks.games;
delete from beach_ranks.game_players;

select date '2017-04-23T22:33:08.141243'

select * from beach_ranks.players

select * from beach_ranks.ratings

select * from beach_ranks.ratings_defs

select * from beach_ranks.games g, beach_ranks.game_players p
where g.game_id = p.game_id

select * from beach_ranks.save_game(1, 'active', '2017-04-23T22:33:08.141243' ,0 , 0)

select * from beach_ranks.save_player(1, 'active', 'nick', '79161234567')


select * from beach_ranks.save_rating('trueskill', 1, 2, 3)


insert into beach_ranks.players(player_id, status, nick, phone) values (0, active, "nick", "79161234567")


select * from beach_ranks.test

select max(coalesce(rat_id, -1)) from (
    select rating_id as rat_id from beach_ranks.ratings_defs
    union
    select -1 as rat_id
    ) a