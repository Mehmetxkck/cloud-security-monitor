--
-- PostgreSQL database dump
--

\restrict F9Rd1D87QcsSFElLH1lv2E5hIAcjLAazuafl0FSFJ5XcCWnKW9f9UefVMsfhaqM

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
    username character varying(255) NOT NULL,
    event_type character varying(100) NOT NULL,
    status character varying(50) NOT NULL
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
-- Name: idx_security_logs_event_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_logs_event_timestamp ON public.security_logs USING btree (event_type, "timestamp");


--
-- PostgreSQL database dump complete
--

\unrestrict F9Rd1D87QcsSFElLH1lv2E5hIAcjLAazuafl0FSFJ5XcCWnKW9f9UefVMsfhaqM

