--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.1

-- Started on 2017-04-23 01:10:15 MSK

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--DROP DATABASE beach_ranks;
--
-- TOC entry 2178 (class 1262 OID 18209)
-- Name: beach_ranks; Type: DATABASE; Schema: -; Owner: beach_ranks
--

CREATE DATABASE beach_ranks WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';

-- Role: beach_ranks

-- DROP ROLE beach_ranks;

CREATE ROLE beach_ranks LOGIN
  ENCRYPTED PASSWORD 'md5d33e435c716fd8c46ce9a04067c01a80'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

ALTER DATABASE beach_ranks OWNER TO beach_ranks;

\connect beach_ranks

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 18210)
-- Name: beach_ranks; Type: SCHEMA; Schema: -; Owner: beach_ranks
--

CREATE SCHEMA beach_ranks;


ALTER SCHEMA beach_ranks OWNER TO beach_ranks;

--
-- TOC entry 1 (class 3079 OID 12427)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2180 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = beach_ranks, pg_catalog;

--
-- TOC entry 204 (class 1255 OID 18244)
-- Name: save_player(integer, character varying, character varying, character varying); Type: FUNCTION; Schema: beach_ranks; Owner: postgres
--

CREATE FUNCTION save_player(p_player_id integer, p_status character varying, p_nick character varying, p_phone character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    i integer;
BEGIN
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
	select max(player_id) into i from beach_ranks.players;
	if i is Null then
	  i := 0;
	end if;
	insert into beach_ranks.players(player_id, status, nick, phone) values (i + 1, p_status, p_nick, p_phone);
	
	return i + 1;
    end if;
    
    return p_player_id;
exception
    when others then
        RAISE EXCEPTION 'beach_ranks.save_player %: %', SQLERRM, SQLSTATE;
        return -1;
END;
$$;


ALTER FUNCTION beach_ranks.save_player(p_player_id integer, p_status character varying, p_nick character varying, p_phone character varying) OWNER TO postgres;

--
-- TOC entry 205 (class 1255 OID 18246)
-- Name: save_rating(character varying, integer, double precision, double precision); Type: FUNCTION; Schema: beach_ranks; Owner: postgres
--

CREATE FUNCTION save_rating(p_rating_code character varying, p_player_id integer, p_value double precision, p_accuracy double precision) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    i integer;
    v_rating_id integer;
BEGIN
    -- find ratings_def
    select max(coalesce(rat_id, -1)) into v_rating_id from (
      select rating_id as rat_id from beach_ranks.ratings_defs where code = p_rating_code
      union
      select -1 as rat_id
    ) a;

    if v_rating_id < 0 then
    -- insert new type of rating
      select max(coalesce(rat_id, 0))+1 into v_rating_id from (
	      select rating_id as rat_id from beach_ranks.ratings_defs
	      union
	      select 0 as rat_id
	    ) a;
      insert into beach_ranks.ratings_defs(rating_id, code, descr) values (v_rating_id, p_rating_code, '');
    end if;

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
      
      insert into beach_ranks.ratings(rating_id, player_id, value, accuracy) values (v_rating_id, p_player_id, p_value, p_accuracy);
    else
      update beach_ranks.ratings
       set value = p_value, accuracy = p_accuracy
        where rating_id = v_rating_id and player_id = p_player_id;
    end if;
    
    return 1;
exception
    when others then
        RAISE EXCEPTION 'beach_ranks.save_rating %: %', SQLERRM, SQLSTATE;
        return -1;
END;
$$;


ALTER FUNCTION beach_ranks.save_rating(p_rating_code character varying, p_player_id integer, p_value double precision, p_accuracy double precision) OWNER TO postgres;

--
-- TOC entry 191 (class 1255 OID 18245)
-- Name: test(); Type: FUNCTION; Schema: beach_ranks; Owner: postgres
--

CREATE FUNCTION test() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    i integer;
BEGIN
  select 1 into i;
  return i;
END;
$$;


ALTER FUNCTION beach_ranks.test() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 190 (class 1259 OID 18238)
-- Name: game_players; Type: TABLE; Schema: beach_ranks; Owner: beach_ranks
--

CREATE TABLE game_players (
    game_id integer,
    player_id integer,
    win boolean,
    valid boolean
);


ALTER TABLE game_players OWNER TO beach_ranks;

--
-- TOC entry 189 (class 1259 OID 18235)
-- Name: games; Type: TABLE; Schema: beach_ranks; Owner: beach_ranks
--

CREATE TABLE games (
    game_id integer,
    status character varying(10),
    date date,
    score_won integer,
    score_lost integer
);


ALTER TABLE games OWNER TO beach_ranks;

--
-- TOC entry 186 (class 1259 OID 18226)
-- Name: players; Type: TABLE; Schema: beach_ranks; Owner: beach_ranks
--

CREATE TABLE players (
    player_id integer,
    status character varying(10),
    nick character varying(50),
    phone character varying(20)
);


ALTER TABLE players OWNER TO beach_ranks;

--
-- TOC entry 188 (class 1259 OID 18232)
-- Name: ratings; Type: TABLE; Schema: beach_ranks; Owner: beach_ranks
--

CREATE TABLE ratings (
    rating_id integer,
    player_id integer,
    value double precision,
    accuracy double precision
);


ALTER TABLE ratings OWNER TO beach_ranks;

--
-- TOC entry 187 (class 1259 OID 18229)
-- Name: ratings_defs; Type: TABLE; Schema: beach_ranks; Owner: beach_ranks
--

CREATE TABLE ratings_defs (
    rating_id integer,
    code character varying(20),
    descr character varying(100)
);


ALTER TABLE ratings_defs OWNER TO beach_ranks;

-- Completed on 2017-04-23 01:10:16 MSK

--
-- PostgreSQL database dump complete
--

