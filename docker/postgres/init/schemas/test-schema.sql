--
-- PostgreSQL database dump
--

\restrict 2veB8Sr6cPJVtJRUkT6g0pf3xB2Z9Jxee9gXxJGBhS3rqqNL8kea0g6adqsVn2b

-- Dumped from database version 17.12 (Homebrew)
-- Dumped by pg_dump version 17.12 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: security_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.security_logs (
    id bigint NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    ip_address character varying(45) NOT NULL,
    username character varying(100) NOT NULL,
    event_type character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: security_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.security_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: security_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.security_logs_id_seq OWNED BY public.security_logs.id;


--
-- Name: security_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_logs ALTER COLUMN id SET DEFAULT nextval('public.security_logs_id_seq'::regclass);


--
-- Name: security_logs security_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_logs
    ADD CONSTRAINT security_logs_pkey PRIMARY KEY (id);


--
-- Name: security_logs unique_security_log; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_logs
    ADD CONSTRAINT unique_security_log UNIQUE ("timestamp", ip_address, username, event_type, status);


--
-- Name: idx_security_logs_event_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_logs_event_timestamp ON public.security_logs USING btree (event_type, "timestamp");


--
-- PostgreSQL database dump complete
--

\unrestrict 2veB8Sr6cPJVtJRUkT6g0pf3xB2Z9Jxee9gXxJGBhS3rqqNL8kea0g6adqsVn2b
