-- DROP ROLE beach_ranks;

/*
  CREATE ROLE beach_ranks LOGIN
  ENCRYPTED PASSWORD 'md5d33e435c716fd8c46ce9a04067c01a80'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
*/
--DROP DATABASE beach_ranks;
/*
CREATE DATABASE beach_ranks
  WITH OWNER = beach_ranks
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1
       TEMPLATE template0;
*/

-- DROP SCHEMA beach_ranks;

CREATE SCHEMA beach_ranks
  AUTHORIZATION beach_ranks;

/*
DROP TABLE beach_ranks.players;
DROP TABLE beach_ranks.ratings;
DROP TABLE beach_ranks.ratings_defs;
DROP TABLE beach_ranks.games;
DROP TABLE beach_ranks.game_players;
*/

-- DROP SEQUENCE beach_ranks.sq_player_id

CREATE SEQUENCE beach_ranks.sq_player_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_player_id
  OWNER TO beach_ranks;

-- DROP SEQUENCE beach_ranks.sq_rating_id

CREATE SEQUENCE beach_ranks.sq_rating_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_rating_id
  OWNER TO beach_ranks;

-- DROP SEQUENCE beach_ranks.sq_game_id

CREATE SEQUENCE beach_ranks.sq_game_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_game_id
  OWNER TO beach_ranks;



CREATE TABLE beach_ranks.players
(
  player_id integer,
  status varchar(10),
  nick varchar(50),
  phone varchar(20)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.players
  OWNER TO beach_ranks;

--DROP TABLE beach_ranks.ratings_defs;

CREATE TABLE beach_ranks.ratings_defs
(
  rating_id integer,
  rating_code varchar(20),
  descr varchar(100)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.ratings_defs
  OWNER TO beach_ranks;

--DROP TABLE beach_ranks.ratings;

CREATE TABLE beach_ranks.ratings
(
  rating_id integer,
  player_id integer,
  value double precision,
  accuracy double precision
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.ratings
  OWNER TO beach_ranks;

--DROP TABLE beach_ranks.games;

CREATE TABLE beach_ranks.games
(
  game_id integer,
  status varchar(10),
  date date,
  score_won integer,
  score_lost integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.games
  OWNER TO beach_ranks;

--DROP TABLE beach_ranks.game_players;

CREATE TABLE beach_ranks.game_players
(
  game_id integer,
  player_id integer,
  win boolean,
  valid boolean
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.game_players
  OWNER TO beach_ranks;

CREATE OR REPLACE FUNCTION beach_ranks.test()
RETURNS integer AS $$
DECLARE
    i integer;
BEGIN
  select 1 into i;
  return i;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_player(p_player_id integer, p_status varchar, p_nick varchar, p_phone varchar)
RETURNS integer AS $$
DECLARE
    i integer;
BEGIN
  -- find player
  select count(*) into i from beach_ranks.players where player_id = p_player_id;
  if i > 0 then
    -- update
    update beach_ranks.players
     set nick = p_nick, phone = p_phone, status = p_status
      where player_id = p_player_id;
  else
    -- new
    -- check nick
    select count(*) into i from beach_ranks.players where nick = p_nick;
    if i > 0 then 
      RAISE EXCEPTION 'beach_ranks.save_player invalid params: nick already in use';
      return -1;
    end if;

    -- create
    select nextval('beach_ranks.sq_player_id') into i;

    insert into beach_ranks.players(player_id, status, nick, phone) 
      values (i, p_status, p_nick, p_phone);
    
    return i;
  end if;
    
  return p_player_id;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_player %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_rating(p_rating_code varchar, p_player_id integer, 
               p_value double precision, p_accuracy double precision)
RETURNS integer AS $$
DECLARE
  i integer;
  v_rating_id integer;
BEGIN
  -- find ratings_def
  begin
    select rating_id into v_rating_id from beach_ranks.ratings_defs 
      where rating_code = p_rating_code;
  exception
    when others then
      -- create new type of rating
      insert into beach_ranks.ratings_defs(rating_id, rating_code, descr) 
        values (nextval('beach_ranks.sq_rating_id'), p_rating_code, '')
        returning rating_id into v_rating_id;
  end;
  
  select count(*) into i from beach_ranks.ratings r
   where r.rating_id = v_rating_id and r.player_id = p_player_id;
  
  if i = 0 then
    -- check player exists
    select count(*) into i from beach_ranks.players
     where player_id = p_player_id;
    if i = 0 then
      RAISE EXCEPTION 'beach_ranks.save_rating invalid params: player not found';
      return -1;
    end if;
    
    -- create rating
    insert into beach_ranks.ratings(rating_id, player_id, value, accuracy) 
      values (v_rating_id, p_player_id, p_value, p_accuracy);
  else
    update beach_ranks.ratings
     set value = p_value, accuracy = p_accuracy
      where rating_id = v_rating_id and player_id = p_player_id;
  end if;
  
  return 1;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_rating %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_game(p_game_id integer, p_status varchar, 
               p_date varchar, p_score_won integer, p_score_lost integer)
RETURNS integer AS $$
DECLARE
  i integer;
  v_game_id integer;
  v_date date := p_date;
BEGIN
  -- check game exists
  select count(*) into i from beach_ranks.games where game_id = p_game_id;
  if i > 0 then
    update beach_ranks.games
      set date = v_date, score_won = p_score_won, score_lost = p_score_lost
      where game_id = p_game_id;
  else
    insert into beach_ranks.games(game_id, status, date, score_won, score_lost) 
      values (nextval('beach_ranks.sq_game_id'), p_status, v_date, p_score_won, p_score_lost)
      returning game_id into v_game_id;
    return v_game_id;
  end if;

  return p_game_id;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_game %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_game_player(p_game_id integer, p_player_id integer, p_win boolean, p_valid boolean)
RETURNS integer AS $$
DECLARE
  i integer;
BEGIN
  -- check game player exists
  select count(*) into i from beach_ranks.game_players 
    where game_id = p_game_id and player_id = p_player_id and valid = True;
  if i > 0 then
    update beach_ranks.game_players
      set win = p_win, valid = p_valid
      where game_id = p_game_id and player_id = p_player_id and valid = True;
  else
    insert into beach_ranks.game_players(game_id, player_id, win, valid) 
      values (p_game_id, p_player_id, p_win, p_valid);
  end if;

  return 1;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_game_player %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;