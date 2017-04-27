-- run under admin after initializing db;

--DROP TABLE beach_ranks.players;
--DROP TABLE beach_ranks.ratings;
--DROP TABLE beach_ranks.ratings_defs;
--DROP TABLE beach_ranks.games;
--DROP TABLE beach_ranks.game_players;
--DROP TABLE beach_ranks.game_ratings;

--DROP SEQUENCE beach_ranks.sq_player_id;

CREATE SEQUENCE beach_ranks.sq_player_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_player_id
  OWNER TO admin;

--DROP SEQUENCE beach_ranks.sq_rating_id;

CREATE SEQUENCE beach_ranks.sq_rating_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_rating_id
  OWNER TO admin;

--DROP SEQUENCE beach_ranks.sq_game_id;

CREATE SEQUENCE beach_ranks.sq_game_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_game_id
  OWNER TO admin;

--DROP SEQUENCE beach_ranks.sq_log_id;

CREATE SEQUENCE beach_ranks.sq_log_id
   INCREMENT 1
   START 1;
ALTER SEQUENCE beach_ranks.sq_log_id
  OWNER TO admin;

--DROP TABLE beach_ranks.players;

CREATE TABLE beach_ranks.players
(
  player_id integer,
  nick varchar(50),
  phone varchar(20)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.players
  OWNER TO admin;

--DROP TABLE beach_ranks.ratings_defs;

CREATE TABLE beach_ranks.ratings_defs
(
  rating_code varchar(20),
  descr varchar(100)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.ratings_defs
  OWNER TO admin;

--DROP TABLE beach_ranks.ratings;

CREATE TABLE beach_ranks.ratings
(
  rating_id integer,
  player_id integer,
  rating_code varchar(20),
  value double precision,
  accuracy double precision
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.ratings
  OWNER TO admin;

--DROP TABLE beach_ranks.games;

CREATE TABLE beach_ranks.games
(
  game_id integer,
  date date,
  score_won integer,
  score_lost integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.games
  OWNER TO admin;

--DROP TABLE beach_ranks.game_players;

CREATE TABLE beach_ranks.game_players
(
  game_id integer,
  player_id integer,
  win boolean
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.game_players
  OWNER TO admin;

--DROP TABLE beach_ranks.game_ratings;

CREATE TABLE beach_ranks.game_ratings
(
  game_id integer,
  rating_id integer,
  value_before double precision,
  value_after double precision,
  accuracy_before double precision,
  accuracy_after double precision
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.game_ratings
  OWNER TO admin;

--DROP TABLE beach_ranks.log;

CREATE TABLE beach_ranks.log
(
  log_id integer,
  object_type varchar(20),
  object_id varchar(30),
  what varchar(100),
  who varchar(20),
  date date
)
WITH (
  OIDS=FALSE
);
ALTER TABLE beach_ranks.log
  OWNER TO admin;

CREATE OR REPLACE FUNCTION beach_ranks.test()
RETURNS integer AS $$
DECLARE
    i integer;
BEGIN
  select 1 into i;
  return i;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_player(p_player_id integer, p_nick varchar, p_phone varchar, who varchar)
RETURNS integer AS $$
DECLARE
    i integer;
BEGIN
  -- find player
  select count(*) into i from beach_ranks.players where player_id = p_player_id;
  if i > 0 then
    -- update
    update beach_ranks.players
     set nick = p_nick, phone = p_phone
      where player_id = p_player_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'players', p_player_id, 'update '||p_nick||' '||p_phone, who, now());
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

    insert into beach_ranks.players(player_id, nick, phone) 
      values (i, p_nick, p_phone);
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'players', i, 'insert '||p_nick||' '||p_phone, who, now());
    return i;
  end if;
    
  return p_player_id;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_player %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_rating(p_player_id integer, p_rating_code varchar,
               p_value double precision, p_accuracy double precision, who varchar)
RETURNS integer AS $$
DECLARE
  i integer;
  v_rating_id integer;
BEGIN
  -- find ratings_def
  select count(*) into i from beach_ranks.ratings_defs 
    where rating_code = p_rating_code;
  if i = 0 then
    -- create new type of rating
    insert into beach_ranks.ratings_defs(rating_code, descr) 
      values (p_rating_code, '');
  end if;
  
  select rating_id into v_rating_id from beach_ranks.ratings r
   where r.rating_code = p_rating_code and r.player_id = p_player_id;
  
  if v_rating_id is Null then
    -- check player exists
    select count(*) into i from beach_ranks.players
     where player_id = p_player_id;
    if i = 0 then
      RAISE EXCEPTION 'beach_ranks.save_rating invalid params: player not found';
      return -1;
    end if;
    
    -- create rating
    insert into beach_ranks.ratings(rating_id, player_id, rating_code, value, accuracy) 
      values (nextval('beach_ranks.sq_rating_id'), p_player_id, p_rating_code, p_value, p_accuracy)
      returning rating_id into v_rating_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date)
      values (nextval('beach_ranks.sq_log_id'), 'ratings', v_rating_id, 
        'insert '||p_player_id||' '||p_rating_code||' '||p_value||' '||p_accuracy, who, now());
  else
    update beach_ranks.ratings
     set value = p_value, accuracy = p_accuracy
      where rating_id = v_rating_id and player_id = p_player_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'ratings', v_rating_id, 
        'update '||p_player_id||' '||p_rating_code||' '||p_value||' '||p_accuracy, who, now());
  end if;
  
  return 1;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_rating %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_game(p_game_id integer, p_date varchar, 
  p_score_won integer, p_score_lost integer, who varchar)
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
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game', p_game_id, 'update '||p_date||' '||p_score_won||' '||p_score_lost, who, now());
  else
    insert into beach_ranks.games(game_id, date, score_won, score_lost) 
      values (nextval('beach_ranks.sq_game_id'), v_date, p_score_won, p_score_lost)
      returning game_id into v_game_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game', v_game_id, 'insert '||p_date||' '||p_score_won||' '||p_score_lost, who, now());
    return v_game_id;
  end if;

  return p_game_id;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_game %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_game_player(p_game_id integer, p_player_id integer, p_win boolean, who varchar)
RETURNS integer AS $$
DECLARE
  i integer;
BEGIN
  -- check game player exists
  select count(*) into i from beach_ranks.game_players 
    where game_id = p_game_id and player_id = p_player_id;
  if i > 0 then
    update beach_ranks.game_players
      set win = p_win
      where game_id = p_game_id and player_id = p_player_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game_players', p_game_id||' '||p_player_id, 'update '||p_win, who, now());
  else
    insert into beach_ranks.game_players(game_id, player_id, win) 
      values (p_game_id, p_player_id, p_win);
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game_players', p_game_id||' '||p_player_id, 'insert '||p_win, who, now());
  end if;

  return 1;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_game_player %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION beach_ranks.save_game_rating(p_game_id integer, p_player_id integer,
  p_rating_code varchar, p_value_before double precision, p_value_after double precision,
  p_accuracy_before double precision, p_accuracy_after double precision, who varchar)
RETURNS integer AS $$
DECLARE
  i integer;
  v_rating_id integer;
BEGIN
  select rating_id into v_rating_id from beach_ranks.ratings
    where rating_code = p_rating_code and player_id = p_player_id;

  -- check game rating exists
  select count(*) into i from beach_ranks.game_ratings
    where game_id = p_game_id and rating_id = v_rating_id;
  if i > 0 then
    update beach_ranks.game_ratings
      set value_before = p_value_before, value_after = p_value_after,
          accuracy_before = p_accuracy_before, accuracy_after = p_accuracy_after
      where game_id = p_game_id and rating_id = v_rating_id;
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game_ratings', p_game_id||' '||v_rating_id, 
        'update '||p_value_before||' '||p_value_after||' '||p_accuracy_before||' '||p_accuracy_after, who, now());
  else
    insert into beach_ranks.game_ratings(game_id, rating_id, value_before, value_after,
        accuracy_before, accuracy_after)
      values (p_game_id, v_rating_id, p_value_before, p_value_after,
        p_accuracy_before, p_accuracy_after);
    insert into beach_ranks.log(log_id, object_type, object_id, what, who, date) 
      values (nextval('beach_ranks.sq_log_id'), 'game_ratings', p_game_id||' '||v_rating_id, 
        'insert '||p_value_before||' '||p_value_after||' '||p_accuracy_before||' '||p_accuracy_after, who, now());
  end if;

  return 1;
/*exception
  when others then
    RAISE EXCEPTION 'beach_ranks.save_game_rating %: %', SQLERRM, SQLSTATE;
    return -1;*/
END;
$$ LANGUAGE plpgsql;

GRANT ALL ON SCHEMA beach_ranks TO GROUP beach_ranks_group;

GRANT ALL ON ALL TABLES IN SCHEMA beach_ranks TO GROUP beach_ranks_group;

GRANT ALL ON ALL SEQUENCES IN SCHEMA beach_ranks TO GROUP beach_ranks_group;

GRANT ALL ON ALL FUNCTIONS IN SCHEMA beach_ranks TO GROUP beach_ranks_group;